#!/usr/bin/env bash
# Host stage: import GPU vectors into an isolated Postgres schema and evaluate gold.
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}")/..")"
cd "$ROOT"
PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
    printf 'Phase 5 eval stopped: missing host interpreter %s\n' "$PYTHON" >&2
    exit 1
fi
export PYTHONPATH="$ROOT/src:$ROOT${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1 TOKENIZERS_PARALLELISM=false HF_HUB_DISABLE_TELEMETRY=1
# Prefer the pod volume; an ordinary /workspace directory is not a mount.
HF_CACHE_ROOT="$ROOT"
if mountpoint -q /workspace 2>/dev/null; then
    HF_CACHE_ROOT=/workspace
fi
export HF_HOME="${HF_HOME:-$HF_CACHE_ROOT/.cache/huggingface}"
export RAG_EVAL_DATABASE_URL="${RAG_EVAL_DATABASE_URL:-postgresql://postgres:postgres@127.0.0.1:5432/evidence_rag_eval}"
mkdir -p .cache/phase5
exec 9>.cache/phase5/eval.lock
if ! flock -n 9; then
    printf 'Phase 5 eval stopped: another runner holds .cache/phase5/eval.lock\n' >&2
    exit 1
fi
printf '\nPhase 5 host evaluation — %s\n' "$(date -u +%FT%TZ)"
exec "$PYTHON" scripts/phase5_eval.py "$@"
