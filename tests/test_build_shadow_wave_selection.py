from __future__ import annotations

from collections import Counter
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_shadow_wave_selection as shadow_selection  # noqa: E402
from common import read_json, read_jsonl  # noqa: E402


def test_build_selection_scales_current_seed_to_reviewable_32_job_wave() -> None:
    rows = read_jsonl(ROOT / "data/derived/teacher_jobs/JAWS/DE/wave1_generation_jobs.jsonl")
    seed_manifest = read_json(ROOT / "data/derived/teacher_jobs/JAWS/DE/current_generation_selection.json")
    seed_job_ids = shadow_selection.load_seed_job_ids(seed_manifest, ROOT)

    selected_rows, added_rows = shadow_selection.build_selection(rows, seed_job_ids)

    assert len(seed_job_ids) == 20
    assert len(selected_rows) == 32
    assert len(added_rows) == 12
    assert Counter(row["task_type"] for row in selected_rows) == shadow_selection.DEFAULT_TOTAL_TARGETS
    assert Counter(row["target_split"] for row in selected_rows) == {"eval": 16, "train": 16}
    assert sum(row["task_type"] == "step_by_step" for row in added_rows) == 4
    assert len({row["job_id"] for row in selected_rows}) == 32
    assert len(
        {
            chunk_id
            for row in selected_rows
            for chunk_id in row["source_chunk_ids"]
        }
    ) == 32
