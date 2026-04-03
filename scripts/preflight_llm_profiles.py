from __future__ import annotations

from pathlib import Path
from typing import Any

from common import find_repo_root, make_parser
from llm_stage_profiles import load_profile_config, resolve_profile_set


def parse_args() -> Any:
    parser = make_parser("Validate LLM stage profile configuration and optionally preflight a selected profile set.")
    parser.add_argument("--config")
    parser.add_argument("--profile-set")
    parser.add_argument("--skip-env-check", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = find_repo_root(Path.cwd())
    config = load_profile_config(repo_root, args.config)
    print(f"Validated LLM profile config with {len(config['profile_sets'])} profile set(s).")
    if not args.profile_set:
        print("Available profile sets: " + ", ".join(sorted(config["profile_sets"])))
        return
    resolved = resolve_profile_set(
        repo_root,
        profile_set_name=args.profile_set,
        profile_config_path=args.config,
        check_runtime_env=not args.skip_env_check,
    )
    print(f"Preflight passed for profile set {args.profile_set}.")
    for stage_name, profile in resolved.items():
        print(f"- {stage_name}: {profile.backend} / {profile.model} / {profile.profile_name}")


if __name__ == "__main__":
    main()
