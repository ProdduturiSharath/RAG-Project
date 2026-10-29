#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p .cache/phase8
exec 9>.cache/phase8/eval.lock
if ! flock -n 9; then
    printf 'Phase 8 stopped: another evaluation holds .cache/phase8/eval.lock\n' >&2
    exit 1
fi
exec > >(tee -a .cache/phase8/eval.log) 2>&1
trap 'printf "Phase 8 failed at line %s (exit %s)\n" "$LINENO" "$?" >&2' ERR
exec "$ROOT/.venv/bin/python" scripts/phase8_eval.py "$@"
