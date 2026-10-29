#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(realpath -- "$(dirname -- "${BASH_SOURCE[0]}" )/..")"
cd "$ROOT"
if [[ -f .env ]]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
fi

if ! command -v docker >/dev/null 2>&1; then
    printf 'Phase 8 demo requires Docker Compose; docker is unavailable.\n' >&2
    exit 2
fi
if ! docker compose version >/dev/null 2>&1; then
    printf 'Phase 8 demo requires Docker Compose v2.\n' >&2
    exit 2
fi

export COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-evidence-rag-phase8-demo}"
export POSTGRES_DB="evidence_rag_demo"
export RAG_DEMO_VOLUME="${RAG_DEMO_VOLUME:-evidence_rag_demo_pgdata}"
export RAG_DEMO_POSTGRES_PORT="${RAG_DEMO_POSTGRES_PORT:-5432}"
export RAG_DEMO_API_PORT="${RAG_DEMO_API_PORT:-8000}"
export RAG_DEMO_UI_PORT="${RAG_DEMO_UI_PORT:-8501}"
: "${POSTGRES_PASSWORD:?copy .env.example to .env and set POSTGRES_PASSWORD}"
: "${RAG_JWT_SECRET:?copy .env.example to .env and set RAG_JWT_SECRET}"

if docker volume inspect "$RAG_DEMO_VOLUME" >/dev/null 2>&1; then
    printf 'Existing demo volume found: %s\n' "$RAG_DEMO_VOLUME"
    printf 'The seed script will inspect the database and refuse non-empty data.\n'
fi

docker compose up -d postgres
until docker compose exec -T postgres pg_isready -U "${POSTGRES_USER:-postgres}" -d "$POSTGRES_DB" >/dev/null 2>&1; do
    sleep 1
done

demo_url="postgresql://${POSTGRES_USER:-postgres}:${POSTGRES_PASSWORD}@127.0.0.1:${RAG_DEMO_POSTGRES_PORT}/${POSTGRES_DB}"
"$ROOT/.venv/bin/python" scripts/seed_demo.py --create --database-url "$demo_url"
docker compose up -d api worker ui
printf 'Phase 8 demo is running: API http://127.0.0.1:%s and UI http://127.0.0.1:%s\n' \
    "$RAG_DEMO_API_PORT" "$RAG_DEMO_UI_PORT"
