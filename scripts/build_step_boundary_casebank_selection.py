from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v10_step_boundary_casebank"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_step_boundary_casebank"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v10_step_boundary_casebank_job_ids.txt"
)
OUTPUT_SELECTION = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v10_step_boundary_casebank_selection.json"
)


STEP_CASE_IDS = [
    # task-type / wrong shape
    "jaws_de_teacher_wave_v1::train::step_by_step::0016",
    # mid-procedure omission / incomplete beginning
    "jaws_de_teacher_wave_v1::train::step_by_step::0034",
    # end-state-only / import completion fragment
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
    # same import section, sibling boundary chunk
    "jaws_de_teacher_wave_v1::train::step_by_step::0061",
    # chunk-boundary sibling pair for a different long flow
    "jaws_de_teacher_wave_v1::train::step_by_step::0033",
    "jaws_de_teacher_wave_v1::train::step_by_step::0041",
    # second sibling pair for boundary comparison
    "jaws_de_teacher_wave_v1::train::step_by_step::0024",
    "jaws_de_teacher_wave_v1::train::step_by_step::0043",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0016": (
        "Task-shape failure: the answer asks a question instead of giving a procedure."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0034": (
        "Mid-procedure omission: the answer starts too late and misses the setup."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "End-state-only fragment: the answer covers only the closing import steps."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0061": (
        "Sibling chunk for the same import assistant, useful to test whether the boundary is the real issue."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0033": (
        "Sibling chunk in the Attribute flow, useful as a boundary comparison point."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0041": (
        "Companion chunk for the Attribute flow, previously green and useful as a completion anchor."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0024": (
        "Sibling chunk in the Schriftname flow, useful as a boundary comparison point."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0043": (
        "Companion chunk for the Schriftname flow, previously green and useful as a completion anchor."
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
                "Boundary case bank for the remaining step_by_step rest zone. Includes the known task-shape, "
                "mid-procedure, and end-state-only rejects plus sibling chunk pairs that can tell whether the "
                "problem repeats on adjacent source chunks or collapses when the full flow is visible."
            ),
            "restpattern_hypotheses": [
                "task-type violations should stay separable from real completeness failures",
                "mid-procedure omissions should cluster differently from end-state-only import fragments",
                "boundary sibling chunks reveal whether the source cutoff is the actual root cause",
            ],
        },
        "historical_source": {
            "recent_long_dialog_wave": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v9_openrouter_gpt54_complete_long_dialog_step_collection_findings.json"
            ),
            "earlier_boundary_audits": (
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
