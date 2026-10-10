#!/usr/bin/env bash
# Host entry point. All inference is local; no .env sourcing or model APIs.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
mkdir -p results/cache
exec > >(tee -a results/phase4.log) 2>&1
trap 'status=$?; printf "\nPhase 4 failed (exit %s, line %s). See %s/results/phase4.log\n" "$status" "$LINENO" "$ROOT"; exit "$status"' ERR
exec 9>results/cache/phase4.lock
if ! flock -n 9; then
    printf 'Phase 4 stopped: another runner holds results/cache/phase4.lock\n'
    exit 1
fi
PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    printf 'Phase 4 stopped: host interpreter missing: %s\n' "$PYTHON"
    exit 1
fi
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false
export HF_HUB_DISABLE_TELEMETRY=1
export RAG_EVAL_DATABASE_URL="${RAG_EVAL_DATABASE_URL:-postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval}"
printf '\nPhase 4 preflight and evaluation — %s\n' "$(date -u +%FT%TZ)"
# Only the new lightweight evaluation dependencies may need installation.
# Existing host sentence-transformers/torch/Postgres dependencies are reused.
if ! "$PYTHON" -c 'import numpy, jsonschema' 2>/dev/null; then
    "$PYTHON" -m pip install 'numpy>=1.26,<3' 'jsonschema>=4.23,<5'
fi
"$PYTHON" -m rag_service.evaluation.run --config configs/phase-4-evaluation.yaml "$@"
