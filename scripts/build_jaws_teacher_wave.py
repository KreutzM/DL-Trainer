from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from common import make_parser, read_jsonl, write_json, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.7.0"
TEACHER_PROMPT_VERSION = "jaws_de_support_wave_v1"
BEHAVIOR_SPEC_PATH = "docs/support_behavior_spec.md"
REVIEW_STATUS_SEED = "seed"
DEFAULT_WAVE_ID = "jaws_de_teacher_wave_v1"

DEFAULT_TRAIN_TARGETS = {
    "clarification": 36,
    "uncertainty_escalation": 36,
    "step_by_step": 64,
    "troubleshooting": 72,
    "faq_direct_answer": 132,
}
DEFAULT_EVAL_TARGETS = {
    "clarification": 8,
    "uncertainty_escalation": 10,
    "step_by_step": 10,
    "troubleshooting": 10,
    "faq_direct_answer": 22,
}
TASK_ORDER = [
    "clarification",
    "step_by_step",
    "uncertainty_escalation",
    "troubleshooting",
    "faq_direct_answer",
]
TASK_CONFIG = {
    "faq_direct_answer": {"prompt_template_path": "prompts/teacher/jaws_de_direct_support.md"},
    "troubleshooting": {"prompt_template_path": "prompts/teacher/jaws_de_direct_support.md"},
    "step_by_step": {"prompt_template_path": "prompts/teacher/jaws_de_step_by_step.md"},
    "clarification": {"prompt_template_path": "prompts/teacher/jaws_de_clarification.md"},
    "uncertainty_escalation": {"prompt_template_path": "prompts/teacher/jaws_de_escalation.md"},
}

LIMITATION_RE = re.compile(
    r"(?i)\b(nicht|nur|falls|wenn|unterstuetzt|unterstützt|abh[aä]ngig|m[öo]glicherweise|kann nicht|ohne|optional)\b"
)
ACTION_RE = re.compile(
    r"(?i)\b(druecken|drücken|waehlen|wählen|oeffnen|öffnen|aktivieren|deaktivieren|pruefen|prüfen|stellen sie sicher|wechseln|konfigurieren|verwenden|geben sie|schalten sie|bewegen sie|gehen sie|markieren|speichern)\b"
)
SHORTCUT_RE = re.compile(r"\*\*([^*]+)\*\*")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class DraftCase:
    task_type: str
    user_message: str
    assistant_message: str
    case_description: str
    expected_behavior: str
    rubric: dict[str, Any]
    prompt_template_path: str
    score: int
    selection_reason: str


def stable_hash(value: str) -> int:
    return int(hashlib.sha256(value.encode("utf-8")).hexdigest()[:16], 16)


def load_chunks(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.glob("*/chunks.jsonl")):
        rows.extend(read_jsonl(path))
    if not rows:
        raise SystemExit(f"No chunks found under {root}")
    return rows


def strip_markdown(text: str) -> str:
    text = MARKDOWN_LINK_RE.sub(r"\1", text)
    text = text.replace("**", "")
    text = text.replace("`", "")
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_line(text: str) -> str:
    text = strip_markdown(text)
    text = re.sub(r"^\d+\.\s*", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip("- ").strip()


def extract_bullets(content: str) -> list[str]:
    bullets = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(clean_line(stripped[2:]))
    return bullets


def extract_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text.replace("\n", " "))
    parts = re.split(r"(?<=[.!?])\s+", normalized)
    cleaned: list[str] = []
    for part in parts:
        sentence = clean_line(part)
        if not sentence or sentence in {"1.", "2.", "3.", "4.", "5."}:
            continue
        cleaned.append(sentence)
    return cleaned


def extract_numbered_steps(text: str) -> list[str]:
    matches = re.findall(r"(?:^|\n)\s*\d+\.\s*(.+?)(?=(?:\n\s*\d+\.\s)|$)", text, flags=re.DOTALL)
    steps = []
    for match in matches:
        cleaned = clean_line(match.replace("\n", " "))
        if cleaned:
            steps.append(cleaned)
    return steps


def first_distinct_sentences(chunk: dict, limit: int = 3) -> list[str]:
    summary = clean_line(chunk.get("summary", ""))
    sentences: list[str] = []
    seen: set[str] = set()
    content_sentences = extract_sentences(chunk["content"])
    if summary and "..." not in summary and "…" not in summary:
        first_content = content_sentences[0].lower() if content_sentences else ""
        if first_content and (first_content.startswith(summary.lower()) or summary.lower()[:48] in first_content):
            summary = ""
    if summary:
        seen.add(summary.lower())
        sentences.append(summary)
    for sentence in content_sentences:
        lowered = sentence.lower()
        if lowered in seen:
            continue
        if sentence.endswith(":"):
            continue
        seen.add(lowered)
        sentences.append(sentence)
        if len(sentences) >= limit:
            break
    return sentences


def extract_shortcuts(text: str) -> list[str]:
    seen: set[str] = set()
    results: list[str] = []
    for match in SHORTCUT_RE.findall(text):
        shortcut = " ".join(match.split())
        lowered = shortcut.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        results.append(shortcut)
    return results


def join_snippets(snippets: list[str], max_chars: int = 340) -> str:
    result = ""
    for snippet in snippets:
        if result:
            result_words = result.lower().replace("…", "").split()
            snippet_words = snippet.lower().replace("…", "").split()
            if result_words[:8] == snippet_words[:8]:
                continue
        candidate = snippet if not result else f"{result} {snippet}"
        if len(candidate) > max_chars:
            break
        result = candidate
    return result or (snippets[0] if snippets else "")


def limitation_sentence(sentences: list[str]) -> str | None:
    for sentence in sentences:
        if LIMITATION_RE.search(sentence):
            return sentence
    return None


def actionable_sentences(sentences: list[str]) -> list[str]:
    return [sentence for sentence in sentences if ACTION_RE.search(sentence)]


def option_labels(chunk: dict, bullets: list[str], shortcuts: list[str]) -> list[str]:
    labels: list[str] = []
    for bullet in bullets:
        label = bullet
        if " - " in label:
            _, label = label.split(" - ", 1)
        label = label.split(",")[0].split(";")[0].strip()
        if 3 <= len(label) <= 80 and not ACTION_RE.search(label):
            labels.append(label)
    if len(labels) >= 3:
        return labels[:4]

    lower_title = chunk["section_title"].lower()
    if "texterkennung" in lower_title:
        return ["Bilddatei", "geoeffnetes PDF", "aktuelles Fenster oder Bildschirm", "Kamera oder Scanner"]
    if "cursor" in lower_title:
        return ["PC Cursor", "JAWS Cursor", "unsichtbaren Cursor"]
    if shortcuts:
        return shortcuts[:3]
    return []


def title_phrase(chunk: dict) -> str:
    return strip_markdown(chunk["section_title"])


def build_faq_case(chunk: dict) -> DraftCase | None:
    sentences = first_distinct_sentences(chunk, limit=3)
    if not sentences:
        return None
    shortcuts = extract_shortcuts(chunk["content"])
    question_templates = [
        f"Wofuer ist {title_phrase(chunk)} in JAWS gedacht?",
        f"Wie beschreibt die JAWS-Dokumentation {title_phrase(chunk)}?",
        f"Was sollte ich in JAWS zu {title_phrase(chunk)} wissen?",
    ]
    question = question_templates[stable_hash(chunk["chunk_id"] + "::faq") % len(question_templates)]
    answer = join_snippets(sentences[:2], max_chars=360)
    if not answer or answer.endswith(":"):
        return None
    if shortcuts and shortcuts[0] not in answer and chunk.get("chunk_type") in {"concept", "reference"}:
        answer = f"{answer} Wichtige Tastenkombination: **{shortcuts[0]}**."
    must_include = [chunk["section_title"]]
    if shortcuts and chunk.get("chunk_type") in {"concept", "reference"}:
        must_include.append(shortcuts[0])
    score = 46
    if chunk["char_count"] <= 1500:
        score += 8
    if chunk.get("chunk_type") in {"concept", "reference"}:
        score += 12
    elif chunk.get("chunk_type") == "warning":
        score += 4
    if shortcuts and chunk.get("chunk_type") in {"concept", "reference"}:
        score += 6
    return DraftCase(
        task_type="faq_direct_answer",
        user_message=question,
        assistant_message=answer,
        case_description=f"Direkte Supportfrage zu {title_phrase(chunk)}.",
        expected_behavior=f"Beantwortet die Frage knapp und dokumentationsgestuetzt zu {title_phrase(chunk)}.",
        rubric={
            "must_include": must_include[:3],
            "must_not_include": ["erfundene Produktdetails"],
            "style": "praezise, vorsichtig, dokumentationsgestuetzt",
        },
        prompt_template_path=TASK_CONFIG["faq_direct_answer"]["prompt_template_path"],
        score=score,
        selection_reason=f"faq:{chunk.get('chunk_type')}:{'shortcut' if shortcuts else 'no_shortcut'}",
    )


def build_troubleshooting_case(chunk: dict) -> DraftCase | None:
    sentences = extract_sentences(chunk["content"])[:6]
    if not sentences:
        return None
    shortcuts = extract_shortcuts(chunk["content"])
    limited = limitation_sentence(sentences)
    action_items = actionable_sentences(sentences)
    if chunk.get("chunk_type") not in {"warning", "procedure"} and not limited:
        return None
    if not action_items and chunk.get("chunk_type") == "concept":
        return None
    chosen: list[str] = []
    if limited:
        chosen.append(limited)
    for sentence in action_items:
        if sentence.lower() not in {item.lower() for item in chosen}:
            chosen.append(sentence)
        if len(chosen) >= 2:
            break
    if not chosen:
        chosen.append(sentences[0])
    answer = "Die Dokumentation empfiehlt fuer diesen Fall: " + " ".join(chosen)
    if shortcuts and shortcuts[0] not in answer and action_items:
        answer = f"{answer} Verwenden Sie dazu **{shortcuts[0]}**."
    question = f"Ich komme bei {title_phrase(chunk)} in JAWS nicht weiter. Was sollte ich laut Dokumentation pruefen oder tun?"
    score = 42
    if chunk.get("chunk_type") in {"warning", "procedure"}:
        score += 16
    if limited:
        score += 10
    if action_items:
        score += 8
    if shortcuts and action_items:
        score += 4
    return DraftCase(
        task_type="troubleshooting",
        user_message=question,
        assistant_message=answer,
        case_description=f"Troubleshooting-Fall zu {title_phrase(chunk)}.",
        expected_behavior=f"Leitet aus dem Abschnitt {title_phrase(chunk)} eine konkrete dokumentierte Hilfestellung ab.",
        rubric={
            "must_include": ([shortcuts[0]] if shortcuts and action_items else [])[:1],
            "must_not_include": ["erfundene Menuepfade", "nicht belegte Workarounds"],
            "style": "praezise, vorsichtig, dokumentationsgestuetzt",
        },
        prompt_template_path=TASK_CONFIG["troubleshooting"]["prompt_template_path"],
        score=score,
        selection_reason=f"troubleshooting:{chunk.get('chunk_type')}:{'limitation' if limited else 'actionable'}",
    )


def build_step_case(chunk: dict) -> DraftCase | None:
    numbered_steps = extract_numbered_steps(chunk["content"])
    bullets = extract_bullets(chunk["content"])
    sentences = extract_sentences(chunk["content"])
    steps: list[str] = []
    if numbered_steps:
        steps.extend(numbered_steps[:5])
    elif bullets:
        for bullet in bullets[:5]:
            steps.append(bullet[0].upper() + bullet[1:] if bullet else bullet)
    else:
        steps.extend(sentences[:5])
    if len(steps) < 3:
        return None
    rendered_steps = [f"{index}. {step}" for index, step in enumerate(steps[:5], start=1)]
    answer = "\n".join(rendered_steps)
    question = f"Wie gehe ich bei {title_phrase(chunk)} in JAWS Schritt fuer Schritt vor?"
    score = 44
    if chunk.get("chunk_type") == "procedure":
        score += 20
    if chunk.get("contains_steps"):
        score += 12
    if extract_shortcuts(chunk["content"]):
        score += 6
    return DraftCase(
        task_type="step_by_step",
        user_message=question,
        assistant_message=answer,
        case_description=f"Schrittfolge fuer {title_phrase(chunk)}.",
        expected_behavior=f"Gibt eine kurze Schrittfolge fuer {title_phrase(chunk)} aus dem Abschnitt wieder.",
        rubric={
            "must_include": [title_phrase(chunk)],
            "must_not_include": ["erfundene Zwischenschritte"],
            "style": "praezise, vorsichtig, dokumentationsgestuetzt",
        },
        prompt_template_path=TASK_CONFIG["step_by_step"]["prompt_template_path"],
        score=score,
        selection_reason=f"step:{chunk.get('chunk_type')}:{'numbered' if numbered_steps else ('bullets' if bullets else 'sentences')}",
    )


def build_clarification_case(chunk: dict) -> DraftCase | None:
    bullets = extract_bullets(chunk["content"])
    shortcuts = extract_shortcuts(chunk["content"])
    options = option_labels(chunk, bullets, shortcuts)
    if len(options) < 3:
        return None
    joined = ", ".join(options[:-1]) + f" oder {options[-1]}"
    lower_title = chunk["section_title"].lower()
    if "texterkennung" in lower_title:
        user_message = "Wie nutze ich die Texterkennung in JAWS?"
    elif "cursor" in lower_title:
        user_message = "Welchen Cursor sollte ich in JAWS verwenden?"
    else:
        user_message = f"Ich brauche Hilfe zu {title_phrase(chunk)} in JAWS."
    assistant_message = f"Geht es Ihnen um {joined}?"
    score = 36
    if chunk.get("contains_list"):
        score += 18
    if len(options) >= 4:
        score += 8
    return DraftCase(
        task_type="clarification",
        user_message=user_message,
        assistant_message=assistant_message,
        case_description=f"Rueckfragefall fuer das breitere Thema {title_phrase(chunk)}.",
        expected_behavior=f"Stellt genau eine fokussierte Rueckfrage und grenzt {title_phrase(chunk)} sinnvoll ein.",
        rubric={
            "must_include": [options[0], options[1]],
            "must_not_include": ["mehrere Folgefragen", "Antwort ohne Rueckfrage"],
            "style": "genau eine fokussierte Rueckfrage auf Deutsch",
        },
        prompt_template_path=TASK_CONFIG["clarification"]["prompt_template_path"],
        score=score,
        selection_reason=f"clarification:options_{len(options)}",
    )


def build_uncertainty_case(chunk: dict) -> DraftCase | None:
    sentences = first_distinct_sentences(chunk, limit=4)
    if not sentences:
        return None
    limited = limitation_sentence(sentences)
    if not limited and chunk.get("chunk_type") != "warning":
        return None
    limited = limited or sentences[0]
    answer = (
        "Dafuer gibt der vorliegende Abschnitt keine allgemeine Zusage. "
        f"{limited} "
        "Pruefen Sie deshalb den konkreten Kontext in JAWS oder in der zugehoerigen Dokumentation, statt eine allgemeine Unterstuetzung anzunehmen."
    )
    question = f"Kann ich mich bei {title_phrase(chunk)} in JAWS allgemein darauf verlassen, dass das immer gleich unterstuetzt wird?"
    score = 42
    if chunk.get("chunk_type") == "warning":
        score += 18
    if limitation_sentence(sentences):
        score += 14
    return DraftCase(
        task_type="uncertainty_escalation",
        user_message=question,
        assistant_message=answer,
        case_description=f"Unsicherheits- oder Eskalationsfall zu {title_phrase(chunk)}.",
        expected_behavior=f"Markiert die Evidenzgrenze fuer {title_phrase(chunk)} klar und erfindet keine generelle Zusage.",
        rubric={
            "must_include": ["keine allgemeine Zusage", "konkreten Kontext"],
            "must_not_include": ["pauschale Zusicherung", "erfundene Kompatibilitaet"],
            "style": "praezise, vorsichtig, dokumentationsgestuetzt",
        },
        prompt_template_path=TASK_CONFIG["uncertainty_escalation"]["prompt_template_path"],
        score=score,
        selection_reason=f"uncertainty:{chunk.get('chunk_type')}:{'limitation' if limitation_sentence(sentences) else 'warning_only'}",
    )


def generate_drafts_for_chunk(chunk: dict) -> list[DraftCase]:
    drafts: list[DraftCase] = []
    faq = build_faq_case(chunk)
    if faq:
        drafts.append(faq)

    lower_content = chunk["content"].lower()
    if chunk.get("chunk_type") == "procedure" or chunk.get("contains_steps"):
        step = build_step_case(chunk)
        if step:
            drafts.append(step)

    if chunk.get("chunk_type") in {"warning", "procedure"} or LIMITATION_RE.search(lower_content):
        troubleshooting = build_troubleshooting_case(chunk)
        if troubleshooting:
            drafts.append(troubleshooting)

    if chunk.get("contains_list") or "texterkennung" in chunk["section_title"].lower() or "cursor" in chunk["section_title"].lower():
        clarification = build_clarification_case(chunk)
        if clarification:
            drafts.append(clarification)

    if chunk.get("chunk_type") == "warning" or LIMITATION_RE.search(chunk["content"]):
        uncertainty = build_uncertainty_case(chunk)
        if uncertainty:
            drafts.append(uncertainty)
    return drafts


def build_source_record(chunk: dict) -> dict:
    return {
        "doc_id": chunk["doc_id"],
        "chunk_id": chunk["chunk_id"],
        "section_id": chunk["section_id"],
        "section_title": chunk["section_title"],
        "normalized_path": chunk["normalized_path"],
        "source_spans": chunk["source_spans"],
    }


def build_job(split: str, index: int, chunk: dict, draft: DraftCase, system_prompt: str, wave_id: str) -> dict:
    expected_output_kind = "sft_sample" if split == "train" else "eval_case"
    if split == "train":
        fixture_payload: dict[str, Any] = {"assistant_message": draft.assistant_message}
    else:
        fixture_payload = {
            "case_description": draft.case_description,
            "expected_behavior": draft.expected_behavior,
            "reference_answer": draft.assistant_message,
            "rubric": draft.rubric,
        }
    return {
        "job_id": f"{wave_id}::{split}::{draft.task_type}::{index:04d}",
        "wave_id": wave_id,
        "job_status": REVIEW_STATUS_SEED,
        "review_status": REVIEW_STATUS_SEED,
        "target_split": split,
        "expected_output_kind": expected_output_kind,
        "task_type": draft.task_type,
        "product": chunk["product"],
        "language": chunk["language"],
        "behavior_spec_path": BEHAVIOR_SPEC_PATH,
        "prompt_template_path": draft.prompt_template_path,
        "teacher_prompt_version": TEACHER_PROMPT_VERSION,
        "generation_mode": "teacher_wave_fixture_v2",
        "source_doc_ids": [chunk["doc_id"]],
        "source_chunk_ids": [chunk["chunk_id"]],
        "source_excerpt": chunk["content"][:1400],
        "runner_input": {
            "system_message": system_prompt,
            "user_message": draft.user_message,
        },
        "fixture_payload": fixture_payload,
        "quality_score": draft.score,
        "selection_reason": draft.selection_reason,
        "chunk_type": chunk.get("chunk_type"),
        "section_path_text": chunk.get("section_path_text"),
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_records": [build_source_record(chunk)],
        },
    }


def draft_sort_key(chunk: dict, draft: DraftCase) -> tuple[int, int]:
    return (-draft.score, stable_hash(f"{chunk['chunk_id']}::{draft.task_type}"))


def load_chunk_exclusions(paths: list[str], directories: list[str]) -> set[str]:
    chunk_ids: set[str] = set()
    for path_str in paths:
        for row in read_jsonl(Path(path_str)):
            chunk_ids.update(row.get("source_chunk_ids", []))
    for directory_str in directories:
        directory = Path(directory_str)
        for path in sorted(directory.glob("*.jsonl")):
            for row in read_jsonl(path):
                chunk_ids.update(row.get("source_chunk_ids", []))
    return chunk_ids


def parse_target_args(values: list[str], defaults: dict[str, int]) -> dict[str, int]:
    targets = dict(defaults)
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Invalid target override '{value}', expected task=count")
        task_type, count_text = value.split("=", 1)
        if task_type not in TASK_CONFIG:
            raise SystemExit(f"Unknown task type in override: {task_type}")
        try:
            count = int(count_text)
        except ValueError as exc:
            raise SystemExit(f"Invalid count in override '{value}'") from exc
        if count < 0:
            raise SystemExit(f"Target count must be non-negative: {value}")
        targets[task_type] = count
    return targets


def round_robin_select(
    candidates_by_doc: dict[str, list[tuple[dict, DraftCase]]],
    target_count: int,
    used_chunks: set[str],
) -> list[tuple[dict, DraftCase]]:
    ordered_docs = sorted(candidates_by_doc, key=lambda doc_id: (stable_hash(doc_id) % 1000, doc_id))
    selected: list[tuple[dict, DraftCase]] = []
    while len(selected) < target_count:
        progressed = False
        for doc_id in ordered_docs:
            pool = candidates_by_doc[doc_id]
            while pool and pool[0][0]["chunk_id"] in used_chunks:
                pool.pop(0)
            if not pool:
                continue
            chunk, draft = pool.pop(0)
            used_chunks.add(chunk["chunk_id"])
            selected.append((chunk, draft))
            progressed = True
            if len(selected) >= target_count:
                break
        if not progressed:
            break
    return selected


def build_selection(
    chunks: list[dict],
    *,
    train_targets: dict[str, int],
    eval_targets: dict[str, int],
    excluded_chunk_ids: set[str],
    eval_modulo: int,
    eval_remainder: int,
    wave_id: str,
) -> tuple[list[tuple[str, dict, DraftCase]], dict[str, Any]]:
    by_task_train: dict[str, dict[str, list[tuple[dict, DraftCase]]]] = defaultdict(lambda: defaultdict(list))
    by_task_eval: dict[str, dict[str, list[tuple[dict, DraftCase]]]] = defaultdict(lambda: defaultdict(list))
    available_by_split_task: dict[str, Counter[str]] = {"train": Counter(), "eval": Counter()}
    available_by_split_doc: dict[str, Counter[str]] = {"train": Counter(), "eval": Counter()}

    for chunk in chunks:
        if chunk["chunk_id"] in excluded_chunk_ids:
            continue
        bucket = "eval" if stable_hash(chunk["chunk_id"]) % eval_modulo == eval_remainder else "train"
        drafts = generate_drafts_for_chunk(chunk)
        for draft in drafts:
            candidate = (chunk, draft)
            if bucket == "eval":
                by_task_eval[draft.task_type][chunk["doc_id"]].append(candidate)
            else:
                by_task_train[draft.task_type][chunk["doc_id"]].append(candidate)
            available_by_split_task[bucket][draft.task_type] += 1
            available_by_split_doc[bucket][chunk["doc_id"]] += 1

    for task_map in [by_task_train, by_task_eval]:
        for doc_map in task_map.values():
            for doc_id, items in doc_map.items():
                items.sort(key=lambda item: draft_sort_key(item[0], item[1]))
                doc_map[doc_id] = items

    selections: list[tuple[str, dict, DraftCase]] = []
    shortages: dict[str, dict[str, int]] = {"train": {}, "eval": {}}
    used_eval_chunks: set[str] = set()
    used_all_chunks: set[str] = set(excluded_chunk_ids)

    for task_type in TASK_ORDER:
        eval_selected = round_robin_select(by_task_eval[task_type], eval_targets[task_type], used_eval_chunks)
        selections.extend(("eval", chunk, draft) for chunk, draft in eval_selected)
        used_all_chunks.update(chunk["chunk_id"] for chunk, _ in eval_selected)
        shortages["eval"][task_type] = max(0, eval_targets[task_type] - len(eval_selected))

    for task_type in TASK_ORDER:
        train_selected = round_robin_select(by_task_train[task_type], train_targets[task_type], used_all_chunks)
        selections.extend(("train", chunk, draft) for chunk, draft in train_selected)
        used_all_chunks.update(chunk["chunk_id"] for chunk, _ in train_selected)
        shortages["train"][task_type] = max(0, train_targets[task_type] - len(train_selected))

    report = {
        "wave_id": wave_id,
        "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
        "train_targets": train_targets,
        "eval_targets": eval_targets,
        "excluded_chunk_ids": len(excluded_chunk_ids),
        "eval_split_rule": {"modulo": eval_modulo, "remainder": eval_remainder},
        "available_by_split_task": {
            split: {task: available_by_split_task[split].get(task, 0) for task in TASK_ORDER}
            for split in ["train", "eval"]
        },
        "available_by_split_doc": {split: dict(available_by_split_doc[split]) for split in ["train", "eval"]},
        "shortages": shortages,
        "selected_jobs": len(selections),
        "selected_by_split": dict(Counter(split for split, _, _ in selections)),
        "selected_by_task_type": dict(Counter(draft.task_type for _, _, draft in selections)),
        "selected_by_doc": dict(Counter(chunk["doc_id"] for _, chunk, _ in selections)),
    }
    return selections, report


def parse_args() -> Any:
    parser = make_parser("Build a deterministic JAWS-DE teacher wave from chunk data.")
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--jobs-output", default="data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl")
    parser.add_argument("--report-output", default="data/derived/teacher_jobs/JAWS/DE/wave1_generation_report.json")
    parser.add_argument("--wave-id", default=DEFAULT_WAVE_ID)
    parser.add_argument("--train-target", action="append", default=[])
    parser.add_argument("--eval-target", action="append", default=[])
    parser.add_argument("--exclude-jsonl", action="append", default=[])
    parser.add_argument("--exclude-dir", action="append", default=[])
    parser.add_argument("--eval-modulo", type=int, default=7)
    parser.add_argument("--eval-remainder", type=int, default=0)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.eval_modulo <= 1:
        raise SystemExit("--eval-modulo must be > 1")
    if not 0 <= args.eval_remainder < args.eval_modulo:
        raise SystemExit("--eval-remainder must be between 0 and eval-modulo-1")

    chunks = load_chunks(Path(args.chunks_root))
    system_prompt = Path(BEHAVIOR_SPEC_PATH).read_text(encoding="utf-8").strip()
    train_targets = parse_target_args(args.train_target, DEFAULT_TRAIN_TARGETS)
    eval_targets = parse_target_args(args.eval_target, DEFAULT_EVAL_TARGETS)
    excluded_chunk_ids = load_chunk_exclusions(args.exclude_jsonl, args.exclude_dir)

    selections, report = build_selection(
        chunks,
        train_targets=train_targets,
        eval_targets=eval_targets,
        excluded_chunk_ids=excluded_chunk_ids,
        eval_modulo=args.eval_modulo,
        eval_remainder=args.eval_remainder,
        wave_id=args.wave_id,
    )
    jobs: list[dict] = []
    counters: Counter[tuple[str, str]] = Counter()
    for split, chunk, draft in selections:
        counters[(split, draft.task_type)] += 1
        jobs.append(build_job(split, counters[(split, draft.task_type)], chunk, draft, system_prompt, args.wave_id))

    write_jsonl(Path(args.jobs_output), jobs)
    write_json(Path(args.report_output), report)
    print(f"Wrote {len(jobs)} teacher wave jobs -> {args.jobs_output}")
    print(f"Wrote job selection report -> {args.report_output}")


if __name__ == "__main__":
    main()
