#!/usr/bin/env bash
# Phase 7 is local-only; database studies report unavailable when no PostgreSQL is provisioned.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p .cache/phase7
exec 9>.cache/phase7/eval.lock
if ! flock -n 9; then
    printf 'Phase 7 stopped: another evaluation holds .cache/phase7/eval.lock\n' >&2
    exit 1
fi
exec > >(tee -a .cache/phase7/eval.log) 2>&1
trap 'printf "Phase 7 failed at line %s (exit %s)\n" "$LINENO" "$?" >&2' ERR
exec "$ROOT/.venv/bin/python" scripts/phase7_eval.py "$@"
