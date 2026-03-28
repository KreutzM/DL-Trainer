#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="training/transformers/qwen3_8b_jaws_de_lora_4090_v3.yaml"
RUN_NAME="qwen3_8b_jaws_de_lora_4090_v3"
OUTPUT_DIR_REL="training/transformers/outputs/${RUN_NAME}"
LOG_DIR_REL="training/transformers/logs/${RUN_NAME}"
PYTHON_BIN="${PYTHON_BIN:-python}"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"

resolve_python_bin() {
  if command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    return 0
  fi

  if [[ "${PYTHON_BIN}" == "python" ]] && command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
    return 0
  fi

  echo "Python interpreter not found: ${PYTHON_BIN}" >&2
  echo "Set PYTHON_BIN explicitly or ensure python/python3 is on PATH." >&2
  exit 1
}

usage() {
  echo "Usage:"
  echo "  scripts/start_qwen3_8b_jaws_de_lora_4090_v3.sh"
  echo "  scripts/start_qwen3_8b_jaws_de_lora_4090_v3.sh --resume-latest"
  echo "  scripts/start_qwen3_8b_jaws_de_lora_4090_v3.sh --resume-from <checkpoint-dir>"
}

find_latest_checkpoint() {
  local output_dir="$1"
  find "${output_dir}" -maxdepth 1 -mindepth 1 -type d -name 'checkpoint-*' -printf '%f\n' | sort -V | tail -n 1
}

RESUME_MODE="fresh"
RESUME_ARG=()

case "${1:-}" in
  "")
    ;;
  --resume-latest)
    RESUME_MODE="resume-latest"
    ;;
  --resume-from)
    if [[ $# -lt 2 ]]; then
      usage
      exit 2
    fi
    RESUME_MODE="resume-from"
    RESUME_ARG=(--resume-from-checkpoint "$2")
    ;;
  *)
    usage
    exit 2
    ;;
esac

mkdir -p "${REPO_ROOT}/${LOG_DIR_REL}"

PREFLIGHT_LOG_REL="${LOG_DIR_REL}/preflight_${TIMESTAMP}.log"
PREFLIGHT_SUMMARY_REL="${LOG_DIR_REL}/preflight_${TIMESTAMP}.json"
TRAIN_LOG_REL="${LOG_DIR_REL}/train_${TIMESTAMP}.log"

ALLOW_EXISTING_OUTPUT=()
if [[ "${RESUME_MODE}" != "fresh" ]]; then
  ALLOW_EXISTING_OUTPUT=(--allow-existing-output)
fi

if [[ "${RESUME_MODE}" == "resume-latest" ]]; then
  LATEST_CHECKPOINT="$(find_latest_checkpoint "${REPO_ROOT}/${OUTPUT_DIR_REL}")"
  if [[ -z "${LATEST_CHECKPOINT}" ]]; then
    echo "No checkpoint-* directory found under ${OUTPUT_DIR_REL}" >&2
    exit 1
  fi
  RESUME_ARG=(--resume-from-checkpoint "${OUTPUT_DIR_REL}/${LATEST_CHECKPOINT}")
fi

export TOKENIZERS_PARALLELISM=false
export PYTHONUNBUFFERED=1

cd "${REPO_ROOT}"
resolve_python_bin

"${PYTHON_BIN}" scripts/preflight_qwen_lora_server.py \
  --config "${CONFIG_REL}" \
  --summary-output "${PREFLIGHT_SUMMARY_REL}" \
  "${ALLOW_EXISTING_OUTPUT[@]}" \
  2>&1 | tee "${PREFLIGHT_LOG_REL}"

"${PYTHON_BIN}" scripts/run_qwen_lora_training.py \
  --config "${CONFIG_REL}" \
  "${RESUME_ARG[@]}" \
  2>&1 | tee "${TRAIN_LOG_REL}"

echo
echo "Training finished."
echo "Run log: ${TRAIN_LOG_REL}"
echo "Preflight summary: ${PREFLIGHT_SUMMARY_REL}"
echo "Next step:"
echo "  scripts/run_qwen3_8b_jaws_de_lora_4090_v3_smoke.sh"
