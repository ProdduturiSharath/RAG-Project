#!/usr/bin/env bash
# GPU-pod stage.  The image owns torch/CUDA; the Python stage installs only
# pinned user-space packages and dependencies using a protected pip plan.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_TELEMETRY=1
# Prefer the pod volume; an ordinary /workspace directory is not a mount.
HF_CACHE_ROOT="$ROOT"
if mountpoint -q /workspace 2>/dev/null; then
    HF_CACHE_ROOT=/workspace
fi
export HF_HOME="${HF_HOME:-$HF_CACHE_ROOT/.cache/huggingface}"
if [[ -n "${RUNPOD_POD_ID:-}" ]] &&
    [[ "$HF_CACHE_ROOT" != /workspace || ( "$ROOT" != /workspace && "$ROOT" != /workspace/* ) ]]; then
    printf 'Phase 5 GPU advisory: checkout %s is not under a mounted /workspace.\n' "$ROOT" >&2
    printf 'Keep phase5_outputs/ and phase5_outputs.tar.gz on persistent storage.\n' >&2
fi
printf '\nPhase 5 GPU sweep/training — %s\n' "$(date -u +%FT%TZ)"
exec python scripts/phase5_gpu.py "$@"
