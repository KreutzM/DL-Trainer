from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from compare_judge_runs import build_judge_run_delta


def _row(job_id: str, task_type: str, decision: str, score: int, summary: str) -> dict:
    return {
        "job_id": job_id,
        "task_type": task_type,
        "decision": decision,
        "quality_score": score,
        "summary": summary,
        "blocking_reasons": [],
    }


def test_build_judge_run_delta_tracks_decision_and_score_changes() -> None:
    baseline = {
        "job-a": _row("job-a", "step_by_step", "approve", 90, "baseline a"),
        "job-b": _row("job-b", "faq_direct_answer", "reject", 60, "baseline b"),
    }
    candidate = {
        "job-a": _row("job-a", "step_by_step", "reject", 55, "candidate a"),
        "job-b": _row("job-b", "faq_direct_answer", "reject", 70, "candidate b"),
    }

    summary = build_judge_run_delta(baseline, candidate, focus_task_types={"step_by_step"})

    assert summary["total_jobs"] == 2
    assert summary["decision_changes"] == 1
    assert summary["improved_scores"] == 1
    assert summary["worsened_scores"] == 1
    assert summary["unchanged_scores"] == 0
    assert summary["avg_quality_score_delta"] == -12.5
    assert [case["job_id"] for case in summary["changed_cases"]] == ["job-a"]


def test_build_judge_run_delta_requires_identical_job_ids() -> None:
    baseline = {"job-a": _row("job-a", "step_by_step", "approve", 90, "baseline")}
    candidate = {"job-b": _row("job-b", "step_by_step", "approve", 90, "candidate")}

    try:
        build_judge_run_delta(baseline, candidate)
    except SystemExit as exc:
        assert "judge result job_id mismatch" in str(exc)
        assert "missing_in_candidate=job-a" in str(exc)
        assert "missing_in_baseline=job-b" in str(exc)
    else:
        raise AssertionError("Expected SystemExit for mismatched job_ids")
