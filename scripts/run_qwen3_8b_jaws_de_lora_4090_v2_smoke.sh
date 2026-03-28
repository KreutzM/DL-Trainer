#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONFIG_REL="training/transformers/qwen3_8b_jaws_de_lora_4090_v2.yaml"
RUN_NAME="qwen3_8b_jaws_de_lora_4090_v2"
DEFAULT_ADAPTER_REL="training/transformers/outputs/${RUN_NAME}/final_adapter"
POST_RUN_DIR_REL="training/transformers/outputs/${RUN_NAME}/post_run"
PYTHON_BIN="${PYTHON_BIN:-python}"
TIMESTAMP="$(date -u +"%Y%m%dT%H%M%SZ")"

ADAPTER_REL="${DEFAULT_ADAPTER_REL}"
OUTPUT_REL="${POST_RUN_DIR_REL}/smoke_test_${TIMESTAMP}.json"

case "${1:-}" in
  "")
    ;;
  --adapter-dir)
    if [[ $# -lt 2 ]]; then
      echo "Missing adapter directory for --adapter-dir" >&2
      exit 2
    fi
    ADAPTER_REL="$2"
    shift 2
    ;;
  *)
    echo "Usage: scripts/run_qwen3_8b_jaws_de_lora_4090_v2_smoke.sh [--adapter-dir <path>]" >&2
    exit 2
    ;;
esac

mkdir -p "${REPO_ROOT}/${POST_RUN_DIR_REL}"
cd "${REPO_ROOT}"

"${PYTHON_BIN}" scripts/smoke_test_qwen_lora_adapter.py \
  --config "${CONFIG_REL}" \
  --adapter-dir "${ADAPTER_REL}" \
  --output "${OUTPUT_REL}"

echo "Smoke test written to ${OUTPUT_REL}"
