from __future__ import annotations

from pathlib import Path

from common import write_json


SELECTION_ID = "jaws_de_shadow_wave_2026_04_04_user_answer_v7_composite_step_restpattern"
WORKFLOW_ROLE = "shadow_wave_user_answer_gpt54_composite_step_restpattern"
JOBS_FILE = "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl"
OUTPUT_JOB_IDS = "data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v7_composite_step_restpattern_job_ids.txt"
OUTPUT_SELECTION = "data/derived/teacher_jobs/JAWS/DE/shadow_wave_2026_04_04_user_answer_v7_composite_step_restpattern_selection.json"

STEP_STRESS_JOB_IDS = [
    "jaws_de_teacher_wave_v1::train::step_by_step::0002",
    "jaws_de_teacher_wave_v1::eval::step_by_step::0004",
    "jaws_de_teacher_wave_v1::eval::step_by_step::0006",
    "jaws_de_teacher_wave_v1::train::step_by_step::0013",
    "jaws_de_teacher_wave_v1::train::step_by_step::0019",
    "jaws_de_teacher_wave_v1::train::step_by_step::0037",
    "jaws_de_teacher_wave_v1::train::step_by_step::0048",
    "jaws_de_teacher_wave_v1::train::step_by_step::0053",
    "jaws_de_teacher_wave_v1::train::step_by_step::0054",
    "jaws_de_teacher_wave_v1::train::step_by_step::0061",
    "jaws_de_teacher_wave_v1::train::step_by_step::0062",
    "jaws_de_teacher_wave_v1::train::step_by_step::0063",
]

CONTROL_JOB_IDS = [
    "jaws_de_teacher_wave_v1::eval::clarification::0007",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010",
    "jaws_de_teacher_wave_v1::eval::troubleshooting::0005",
    "jaws_de_teacher_wave_v1::train::uncertainty_escalation::0010",
]

SELECTION_NOTES = {
    "jaws_de_teacher_wave_v1::train::step_by_step::0002": (
        "Known adjacent-procedure blocker: opening Stimmeneinstellungen and the separate Stimmenprofil path live in one excerpt."
    ),
    "jaws_de_teacher_wave_v1::eval::step_by_step::0004": (
        "One excerpt contains two neighboring procedures, Schriftgroessenregel bearbeiten or loeschen, with shared closing steps."
    ),
    "jaws_de_teacher_wave_v1::eval::step_by_step::0006": (
        "Known branch-scope stress case: add or remove voices can collapse to install only."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0013": (
        "Rules can be bearbeiten, loeschen, or umbenennen from one context menu; easy to merge or answer only one branch."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0019": (
        "Reordering rules branches between moving up and moving down inside one management dialog."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0037": (
        "Settings path branches between app-specific and default scope, then continues into a second optional sound setting."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0048": (
        "Stable green anchor with warning confirmation and import-result closure; checks that long assistant flows still stay green."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0053": (
        "Voice utility explicitly covers installieren oder entfernen; tests whether the answer keeps both branches in scope."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0054": (
        "Long multi-page dialog flow that can drift between tab-scoping and rule creation details."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0061": (
        "Known long import-assistant blocker with risk of escalation instead of documented steps."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0062": (
        "Second half of the same import assistant focuses on merge-vs-keep conflict handling and true goal completion."
    ),
    "jaws_de_teacher_wave_v1::train::step_by_step::0063": (
        "Stable green anchor with delete-then-restore voice profile sequence and a fragile end state."
    ),
    "jaws_de_teacher_wave_v1::eval::clarification::0007": "Stable clarification control.",
    "jaws_de_teacher_wave_v1::train::faq_direct_answer::0010": "Stable faq_direct_answer control.",
    "jaws_de_teacher_wave_v1::eval::troubleshooting::0005": "Stable troubleshooting control.",
    "jaws_de_teacher_wave_v1::train::uncertainty_escalation::0010": "Stable uncertainty_escalation control.",
}


def main() -> None:
    repo_root = Path.cwd()
    output_job_ids_path = repo_root / OUTPUT_JOB_IDS
    output_selection_path = repo_root / OUTPUT_SELECTION
    job_ids = STEP_STRESS_JOB_IDS + CONTROL_JOB_IDS

    output_job_ids_path.parent.mkdir(parents=True, exist_ok=True)
    output_job_ids_path.write_text("\n".join(job_ids) + "\n", encoding="utf-8")

    manifest = {
        "selection_id": SELECTION_ID,
        "workflow_role": WORKFLOW_ROLE,
        "jobs_file": JOBS_FILE,
        "job_ids_file": OUTPUT_JOB_IDS.replace("\\", "/"),
        "selected_job_count": len(job_ids),
        "selection_summary": {
            "train_examples": 12,
            "eval_examples": 4,
            "task_types": [
                "clarification",
                "faq_direct_answer",
                "step_by_step",
                "troubleshooting",
                "uncertainty_escalation",
            ],
            "task_type_counts": {
                "clarification": 1,
                "faq_direct_answer": 1,
                "step_by_step": len(STEP_STRESS_JOB_IDS),
                "troubleshooting": 1,
                "uncertainty_escalation": 1,
            },
            "focus_task_type_counts": {
                "step_by_step": len(STEP_STRESS_JOB_IDS),
            },
            "selection_strategy": (
                "Manually curated rest-pattern subset. Repeats the three known composite-step blockers, "
                "then adds nearby branchy/composite procedures that stress one-of-many branch choice, "
                "adjacent procedure mixing, long assistant completion, and avoidable escalation. "
                "Includes four stable non-step controls to detect spillover."
            ),
            "restpattern_hypotheses": [
                "adjacent procedures inside one excerpt are still vulnerable to over-merging",
                "branchy user goals can collapse to only one requested path",
                "long assistant flows can still miss the true end state or escalate unnecessarily",
            ],
        },
        "historical_source": {
            "broader_reference_wave": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v4_openrouter_gpt54_findings.json"
            ),
            "composite_collection_wave": (
                "data/derived/teacher_reviews/JAWS/DE/benchmarks/"
                "jaws_de_shadow_2026_04_04_user_answer_v6_openrouter_gpt54_composite_step_collection_findings.json"
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
