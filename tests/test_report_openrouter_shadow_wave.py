from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import report_openrouter_shadow_wave as shadow_report  # noqa: E402


def test_shadow_wave_report_builds_from_existing_openrouter_gpt54_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    output_path = tmp_path / "shadow_wave_report.json"
    report_path = (
        ROOT
        / "data/derived/teacher_reviews/JAWS/DE/jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1_pipeline_report.json"
    )

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "report_openrouter_shadow_wave.py",
            "--report-path",
            str(report_path),
            "--output",
            str(output_path),
        ],
    )

    shadow_report.main()

    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["run_name"] == "jaws_de_shadow_2026_04_04_expanded_v1_openrouter_gpt54_v1"
    assert report["judge_role"]["shadow_only"] is True
    assert report["judge_role"]["intended_role"] == "secondary_audit_judge"
    assert report["processing"]["jobs_total"] == 20
    assert report["approval_distribution"] == {"approve": 18, "reject": 2}
    assert report["provider_usage"]["answer"]["rows_with_provider_usage"] == 20
    assert report["provider_usage"]["judge"]["rows_with_provider_usage"] == 20
    assert report["qualitative_focus_cases"]
