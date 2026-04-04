from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v9_complete_long_dialog_step_collection"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_complete_long_dialog_step_collection"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v9_complete_long_dialog_step_collection_job_ids.txt"
)
OUTPUT_SELECTION = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v9_complete_long_dialog_step_collection_selection.json"
)


FULL_LONG_JOB_IDS = [
    "jaws_de_teacher_wave_v1::train::step_by_step::0012",
    "jaws_de_teacher_wave_v1::train::step_by_step::0016",
    "jaws_de_teacher_wave_v1::train::step_by_step::0024",
    "jaws_de_teacher_wave_v1::train::step_by_step::0030",
    "jaws_de_teacher_wave_v1::train::step_by_step::0041",
    "jaws_de_teacher_wave_v1::train::step_by_step::0052",
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
]

CHUNK_BOUNDARY_JOB_IDS = [
    "jaws_de_teacher_wave_v1::train::step_by_step::0027",
    "jaws_de_teacher_wave_v1::train::step_by_step::0034",
    "jaws_de_teacher_wave_v1::train::step_by_step::0043",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
    "jaws_de_teacher_wave_v1::eval::troubleshooting::0005",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0012": (
        "Long settings-center flow with a complete numbered procedure and no obvious branch spill."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0016": (
        "Long notification-rule setup that should finish cleanly if source coverage is sufficient."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0024": (
        "Long font-name flow with a complete end state and no special chunk ambiguity."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0030": (
        "Known-green long multi-tab settings flow kept as a stable anchor."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0041": (
        "Known-green long settings-center configuration kept as a stable anchor."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0052": (
        "Known-green long rule-management path kept as a stable anchor."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "Known-green completion half of the import assistant kept as a stable anchor."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0027": (
        "Short continuation chunk for the Einrückung flow, useful as a chunk-boundary sibling."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0034": (
        "Later chunk in the notification-rule flow, useful for boundary versus completion comparison."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0043": (
        "Continuation chunk for the Schriftname flow, useful for boundary versus completion comparison."
    ),
    "jaws_de_teacher_wave_v1::eval::clarification::0007": "Stable clarification control.",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010": "Stable faq_direct_answer control.",
    "jaws_de_teacher_wave_v1::eval::troubleshooting::0005": "Stable troubleshooting control.",
}


def main() -> None:
    repo_root = Path.cwd()
    output_job_ids_path = repo_root / OUTPUT_JOB_IDS
    output_selection_path = repo_root / OUTPUT_SELECTION
    job_ids = FULL_LONG_JOB_IDS + CHUNK_BOUNDARY_JOB_IDS + CONTROL_JOB_IDS

    output_job_ids_path.parent.mkdir(parents=True, exist_ok=True)
    output_job_ids_path.write_text("\n".join(job_ids) + "\n", encoding="utf-8")

    manifest = {
        "selection_id": SELECTION_ID,
        "workflow_role": WORKFLOW_ROLE,
        "jobs_file": JOBS_FILE,
        "job_ids_file": OUTPUT_JOB_IDS.replace("\\", "/"),
        "selected_job_count": len(job_ids),
        "selection_summary": {
            "train_examples": 10,
            "eval_examples": 3,
            "task_types": [
                "clarification",
                "faq_direct_answer",
                "step_by_step",
                "troubleshooting",
            ],
            "task_type_counts": {
                "clarification": 1,
                "faq_direct_answer": 1,
                "step_by_step": len(FULL_LONG_JOB_IDS) + len(CHUNK_BOUNDARY_JOB_IDS),
                "troubleshooting": 1,
            },
            "focus_task_type_counts": {
                "step_by_step": len(FULL_LONG_JOB_IDS) + len(CHUNK_BOUNDARY_JOB_IDS),
            },
            "selection_strategy": (
                "Small long-dialog audit subset that mixes known-green complete long flows with new complete long "
                "step_by_step examples and three chunk-boundary siblings. The goal is to separate real answer "
                "generation defects from source-cutoff or scope-truncation effects."
            ),
            "restpattern_hypotheses": [
                "complete long step_by_step flows should stay green when the documented end state is fully visible",
                "chunk-boundary siblings can expose whether source-cutoff meta responses are tied to coverage gaps",
                "if only the boundary chunks fail, the remaining blocker is probably source coverage rather than a broad prompt issue",
            ],
        },
        "historical_source": {
            "broader_reference_wave": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v4_openrouter_gpt54_findings.json"
            ),
            "long_dialog_audit_wave": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v8_openrouter_gpt54_long_dialog_step_audit_findings.json"
            ),
            "current_prompt_version": "jaws_de_support_answer_mvp_v4",
        },
        "job_ids": job_ids,
        "selection_notes": SELECTION_NOTES,
    }
    write_json(output_selection_path, manifest)
    print(f"Wrote {len(job_ids)} job IDs -> {OUTPUT_JOB_IDS}")
    print(f"Wrote selection manifest -> {OUTPUT_SELECTION}")


if __name__ == "__main__":
    main()
