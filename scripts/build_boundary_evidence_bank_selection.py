from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v13_boundary_evidence_bank"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_boundary_evidence_bank"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v13_boundary_evidence_bank_job_ids.txt"
)
OUTPUT_SELECTION = (
    "data/derived/teacher_jobs/JAWS/DE/"
    "shadow_wave_2026_04_04_user_answer_v13_boundary_evidence_bank_selection.json"
)


STEP_CASE_IDS = [
    # Pair 1: same section, first vs later chunk
    "jaws_de_teacher_wave_v1::train::step_by_step::0012",
    "jaws_de_teacher_wave_v1::train::step_by_step::0027",
    # Pair 2: same section, task-shape + later boundary chunk
    "jaws_de_teacher_wave_v1::train::step_by_step::0016",
    "jaws_de_teacher_wave_v1::train::step_by_step::0034",
    # Pair 3: attribute sibling pair
    "jaws_de_teacher_wave_v1::train::step_by_step::0033",
    "jaws_de_teacher_wave_v1::train::step_by_step::0041",
    # Pair 4: Schriftname sibling pair
    "jaws_de_teacher_wave_v1::train::step_by_step::0024",
    "jaws_de_teacher_wave_v1::train::step_by_step::0043",
    # Pair 5: import assistant split across adjacent chunks
    "jaws_de_teacher_wave_v1::train::step_by_step::0061",
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0012": (
        "Boundary pair member: the opening chunk of the Einrückung procedure."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0027": (
        "Boundary pair member: the later Einrückung chunk, useful for setup-vs-follow-up separation."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0016": (
        "Task-shape anchor: a documented procedure exists, but the prior answer shape was a question instead of a step list."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0034": (
        "Boundary pair member: later notification-rule chunk, useful to see whether completion is visible on its own."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0033": (
        "Boundary pair member: later Attribute chunk, paired with the companion chunk to test continuity."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0041": (
        "Boundary pair member: earlier Attribute chunk, used as the visible completion side."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0024": (
        "Boundary pair member: earlier Schriftname chunk, used as the setup side."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0043": (
        "Boundary pair member: later Schriftname chunk, used as the completion side."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0061": (
        "Import assistant boundary member: first half of the split procedure."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "Import assistant boundary member: second half of the split procedure, where the closure fragment lives."
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
            "train_examples": 11,
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
                "Boundary evidence bank built from adjacent chunk pairs. It keeps the task-shape anchor, "
                "two same-section boundary pairs, the import split, and two stable sibling pairs to see whether "
                "the remaining rest zone behaves like a selection/chunk artifact."
            ),
            "restpattern_hypotheses": [
                "setup and completion may separate across adjacent chunks inside the same documented procedure",
                "task-shape violations should remain clearly distinct from boundary completion failures",
                "stable sibling pairs should remain green if the boundary is the root cause rather than the prompt",
            ],
        },
        "historical_source": {
            "recent_boundary_audit": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v12_openrouter_gpt54_boundary_sibling_pair_audit_findings.json"
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
