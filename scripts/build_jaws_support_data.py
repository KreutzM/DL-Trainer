from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from common import make_parser, read_jsonl, write_jsonl


TRANSFORM_PIPELINE_VERSION = "0.3.0"
TEACHER_PROMPT_VERSION = "jaws_de_support_seed_v1"
BEHAVIOR_SPEC_PATH = "docs/support_behavior_spec.md"


@dataclass
class Recipe:
    recipe_id: str
    split: str
    task_type: str
    prompt_template_path: str
    selector: Callable[[dict], bool]
    user_message: str
    assistant_message: str | None
    case_description: str | None = None
    rubric: dict[str, Any] | None = None
    reference_answer: str | None = None
    expected_behavior: str | None = None


def load_chunks(root: Path) -> list[dict]:
    rows: list[dict] = []
    for path in sorted(root.glob("*/chunks.jsonl")):
        rows.extend(read_jsonl(path))
    if not rows:
        raise SystemExit(f"No chunks found under {root}")
    return rows


def first_chunk(chunks: list[dict], predicate: Callable[[dict], bool]) -> dict:
    for chunk in chunks:
        if predicate(chunk):
            return chunk
    raise ValueError("No chunk matched recipe selector")


def build_source_record(chunk: dict) -> dict:
    return {
        "doc_id": chunk["doc_id"],
        "chunk_id": chunk["chunk_id"],
        "section_id": chunk["section_id"],
        "section_title": chunk["section_title"],
        "normalized_path": chunk["normalized_path"],
        "source_spans": chunk["source_spans"],
    }


def build_job(recipe: Recipe, chunk: dict) -> dict:
    return {
        "job_id": recipe.recipe_id,
        "target_split": recipe.split,
        "task_type": recipe.task_type,
        "product": chunk["product"],
        "language": chunk["language"],
        "behavior_spec_path": BEHAVIOR_SPEC_PATH,
        "prompt_template_path": recipe.prompt_template_path,
        "teacher_prompt_version": TEACHER_PROMPT_VERSION,
        "generation_mode": "dry_run_prompt_job_v1",
        "user_message": recipe.user_message,
        "source_doc_ids": [chunk["doc_id"]],
        "source_chunk_ids": [chunk["chunk_id"]],
        "source_excerpt": chunk["content"][:1200],
        "expected_output_kind": "sft_sample" if recipe.split == "sft" else "eval_case",
        "review_status": "draft",
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "source_records": [build_source_record(chunk)],
        },
    }


def build_sft_row(recipe: Recipe, chunk: dict, system_prompt: str, index: int) -> dict:
    provenance = {
        "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
        "behavior_spec_path": BEHAVIOR_SPEC_PATH,
        "prompt_template_path": recipe.prompt_template_path,
        "source_records": [build_source_record(chunk)],
    }
    meta = {
        "product": chunk["product"],
        "language": chunk["language"],
        "task_type": recipe.task_type,
        "teacher_model": "template-seed-no-llm",
        "source_doc_ids": [chunk["doc_id"]],
        "source_chunk_ids": [chunk["chunk_id"]],
        "teacher_prompt_version": TEACHER_PROMPT_VERSION,
        "generation_mode": "template_seed_v1",
        "needs_clarification": recipe.task_type == "clarification",
        "review_status": "draft",
        "split": "seed_train",
        "provenance": provenance,
    }
    return {
        "id": f"jaws_de_seed_sft_{index:04d}",
        "product": chunk["product"],
        "language": chunk["language"],
        "task_type": recipe.task_type,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": recipe.user_message},
            {"role": "assistant", "content": recipe.assistant_message or ""},
        ],
        "source_doc_ids": [chunk["doc_id"]],
        "source_chunk_ids": [chunk["chunk_id"]],
        "teacher_prompt_version": TEACHER_PROMPT_VERSION,
        "generation_mode": "template_seed_v1",
        "review_status": "draft",
        "provenance": provenance,
        "meta": meta,
    }


def build_eval_row(recipe: Recipe, chunk: dict, index: int) -> dict:
    return {
        "eval_id": f"jaws_de_eval_seed_{index:04d}",
        "product": chunk["product"],
        "language": chunk["language"],
        "case_type": recipe.task_type,
        "prompt": recipe.user_message,
        "case_description": recipe.case_description or "",
        "expected_behavior": recipe.expected_behavior or "",
        "source_doc_ids": [chunk["doc_id"]],
        "source_chunk_ids": [chunk["chunk_id"]],
        "review_status": "draft",
        "reference_answer": recipe.reference_answer or "",
        "rubric": recipe.rubric or {
            "must_include": [],
            "must_not_include": ["erfundene Fakten"],
            "style": "präzise, vorsichtig, dokumentationsgestützt",
        },
        "provenance": {
            "transform_pipeline_version": TRANSFORM_PIPELINE_VERSION,
            "behavior_spec_path": BEHAVIOR_SPEC_PATH,
            "prompt_template_path": recipe.prompt_template_path,
            "source_records": [build_source_record(chunk)],
        },
    }


def make_recipes() -> list[Recipe]:
    return [
        Recipe(
            recipe_id="sft_direct_jaws_cursor",
            split="sft",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_tutorial_basics" and c["section_title"] == "Der JAWS Cursor - Folgt dem Mauszeiger",
            user_message="Wofür ist der JAWS Cursor gedacht und wie aktiviere ich ihn?",
            assistant_message="Der JAWS Cursor ist dafür gedacht, Informationen zu lesen, die der PC Cursor nicht erreicht, zum Beispiel Inhalte in einer Werkzeugleiste. Aktivieren Sie ihn mit **NUM GEDANKENSTRICH**.",
        ),
        Recipe(
            recipe_id="sft_direct_image_files",
            split="sft",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Bilddateien erkennen",
            user_message="Welche Dateitypen kann JAWS direkt per Texterkennung lesen?",
            assistant_message="JAWS kann Text in Bilddateien erkennen, die als **BMP, JPG, JPEG, GIF, TIF, TIFF, PNG, PCX oder PDF** gespeichert wurden. Dafür wählen Sie die Datei im Explorer oder auf dem Desktop aus und drücken **EINFÜGEN+LEERTASTE, O, F**.",
        ),
        Recipe(
            recipe_id="sft_steps_teams_zoom",
            split="sft",
            task_type="step_by_step",
            prompt_template_path="prompts/teacher/jaws_de_step_by_step.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Beispiel für geteilte Folien in Teams und Zoom",
            user_message="Wie greife ich in einer Teams- oder Zoom-Besprechung mit JAWS auf geteilte Folien per Hintergrund-OCR zu?",
            assistant_message="1. Treten Sie dem Teams- oder Zoom-Meeting bei, in dem Inhalte geteilt werden.\n2. Drücken Sie **EINFÜGEN+LEERTASTE**, **O**, **EINGABE**.\n3. JAWS startet die Hintergrund-OCR, aktiviert den unsichtbaren Cursor und bewegt ihn zum geteilten Inhaltsbereich.\n4. Lesen Sie den erkannten Text mit den **Pfeiltasten**.\n5. Beenden Sie die Erkennung bei Bedarf mit **EINFÜGEN+LEERTASTE**, **O**, **Q** oder indem Sie den Fokus in ein anderes Fenster verschieben.",
        ),
        Recipe(
            recipe_id="sft_steps_youtube",
            split="sft",
            task_type="step_by_step",
            prompt_template_path="prompts/teacher/jaws_de_step_by_step.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Beispiel für YouTube",
            user_message="Wie nutze ich Hintergrund-OCR, um eingebetteten Text in einem YouTube-Video mit JAWS zu lesen?",
            assistant_message="1. Starten Sie die Wiedergabe des Videos auf YouTube.\n2. Drücken Sie **EINFÜGEN+LEERTASTE**, **O**, **EINGABE**.\n3. JAWS startet die Hintergrund-OCR, aktiviert den unsichtbaren Cursor und bewegt ihn zum Video.\n4. Erkunden Sie den erkannten Text mit den **Pfeiltasten**.\n5. Beenden Sie die Erkennung mit **EINFÜGEN+LEERTASTE**, **O**, **Q** oder durch einen Wechsel des Fokus.",
        ),
        Recipe(
            recipe_id="sft_troubleshoot_graphics_only",
            split="sft",
            task_type="troubleshooting",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Einfache Texterkennung" and c["chunk_index_in_section"] == 2,
            user_message="In einem Anwendungsfenster ist für JAWS nur Grafik. Wie komme ich trotzdem an den Text?",
            assistant_message="Wenn das aktuelle Anwendungsfenster Text als Bild enthält, drücken Sie **EINFÜGEN+LEERTASTE**, **O**, **W**. Damit erkennt JAWS das fokussierte Fenster und stellt den erkannten Text so bereit, dass Sie ihn anschließend lesen können.",
        ),
        Recipe(
            recipe_id="sft_troubleshoot_pdf",
            split="sft",
            task_type="troubleshooting",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Texterkennung eines geöffneten PDF Dokuments",
            user_message="Ein PDF ist im Adobe Reader nicht zugänglich. Was ist in JAWS der richtige Weg?",
            assistant_message="Öffnen Sie das PDF im Adobe Reader und drücken Sie **EINFÜGEN+LEERTASTE, O, D**. JAWS startet dann die Texterkennung für das gesamte Dokument und zeigt den erkannten Inhalt im Ergebnisbetrachter an. Falls das PDF ein Passwort verlangt, müssen Sie dieses zuerst eingeben, bevor die OCR weiterläuft.",
        ),
        Recipe(
            recipe_id="sft_clarify_ocr_mode",
            split="sft",
            task_type="clarification",
            prompt_template_path="prompts/teacher/jaws_de_clarification.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Einfache Texterkennung" and c["chunk_index_in_section"] == 2,
            user_message="Wie starte ich die Texterkennung in JAWS?",
            assistant_message="Möchten Sie eine Bilddatei, ein geöffnetes PDF, das aktuelle Fenster bzw. den Bildschirm oder eine Kamera-/Scanner-Aufnahme erkennen?",
        ),
        Recipe(
            recipe_id="sft_clarify_cursor_choice",
            split="sft",
            task_type="clarification",
            prompt_template_path="prompts/teacher/jaws_de_clarification.md",
            selector=lambda c: c["doc_id"] == "jaws_de_tutorial_basics" and c["section_title"] == "Über die JAWS Cursor",
            user_message="Welchen Cursor soll ich in JAWS verwenden?",
            assistant_message="Möchten Sie im aktuellen Fokus arbeiten, Inhalte außerhalb des PC Cursors lesen oder den Bildschirm erkunden, ohne den Fokus zu verschieben?",
        ),
        Recipe(
            recipe_id="sft_escalate_scanner_support",
            split="sft",
            task_type="uncertainty_escalation",
            prompt_template_path="prompts/teacher/jaws_de_escalation.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Erkennung von Bildern über die PEARL Kamera oder einen Scanner" and c["chunk_index_in_section"] == 3,
            user_message="Unterstützt mein Scanner sicher alle erweiterten OCR-Einstellungen in JAWS?",
            assistant_message="Dazu gibt der vorliegende Abschnitt keine generelle Zusage. Die Dokumentation sagt ausdrücklich, dass die erweiterten Scanner-Einstellungen **nicht von allen Scannern unterstützt** werden. Prüfen Sie deshalb Ihr konkretes Scanner-Modell direkt im Dialog und ziehen Sie bei Bedarf die Dokumentation des Geräts oder den Support hinzu, statt sich auf eine allgemeine Aussage zu verlassen.",
        ),
        Recipe(
            recipe_id="sft_escalate_mouse_mode",
            split="sft",
            task_type="uncertainty_escalation",
            prompt_template_path="prompts/teacher/jaws_de_escalation.md",
            selector=lambda c: c["doc_id"] == "jaws_de_hilfe_kernfunktionen" and c["section_title"] == "Mausmodus (nur für Fusion)",
            user_message="Kann ich den OCR-Mausmodus genauso auch in reinem JAWS verwenden?",
            assistant_message="Im vorliegenden Abschnitt ist der Mausmodus ausdrücklich **nur für Fusion** dokumentiert. Für reines JAWS sehe ich in dieser Quelle keinen belastbaren Beleg, dass derselbe Mausmodus verfügbar ist. Wenn Sie Fusion nutzen, ist dort der OCR-Schalter bzw. **FESTSTELL+STRG+O** beschrieben; für JAWS allein sollten Sie ohne weitere Evidenz nicht davon ausgehen.",
        ),
        Recipe(
            recipe_id="eval_unsichtbarer_cursor",
            split="eval",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_tutorial_basics" and c["section_title"] == "Der unsichtbare Cursor - Erkunden, ohne den Fokus zu bewegen",
            user_message="Was bringt mir der unsichtbare Cursor in JAWS, und wie aktiviere ich ihn?",
            assistant_message=None,
            case_description="Direkte Wissensfrage zu einem Cursor-Konzept.",
            expected_behavior="Erklärt knapp den Zweck des unsichtbaren Cursors, erwähnt das Erkunden ohne Fokusverschiebung und nennt die Aktivierung mit **NUM MINUS** zweimal.",
            reference_answer="Der unsichtbare Cursor erlaubt es, den Bildschirm zu erkunden, ohne die Position des PC Cursors oder Mauszeigers zu verändern. Aktivieren Sie ihn mit **NUM MINUS** zweimal hintereinander.",
            rubric={
                "must_include": ["ohne den Fokus zu verschieben", "NUM MINUS"],
                "must_not_include": ["erfundene zusätzliche Kurztasten"],
                "style": "präzise, vorsichtig, dokumentationsgestützt",
                "scoring_notes": "Nicht nur den Namen nennen, sondern Zweck plus Aktivierung."
            },
        ),
        Recipe(
            recipe_id="eval_web_pdf_auto_read",
            split="eval",
            task_type="uncertainty_escalation",
            prompt_template_path="prompts/teacher/jaws_de_escalation.md",
            selector=lambda c: c["doc_id"] == "jaws_de_settingscenter" and c["section_title"] == "Dokument und Webseiten beim Laden automatische lesen",
            user_message="Wo kann ich in JAWS abschalten, dass Webseiten und PDF-Dokumente beim Laden sofort vorgelesen werden?",
            assistant_message=None,
            case_description="Einstellungsfrage mit dokumentiertem Standardverhalten und Hinweis.",
            expected_behavior="Beschreibt das Kontrollfeld zum automatischen Lesen beim Laden und erwähnt, dass die Einstellung deaktiviert werden kann.",
            reference_answer="Gehen Sie in die entsprechende Einstellung **Dokument und Webseiten beim Laden automatische lesen** und deaktivieren Sie das Kontrollfeld, wenn JAWS den Lesevorgang nicht automatisch starten soll.",
            rubric={
                "must_include": ["Kontrollfeld", "automatisch", "deaktivieren"],
                "must_not_include": ["nicht belegte Menüpfade"],
                "style": "präzise, vorsichtig, dokumentationsgestützt",
                "scoring_notes": "Outlook-Hinweis ist optional, aber keine falschen Navigationsebenen erfinden."
            },
        ),
        Recipe(
            recipe_id="eval_braille_structure",
            split="eval",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_braille" and c["section_title"] == "Ein Beispiel für eine strukturierte Zeile",
            user_message="Warum sieht eine strukturierte Braillezeile anders aus als das, was JAWS spricht?",
            assistant_message=None,
            case_description="Erklärfall zu Braille- und Sprachausgabe-Darstellung.",
            expected_behavior="Erklärt, dass Windows eine grafische Umgebung ist und die Informationen auf der Braillezeile deshalb nicht der gesprochenen Reihenfolge entsprechen müssen.",
            reference_answer="Die strukturierte Braillezeile kann anders aussehen als die Sprachausgabe, weil Windows eine grafische, dreidimensionale Umgebung ist. Deshalb richtet sich die Reihenfolge der Informationen auf der Braillezeile nicht zwingend nach der gesprochenen Reihenfolge von JAWS.",
            rubric={
                "must_include": ["grafische Umgebung", "Reihenfolge"],
                "must_not_include": ["frei erfundene Braille-Regeln"],
                "style": "präzise, vorsichtig, dokumentationsgestützt",
                "scoring_notes": "Der Kern ist die unterschiedliche Struktur von Braillezeile und Sprachausgabe."
            },
        ),
        Recipe(
            recipe_id="eval_skip_blank_lines",
            split="eval",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_settingscenter" and c["section_title"] == "Leerzeilen beim Navigieren überspringen",
            user_message="Kann JAWS beim Navigieren in Webseiten oder PDFs leere Zeilen überspringen?",
            assistant_message=None,
            case_description="Einstellungsfrage zu virtuellem Cursor.",
            expected_behavior="Bestätigt die Option, erklärt kurz die Wirkung und erwähnt, dass das Kontrollfeld standardmäßig aktiviert ist.",
            reference_answer="Ja. Wenn **Leerzeilen beim Navigieren überspringen** aktiviert ist, überspringen JAWS und Fusion leere Zeilen beim Navigieren mit dem virtuellen Cursor. Das Kontrollfeld ist standardmäßig aktiviert.",
            rubric={
                "must_include": ["virtuellen Cursor", "standardmäßig aktiviert"],
                "must_not_include": ["erfundene Nebenwirkungen"],
                "style": "präzise, vorsichtig, dokumentationsgestützt",
                "scoring_notes": "Soll die konkrete Funktion, nicht nur ein allgemeines Ja, nennen."
            },
        ),
        Recipe(
            recipe_id="eval_virtual_pc_cursor_highlight",
            split="eval",
            task_type="faq_direct_answer",
            prompt_template_path="prompts/teacher/jaws_de_direct_support.md",
            selector=lambda c: c["doc_id"] == "jaws_de_settingscenter" and c["section_title"] == "Virtuellen PC Cursor hervorheben",
            user_message="Kann JAWS beim Lesen in Webseiten oder PDF-Dokumenten den aktuell gesprochenen Text visuell hervorheben?",
            assistant_message=None,
            case_description="Einstellungsfall zur visuellen Verfolgung im virtuellen PC Cursor.",
            expected_behavior="Bestätigt die Möglichkeit, nennt den virtuellen PC Cursor und erwähnt, dass die Hervorhebung in unterstützten Programmen standardmäßig aktiv ist.",
            reference_answer="Ja. Mit der Einstellung **Virtuellen PC Cursor hervorheben** kann JAWS den aktuell gewählten Text beim Lesen im virtuellen PC Cursor hervorheben. Die Einstellung ist in Programmen wie Edge, Chrome, Firefox, Adobe Reader und Microsoft Mail standardmäßig aktiviert.",
            rubric={
                "must_include": ["virtuellen PC Cursor", "hervorheben"],
                "must_not_include": ["erfundene Programme oder Optionen"],
                "style": "präzise, vorsichtig, dokumentationsgestützt",
                "scoring_notes": "Mindestens Funktion und Kontext Web/PDF nennen."
            },
        ),
    ]


def parse_args() -> Any:
    parser = make_parser("Build a small JAWS-DE support seed pipeline from chunk artifacts.")
    parser.add_argument("--chunks-root", default="data/derived/chunks/JAWS/DE")
    parser.add_argument("--jobs-output", default="data/derived/teacher_outputs/JAWS/DE/seed_generation_jobs.jsonl")
    parser.add_argument("--sft-output", default="data/derived/teacher_outputs/JAWS/DE/seed_sft_candidates.jsonl")
    parser.add_argument("--eval-output", default="data/derived/teacher_outputs/JAWS/DE/seed_eval_cases.jsonl")
    parser.add_argument("--mode", choices=["seed", "dry-run"], default="seed")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    chunks = load_chunks(Path(args.chunks_root))
    recipes = make_recipes()
    system_prompt = Path(BEHAVIOR_SPEC_PATH).read_text(encoding="utf-8").strip()

    jobs: list[dict] = []
    sft_rows: list[dict] = []
    eval_rows: list[dict] = []
    sft_index = 0
    eval_index = 0

    for recipe in recipes:
        chunk = first_chunk(chunks, recipe.selector)
        jobs.append(build_job(recipe, chunk))
        if args.mode == "dry-run":
            continue
        if recipe.split == "sft":
            sft_index += 1
            sft_rows.append(build_sft_row(recipe, chunk, system_prompt, sft_index))
        else:
            eval_index += 1
            eval_rows.append(build_eval_row(recipe, chunk, eval_index))

    write_jsonl(Path(args.jobs_output), jobs)
    print(f"Wrote {len(jobs)} generation jobs -> {args.jobs_output}")
    if args.mode == "seed":
        write_jsonl(Path(args.sft_output), sft_rows)
        write_jsonl(Path(args.eval_output), eval_rows)
        print(f"Wrote {len(sft_rows)} SFT seed rows -> {args.sft_output}")
        print(f"Wrote {len(eval_rows)} eval seed rows -> {args.eval_output}")


if __name__ == "__main__":
    main()
