from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import ANSWER_MODE, JUDGE_MODE, USER_SIMULATION_MODE, stage_defaults
from common import find_repo_root, make_parser, write_json


def parse_args() -> Any:
    user_defaults = stage_defaults(USER_SIMULATION_MODE)
    answer_defaults = stage_defaults(ANSWER_MODE)
    judge_defaults = stage_defaults(JUDGE_MODE)

    parser = make_parser("Run the cost-optimized JAWS-DE Codex CLI MVP pipeline end to end.")
    parser.add_argument("--jobs", required=True)
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="read-only")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--codex-config", action="append", default=[])
    parser.add_argument("--timeout-sec", type=int, default=600)
    parser.add_argument("--promote", action="store_true")

    parser.add_argument("--user-sim-model", default=user_defaults["model"])
    parser.add_argument("--user-sim-reasoning-effort", default=user_defaults["reasoning_effort"])
    parser.add_argument("--user-sim-batch-size", type=int, default=user_defaults["batch_size"])
    parser.add_argument("--user-sim-max-attempts", type=int, default=user_defaults["max_attempts"])

    parser.add_argument("--answer-model", default=answer_defaults["model"])
    parser.add_argument("--answer-reasoning-effort", default=answer_defaults["reasoning_effort"])
    parser.add_argument("--answer-batch-size", type=int, default=answer_defaults["batch_size"])
    parser.add_argument("--answer-max-attempts", type=int, default=answer_defaults["max_attempts"])

    parser.add_argument("--judge-model", default=judge_defaults["model"])
    parser.add_argument("--judge-reasoning-effort", default=judge_defaults["reasoning_effort"])
    parser.add_argument("--judge-batch-size", type=int, default=judge_defaults["batch_size"])
    parser.add_argument("--judge-max-attempts", type=int, default=judge_defaults["max_attempts"])
    return parser.parse_args()


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def ensure_safe_run_name(run_name: str, paths: list[Path], resume: bool) -> None:
    existing = [normalized_path(path) for path in paths if path.exists()]
    if existing and not resume:
        formatted = "\n".join(f"- {path}" for path in existing)
        raise SystemExit(
            "Run name already has committed or generated artifacts. "
            "Choose a fresh --run-name or rerun with --resume.\n"
            f"{formatted}"
        )


def run_command(command: list[str], repo_root: Path) -> None:
    completed = subprocess.run(command, cwd=repo_root, text=True)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def add_job_selection_args(command: list[str], args: Any) -> None:
    for job_id in args.job_id:
        command.extend(["--job-id", job_id])
    for path in args.job_ids_file:
        command.extend(["--job-ids-file", path])
    if args.limit is not None:
        command.extend(["--limit", str(args.limit)])


def add_common_stage_args(command: list[str], args: Any) -> None:
    command.extend(["--codex-bin", args.codex_bin])
    command.extend(["--sandbox", args.sandbox])
    command.extend(["--timeout-sec", str(args.timeout_sec)])
    if args.resume:
        command.append("--resume")
    for config_value in args.codex_config:
        command.extend(["--codex-config", config_value])


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    python_bin = sys.executable
    jobs_path = Path(args.jobs)
    run_name = args.run_name

    user_sim_output = repo_root / "data/derived/user_simulations/JAWS/DE" / f"{run_name}_user_simulations.jsonl"
    user_sim_report = repo_root / "data/derived/user_simulations/JAWS/DE" / f"{run_name}_user_simulations_report.json"
    answer_raw_output = repo_root / "data/derived/teacher_outputs/JAWS/DE" / f"{run_name}_raw_responses.jsonl"
    answer_teacher_output = repo_root / "data/derived/teacher_outputs/JAWS/DE" / f"{run_name}_teacher_outputs.jsonl"
    answer_report = repo_root / "data/derived/teacher_outputs/JAWS/DE" / f"{run_name}_answer_report.json"
    judge_output = repo_root / "data/derived/teacher_reviews/JAWS/DE" / f"{run_name}_judge_results.jsonl"
    reviewed_output = repo_root / "data/derived/teacher_outputs/JAWS/DE" / f"{run_name}_reviewed_teacher_outputs.jsonl"
    judge_report = repo_root / "data/derived/teacher_reviews/JAWS/DE" / f"{run_name}_judge_report.json"
    pipeline_report = repo_root / "data/derived/teacher_reviews/JAWS/DE" / f"{run_name}_pipeline_report.json"
    train_output = repo_root / "data/gold/train/sft/JAWS/DE" / f"{run_name}_promoted_sft_samples.jsonl"
    eval_output = repo_root / "data/gold/eval/JAWS/DE" / f"{run_name}_promoted_eval_cases.jsonl"
    ensure_safe_run_name(
        run_name,
        [
            user_sim_output,
            user_sim_report,
            answer_raw_output,
            answer_teacher_output,
            answer_report,
            judge_output,
            reviewed_output,
            judge_report,
            pipeline_report,
            train_output,
            eval_output,
            repo_root / "data/derived/teacher_runs/JAWS/DE" / run_name,
        ],
        resume=args.resume,
    )

    user_command = [
        python_bin,
        "scripts/run_codex_cli_user_sim_batch.py",
        "--jobs",
        str(jobs_path),
        "--output",
        str(user_sim_output),
        "--report-output",
        str(user_sim_report),
        "--artifact-dir",
        str(repo_root / "data/derived/teacher_runs/JAWS/DE" / run_name / "user_simulations"),
        "--simulator-run-id",
        f"{run_name}_user_sim",
        "--simulator-model",
        args.user_sim_model,
        "--reasoning-effort",
        args.user_sim_reasoning_effort,
        "--batch-size",
        str(args.user_sim_batch_size),
        "--max-attempts",
        str(args.user_sim_max_attempts),
    ]
    add_job_selection_args(user_command, args)
    add_common_stage_args(user_command, args)
    run_command(user_command, repo_root)

    answer_command = [
        python_bin,
        "scripts/run_codex_cli_support_answer_batch.py",
        "--jobs",
        str(jobs_path),
        "--user-simulations",
        str(user_sim_output),
        "--raw-output",
        str(answer_raw_output),
        "--teacher-output",
        str(answer_teacher_output),
        "--report-output",
        str(answer_report),
        "--artifact-dir",
        str(repo_root / "data/derived/teacher_runs/JAWS/DE" / run_name / "answers"),
        "--teacher-run-id",
        f"{run_name}_answer",
        "--teacher-model",
        args.answer_model,
        "--reasoning-effort",
        args.answer_reasoning_effort,
        "--batch-size",
        str(args.answer_batch_size),
        "--max-attempts",
        str(args.answer_max_attempts),
    ]
    add_job_selection_args(answer_command, args)
    add_common_stage_args(answer_command, args)
    run_command(answer_command, repo_root)

    judge_command = [
        python_bin,
        "scripts/run_codex_cli_support_judge_batch.py",
        "--jobs",
        str(jobs_path),
        "--user-simulations",
        str(user_sim_output),
        "--raw-output",
        str(answer_raw_output),
        "--teacher-output",
        str(answer_teacher_output),
        "--judge-output",
        str(judge_output),
        "--reviewed-output",
        str(reviewed_output),
        "--report-output",
        str(judge_report),
        "--artifact-dir",
        str(repo_root / "data/derived/teacher_runs/JAWS/DE" / run_name / "judge"),
        "--reviewer-run-id",
        f"{run_name}_judge",
        "--reviewer-model",
        args.judge_model,
        "--reasoning-effort",
        args.judge_reasoning_effort,
        "--batch-size",
        str(args.judge_batch_size),
        "--max-attempts",
        str(args.judge_max_attempts),
    ]
    add_job_selection_args(judge_command, args)
    add_common_stage_args(judge_command, args)
    run_command(judge_command, repo_root)

    promoted = False
    if args.promote:
        promote_command = [
            python_bin,
            "scripts/promote_teacher_outputs.py",
            "--input",
            str(reviewed_output),
            "--train-output",
            str(train_output),
            "--eval-output",
            str(eval_output),
            "--allow-codex-reviewed",
        ]
        run_command(promote_command, repo_root)
        promoted = True

    user_report = json.loads(user_sim_report.read_text(encoding="utf-8"))
    answer_stage_report = json.loads(answer_report.read_text(encoding="utf-8"))
    judge_stage_report = json.loads(judge_report.read_text(encoding="utf-8"))
    pipeline_summary = {
        "jobs_path": normalized_path(jobs_path),
        "run_name": run_name,
        "stages": {
            "user_simulation": user_report,
            "answering": answer_stage_report,
            "judge": judge_stage_report,
        },
        "defaults": {
            "user_simulation": {
                "model": args.user_sim_model,
                "reasoning_effort": args.user_sim_reasoning_effort,
                "batch_size": args.user_sim_batch_size,
                "max_attempts": args.user_sim_max_attempts,
            },
            "answering": {
                "model": args.answer_model,
                "reasoning_effort": args.answer_reasoning_effort,
                "batch_size": args.answer_batch_size,
                "max_attempts": args.answer_max_attempts,
            },
            "judge": {
                "model": args.judge_model,
                "reasoning_effort": args.judge_reasoning_effort,
                "batch_size": args.judge_batch_size,
                "max_attempts": args.judge_max_attempts,
            },
        },
        "paths": {
            "user_simulations": normalized_path(user_sim_output),
            "raw_responses": normalized_path(answer_raw_output),
            "teacher_outputs": normalized_path(answer_teacher_output),
            "judge_results": normalized_path(judge_output),
            "reviewed_outputs": normalized_path(reviewed_output),
            "train_output": normalized_path(train_output) if promoted else None,
            "eval_output": normalized_path(eval_output) if promoted else None,
        },
        "promotion_ran": promoted,
    }
    write_json(pipeline_report, pipeline_summary)
    print(f"Wrote pipeline report -> {pipeline_report}")


if __name__ == "__main__":
    main()
