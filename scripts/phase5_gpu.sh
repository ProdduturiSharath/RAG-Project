#!/usr/bin/env bash
# GPU-pod stage.  The image owns torch/CUDA; the Python stage installs only
# pinned user-space packages with --no-deps and never replaces torch.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_TELEMETRY=1
printf '\nPhase 5 GPU sweep/training — %s\n' "$(date -u +%FT%TZ)"
exec python scripts/phase5_gpu.py "$@"
