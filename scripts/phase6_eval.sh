#!/usr/bin/env bash
# Evaluation-only cache; retrieval reads the preserved Phase 5 corpus/vector snapshot.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p .cache/phase6
exec 9>.cache/phase6/eval.lock
if ! flock -n 9; then
    printf 'Phase 6 stopped: another evaluation holds .cache/phase6/eval.lock\n' >&2
    exit 1
fi
exec > >(tee -a .cache/phase6/eval.log) 2>&1
trap 'printf "Phase 6 failed at line %s (exit %s)\n" "$LINENO" "$?" >&2' ERR
"$ROOT/.venv/bin/python" scripts/phase6_eval.py "$@"
