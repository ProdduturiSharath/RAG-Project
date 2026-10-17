#!/usr/bin/env bash
# Host stage: materialize train-only data and generate/filter query candidates.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    printf 'Phase 5 prepare stopped: missing host interpreter %s\n' "$PYTHON" >&2
    exit 1
fi
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_TELEMETRY=1
mkdir -p .cache/phase5 data/train
exec 9>.cache/phase5/prepare.lock
if ! flock -n 9; then
    printf 'Phase 5 prepare stopped: another runner holds .cache/phase5/prepare.lock\n' >&2
    exit 1
fi
printf '\nPhase 5 host prepare — %s\n' "$(date -u +%FT%TZ)"
exec "$PYTHON" scripts/phase5_prepare.py "$@"
