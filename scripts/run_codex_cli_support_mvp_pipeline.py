from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from codex_cli_support_mvp_common import (
    ANSWER_MODE,
    JUDGE_MODE,
    LEGACY_TIMEOUT_DEFAULT_SEC,
    USER_SIMULATION_MODE,
    stage_defaults,
)
from common import find_repo_root, make_parser, write_json
from llm_json_backends import OPENROUTER_API_BASE
from llm_stage_profiles import ResolvedStageLlmProfile, resolve_profile_set


def parse_args() -> Any:
    user_defaults = stage_defaults(USER_SIMULATION_MODE)
    answer_defaults = stage_defaults(ANSWER_MODE)
    judge_defaults = stage_defaults(JUDGE_MODE)

    parser = make_parser("Run the cost-optimized JAWS-DE Codex CLI MVP pipeline end to end.")
    parser.add_argument("--jobs")
    parser.add_argument("--selection-manifest")
    parser.add_argument("--run-name", required=True)
    parser.add_argument("--job-id", action="append", default=[])
    parser.add_argument("--job-ids-file", action="append", default=[])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--sandbox", default="read-only")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--codex-config", action="append", default=[])
    parser.add_argument("--timeout-sec", type=int, default=600)
    parser.add_argument("--llm-backend", choices=["codex_cli", "openrouter"], default="codex_cli")
    parser.add_argument("--openrouter-api-base", default=OPENROUTER_API_BASE)
    parser.add_argument("--openrouter-api-key-env", default="OPENROUTER_API_KEY")
    parser.add_argument("--llm-profile-config")
    parser.add_argument("--llm-profile-set")
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
    args = parser.parse_args()
    if not args.jobs and not args.selection_manifest:
        parser.error("either --jobs or --selection-manifest is required")
    return args


def normalized_path(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_selection_manifest(path_value: str, repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / path_value
    manifest = read_json(manifest_path)
    if not manifest.get("jobs_file"):
        raise SystemExit("Selection manifest is missing required key: jobs_file")
    return manifest


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
    if args.resume:
        command.append("--resume")
    if args.llm_profile_set:
        if args.llm_profile_config:
            command.extend(["--llm-profile-config", args.llm_profile_config])
        command.extend(["--llm-profile-set", args.llm_profile_set])
        return
    command.extend(["--sandbox", args.sandbox])
    command.extend(["--timeout-sec", str(args.timeout_sec)])
    command.extend(["--llm-backend", args.llm_backend])
    command.extend(["--openrouter-api-base", args.openrouter_api_base])
    command.extend(["--openrouter-api-key-env", args.openrouter_api_key_env])
    for config_value in args.codex_config:
        command.extend(["--codex-config", config_value])


def ensure_profile_mode_has_no_pipeline_overrides(args: Any) -> None:
    user_defaults = stage_defaults(USER_SIMULATION_MODE)
    answer_defaults = stage_defaults(ANSWER_MODE)
    judge_defaults = stage_defaults(JUDGE_MODE)
    conflicts: list[str] = []
    if args.timeout_sec != LEGACY_TIMEOUT_DEFAULT_SEC:
        conflicts.append("--timeout-sec")
    if args.llm_backend != "codex_cli":
        conflicts.append("--llm-backend")
    if args.sandbox != "read-only":
        conflicts.append("--sandbox")
    if args.openrouter_api_base != OPENROUTER_API_BASE:
        conflicts.append("--openrouter-api-base")
    if args.openrouter_api_key_env != "OPENROUTER_API_KEY":
        conflicts.append("--openrouter-api-key-env")
    if args.codex_config:
        conflicts.append("--codex-config")
    stage_defaults_by_option = {
        "--user-sim-model": user_defaults["model"],
        "--user-sim-reasoning-effort": user_defaults["reasoning_effort"],
        "--user-sim-batch-size": user_defaults["batch_size"],
        "--user-sim-max-attempts": user_defaults["max_attempts"],
        "--answer-model": answer_defaults["model"],
        "--answer-reasoning-effort": answer_defaults["reasoning_effort"],
        "--answer-batch-size": answer_defaults["batch_size"],
        "--answer-max-attempts": answer_defaults["max_attempts"],
        "--judge-model": judge_defaults["model"],
        "--judge-reasoning-effort": judge_defaults["reasoning_effort"],
        "--judge-batch-size": judge_defaults["batch_size"],
        "--judge-max-attempts": judge_defaults["max_attempts"],
    }
    current_values = {
        "--user-sim-model": args.user_sim_model,
        "--user-sim-reasoning-effort": args.user_sim_reasoning_effort,
        "--user-sim-batch-size": args.user_sim_batch_size,
        "--user-sim-max-attempts": args.user_sim_max_attempts,
        "--answer-model": args.answer_model,
        "--answer-reasoning-effort": args.answer_reasoning_effort,
        "--answer-batch-size": args.answer_batch_size,
        "--answer-max-attempts": args.answer_max_attempts,
        "--judge-model": args.judge_model,
        "--judge-reasoning-effort": args.judge_reasoning_effort,
        "--judge-batch-size": args.judge_batch_size,
        "--judge-max-attempts": args.judge_max_attempts,
    }
    for option_name, default_value in stage_defaults_by_option.items():
        if current_values[option_name] != default_value:
            conflicts.append(option_name)
    if conflicts:
        joined = ", ".join(conflicts)
        raise SystemExit(f"--llm-profile-set cannot be combined with legacy pipeline LLM overrides: {joined}")


def resolved_profile_report(profiles: dict[str, ResolvedStageLlmProfile]) -> dict[str, Any]:
    return {stage_name: profile.summary() for stage_name, profile in profiles.items()}


def legacy_stage_summary(
    *,
    backend: str,
    model: str,
    batch_size: int,
    max_attempts: int,
    timeout_sec: int,
    reasoning_effort: str,
    sandbox: str,
    codex_config: list[str],
    openrouter_api_base: str,
    openrouter_api_key_env: str,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "backend": backend,
        "model": model,
        "batch_size": batch_size,
        "max_attempts": max_attempts,
        "timeout_sec": timeout_sec,
    }
    if backend == "codex_cli":
        payload["codex_cli"] = {
            "reasoning_effort": reasoning_effort,
            "sandbox": sandbox,
            "extra_config": list(codex_config),
        }
    else:
        payload["openrouter"] = {
            "api_base": openrouter_api_base,
            "api_key_env": openrouter_api_key_env,
            "extra_headers": {},
            "provider_options": {},
        }
    return payload


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    resolved_profiles: dict[str, ResolvedStageLlmProfile] | None = None
    if args.llm_profile_set:
        ensure_profile_mode_has_no_pipeline_overrides(args)
        resolved_profiles = resolve_profile_set(
            repo_root,
            profile_set_name=args.llm_profile_set,
            profile_config_path=args.llm_profile_config,
            check_runtime_env=True,
        )
    python_bin = sys.executable
    selection_manifest_path = args.selection_manifest
    if selection_manifest_path:
        selection_manifest = load_selection_manifest(selection_manifest_path, repo_root)
        if args.jobs and args.jobs != selection_manifest["jobs_file"]:
            raise SystemExit("Selection manifest jobs_file conflicts with explicit --jobs value.")
        args.jobs = selection_manifest["jobs_file"]
        if not args.job_id and not args.job_ids_file and args.limit is None:
            job_ids_file = selection_manifest.get("job_ids_file")
            if job_ids_file:
                args.job_ids_file.append(job_ids_file)
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
    ]
    if not args.llm_profile_set:
        user_command.extend(
            [
                "--simulator-model",
                args.user_sim_model,
                "--reasoning-effort",
                args.user_sim_reasoning_effort,
                "--batch-size",
                str(args.user_sim_batch_size),
                "--max-attempts",
                str(args.user_sim_max_attempts),
            ]
        )
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
    ]
    if not args.llm_profile_set:
        answer_command.extend(
            [
                "--teacher-model",
                args.answer_model,
                "--reasoning-effort",
                args.answer_reasoning_effort,
                "--batch-size",
                str(args.answer_batch_size),
                "--max-attempts",
                str(args.answer_max_attempts),
            ]
        )
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
    ]
    if not args.llm_profile_set:
        judge_command.extend(
            [
                "--reviewer-model",
                args.judge_model,
                "--reasoning-effort",
                args.judge_reasoning_effort,
                "--batch-size",
                str(args.judge_batch_size),
                "--max-attempts",
                str(args.judge_max_attempts),
            ]
        )
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
        "selection_manifest": selection_manifest_path,
        "stages": {
            "user_simulation": user_report,
            "answering": answer_stage_report,
            "judge": judge_stage_report,
        },
        "defaults": {
            "user_simulation": resolved_profiles["user_simulation"].summary()
            if resolved_profiles
            else legacy_stage_summary(
                backend=args.llm_backend,
                model=args.user_sim_model,
                batch_size=args.user_sim_batch_size,
                max_attempts=args.user_sim_max_attempts,
                timeout_sec=args.timeout_sec,
                reasoning_effort=args.user_sim_reasoning_effort,
                sandbox=args.sandbox,
                codex_config=args.codex_config,
                openrouter_api_base=args.openrouter_api_base,
                openrouter_api_key_env=args.openrouter_api_key_env,
            ),
            "answering": resolved_profiles["answer"].summary()
            if resolved_profiles
            else legacy_stage_summary(
                backend=args.llm_backend,
                model=args.answer_model,
                batch_size=args.answer_batch_size,
                max_attempts=args.answer_max_attempts,
                timeout_sec=args.timeout_sec,
                reasoning_effort=args.answer_reasoning_effort,
                sandbox=args.sandbox,
                codex_config=args.codex_config,
                openrouter_api_base=args.openrouter_api_base,
                openrouter_api_key_env=args.openrouter_api_key_env,
            ),
            "judge": resolved_profiles["judge"].summary()
            if resolved_profiles
            else legacy_stage_summary(
                backend=args.llm_backend,
                model=args.judge_model,
                batch_size=args.judge_batch_size,
                max_attempts=args.judge_max_attempts,
                timeout_sec=args.timeout_sec,
                reasoning_effort=args.judge_reasoning_effort,
                sandbox=args.sandbox,
                codex_config=args.codex_config,
                openrouter_api_base=args.openrouter_api_base,
                openrouter_api_key_env=args.openrouter_api_key_env,
            ),
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
    if resolved_profiles:
        pipeline_summary["llm_profile_set"] = args.llm_profile_set
        pipeline_summary["llm_profiles"] = resolved_profile_report(resolved_profiles)
    write_json(pipeline_report, pipeline_summary)
    print(f"Wrote pipeline report -> {pipeline_report}")


if __name__ == "__main__":
    main()
