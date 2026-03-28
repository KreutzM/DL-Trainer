#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-$HOME/venvs/dl-trainer-qwen}"
TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu128}"
TORCH_VERSION="${TORCH_VERSION:-2.8.0}"
TORCHVISION_VERSION="${TORCHVISION_VERSION:-0.23.0}"
TORCHAUDIO_VERSION="${TORCHAUDIO_VERSION:-2.8.0}"
VIRTUALENV_BIN="${VIRTUALENV_BIN:-virtualenv}"

resolve_python_bin() {
  if command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
    return 0
  fi

  if [[ "${PYTHON_BIN}" == "python3" ]] && command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
    return 0
  fi

  echo "Python interpreter not found: ${PYTHON_BIN}" >&2
  exit 1
}

ensure_virtualenv_tool() {
  if command -v "${VIRTUALENV_BIN}" >/dev/null 2>&1; then
    return 0
  fi

  "${PYTHON_BIN}" -m pip install --user virtualenv
  export PATH="${HOME}/.local/bin:${PATH}"

  if ! command -v "${VIRTUALENV_BIN}" >/dev/null 2>&1; then
    echo "virtualenv is not available after installation." >&2
    exit 1
  fi
}

create_or_reuse_venv() {
  mkdir -p "$(dirname "${VENV_DIR}")"

  if [[ -x "${VENV_DIR}/bin/python" ]]; then
    return 0
  fi

  if "${PYTHON_BIN}" -m venv "${VENV_DIR}" >/dev/null 2>&1; then
    return 0
  fi

  ensure_virtualenv_tool
  "${VIRTUALENV_BIN}" -p "${PYTHON_BIN}" "${VENV_DIR}"
}

resolve_python_bin
create_or_reuse_venv

# shellcheck disable=SC1090
. "${VENV_DIR}/bin/activate"
cd "${REPO_ROOT}"

python -m pip install --upgrade pip setuptools wheel
python -m pip uninstall -y torch torchvision torchaudio >/dev/null 2>&1 || true
python -m pip install \
  --index-url "${TORCH_INDEX_URL}" \
  "torch==${TORCH_VERSION}" \
  "torchvision==${TORCHVISION_VERSION}" \
  "torchaudio==${TORCHAUDIO_VERSION}"
python -m pip install -r training/transformers/requirements-qwen-server-4090-v2.txt

echo
echo "Environment ready."
echo "Venv: ${VENV_DIR}"
echo "Python: $(command -v python)"
python - <<'PY'
import torch
print("torch", torch.__version__)
print("torch_cuda", torch.version.cuda)
print("cuda_available", torch.cuda.is_available())
if torch.cuda.is_available():
    print("gpu0", torch.cuda.get_device_name(0))
PY
