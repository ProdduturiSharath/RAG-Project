ALTER TABLE query_traces
    ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE query_traces
    ADD COLUMN IF NOT EXISTS generation_mode text NOT NULL DEFAULT 'verified';
ALTER TABLE query_traces
    ADD COLUMN IF NOT EXISTS cost_usd numeric(18, 8) NOT NULL DEFAULT 0;
ALTER TABLE query_traces
    ADD COLUMN IF NOT EXISTS latency_ms double precision;

ALTER TABLE query_traces
    DROP CONSTRAINT IF EXISTS query_traces_generation_mode_check;
ALTER TABLE query_traces
    ADD CONSTRAINT query_traces_generation_mode_check
    CHECK (generation_mode IN ('extractive', 'verified', 'unverified'));
ALTER TABLE query_traces
    DROP CONSTRAINT IF EXISTS query_traces_cost_usd_check;
ALTER TABLE query_traces
    ADD CONSTRAINT query_traces_cost_usd_check CHECK (cost_usd >= 0);

INSERT INTO schema_migrations(version)
VALUES ('004_trace_observability')
ON CONFLICT (version) DO NOTHING;
