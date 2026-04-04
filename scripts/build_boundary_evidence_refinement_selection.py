from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v14_boundary_evidence_refinement"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_boundary_evidence_refinement"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v14_boundary_evidence_refinement_job_ids.txt"
)
OUTPUT_SELECTION = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v14_boundary_evidence_refinement_selection.json"
)


STEP_CASE_IDS = [
    "jaws_de_teacher_wave_v1::train::step_by_step::0016",
    "jaws_de_teacher_wave_v1::train::step_by_step::0034",
    "jaws_de_teacher_wave_v1::train::step_by_step::0061",
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
    "jaws_de_teacher_wave_v1::train::step_by_step::0048",
    "jaws_de_teacher_wave_v1::train::step_by_step::0012",
    "jaws_de_teacher_wave_v1::train::step_by_step::0027",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0016": (
        "Task-shape failure anchor: this is the known case where a question replaced the procedure."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0034": (
        "Direct neighbor in the same notification-rule section; useful to see whether the later chunk stays green."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0061": (
        "Setup-side import fragment; the previous waves showed it as the surviving completion-gap case."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "Completion-side import fragment; paired with 0061 to test whether the split behaves consistently."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0048": (
        "Full import anchor from a related settings-import path; useful as a complete long-flow comparator."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0012": (
        "Green control from the Einrückung pair; establishes that the same document family can still complete cleanly."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0027": (
        "Companion green control for the Einrückung pair."
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
            "train_examples": 8,
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
                "Refinement bank centered on the two remaining rest cases. It keeps the task-shape anchor, the "
                "import split, a complete import comparator, and a known-green sibling pair so the boundary "
                "effect can be separated from a generic answer problem."
            ),
            "restpattern_hypotheses": [
                "the remaining failures should separate into task-shape, setup-missing, and completion-missing bins",
                "the completion-side import fragment should align with the setup-side fragment if the issue is a real boundary artifact",
                "complete sibling flows should remain green if the prompt is not the root cause",
            ],
        },
        "historical_source": {
            "recent_evidence_bank": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v13_openrouter_gpt54_boundary_evidence_bank_findings.json"
            ),
            "boundary_prompt_pass": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v11_openrouter_gpt54_step_boundary_casebank_findings.json"
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
