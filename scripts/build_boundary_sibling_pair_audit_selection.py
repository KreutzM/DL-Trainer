from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v12_boundary_sibling_pair_audit"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_boundary_sibling_pair_audit"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v12_boundary_sibling_pair_audit_job_ids.txt"
)
OUTPUT_SELECTION = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v12_boundary_sibling_pair_audit_selection.json"
)


STEP_CASE_IDS = [
    # task-shape violation anchor
    "jaws_de_teacher_wave_v1::train::step_by_step::0016",
    # same section, later chunk; missing setup / early-step omission
    "jaws_de_teacher_wave_v1::train::step_by_step::0034",
    # import assistant, first half
    "jaws_de_teacher_wave_v1::train::step_by_step::0061",
    # import assistant, second half
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
    # attribute sibling pair, one side of the boundary
    "jaws_de_teacher_wave_v1::train::step_by_step::0033",
    "jaws_de_teacher_wave_v1::train::step_by_step::0041",
    # font-name sibling pair, one side of the boundary
    "jaws_de_teacher_wave_v1::train::step_by_step::0024",
    "jaws_de_teacher_wave_v1::train::step_by_step::0043",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0016": (
        "Task-shape violation anchor: the response asks a question instead of giving the requested procedure."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0034": (
        "Boundary sibling candidate: later chunk in the notification-rule flow, used to test missing setup versus completion."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0061": (
        "Boundary sibling candidate: first half of the import assistant, useful for setup-versus-finish separation."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "Boundary sibling candidate: second half of the same import assistant, useful for finish-versus-setup separation."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0033": (
        "Boundary sibling candidate in the Attribute flow; paired with the companion chunk to see if the same procedure remains coherent."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0041": (
        "Companion chunk in the Attribute flow; used as the visible completion side of the pair."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0024": (
        "Boundary sibling candidate in the Schriftname flow; paired with the companion chunk to test end-state continuity."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0043": (
        "Companion chunk in the Schriftname flow; used as the visible completion side of the pair."
    ),
    "jaws_de_teacher_wave_v1::eval::clarification::0007": "Stable clarification control.",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010": "Stable faq_direct_answer control.",
}


def main() -> None:
    repo_root = Path.cwd()
    output_job_ids_path = repo_root / OUTPUT_JOB_IDS
    output_selection_path = repo_root / OUTPUT_SELECTION
    job_ids = STEP_CASE_IDS + CONTROL_JOB_IDS

    output_job_ids_path.parent.mkdir(parents=True, exist_ok=True)
    output_job_ids_path.write_text("\n".join(job_ids) + "\n", encoding="utf-8")

    manifest = {
        "selection_id": SELECTION_ID,
        "workflow_role": WORKFLOW_ROLE,
        "jobs_file": JOBS_FILE,
        "job_ids_file": OUTPUT_JOB_IDS.replace("\\", "/"),
        "selected_job_count": len(job_ids),
        "selection_summary": {
            "train_examples": 9,
            "eval_examples": 2,
            "task_types": [
                "clarification",
                "faq_direct_answer",
                "step_by_step",
            ],
            "task_type_counts": {
                "clarification": 1,
                "faq_direct_answer": 1,
                "step_by_step": len(STEP_CASE_IDS),
            },
            "focus_task_type_counts": {
                "step_by_step": len(STEP_CASE_IDS),
            },
            "selection_strategy": (
                "Small boundary/sibling audit bank. It combines the known task-shape failure with two "
                "boundary-completeness pairs and two stable sibling pairs so we can see whether setup and "
                "finish split across adjacent chunks in a reproducible way."
            ),
            "restpattern_hypotheses": [
                "task-shape violations should remain separable from completeness failures",
                "import assistant fragments should split into setup-missing and finish-missing sides",
                "stable sibling pairs should stay green if the boundary is not the real root cause",
            ],
        },
        "historical_source": {
            "recent_boundary_bank": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v11_openrouter_gpt54_step_boundary_casebank_findings.json"
            ),
            "long_dialog_reference": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v9_openrouter_gpt54_complete_long_dialog_step_collection_findings.json"
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
