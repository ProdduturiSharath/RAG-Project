CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS schema_migrations (
    version text PRIMARY KEY,
    applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS documents (
    document_id text PRIMARY KEY,
    title text,
    source_uri text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS document_versions (
    id bigserial PRIMARY KEY,
    document_id text NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
    product_version text NOT NULL,
    revision integer NOT NULL CHECK (revision > 0),
    content_hash text NOT NULL,
    status text NOT NULL CHECK (status IN ('building', 'active', 'superseded', 'deleted')),
    parser_config_hash text NOT NULL,
    chunker_config_hash text NOT NULL,
    embedder_id text NOT NULL,
    source_uri text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    activated_at timestamptz,
    deleted_at timestamptz,
    UNIQUE (document_id, product_version, revision)
);

CREATE UNIQUE INDEX IF NOT EXISTS document_versions_one_active
    ON document_versions (document_id, product_version)
    WHERE status = 'active';

CREATE INDEX IF NOT EXISTS document_versions_scope_status
    ON document_versions (document_id, product_version, status);

CREATE TABLE IF NOT EXISTS sections (
    id bigserial PRIMARY KEY,
    document_version_id bigint NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    section_key text NOT NULL,
    parent_id bigint REFERENCES sections(id) ON DELETE SET NULL,
    parent_key text,
    heading_path jsonb NOT NULL DEFAULT '[]'::jsonb,
    lineage_key text NOT NULL,
    text text NOT NULL,
    page integer,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    ordinal integer NOT NULL CHECK (ordinal >= 0),
    UNIQUE (document_version_id, section_key)
);

CREATE INDEX IF NOT EXISTS sections_lineage_key ON sections(lineage_key);

CREATE TABLE IF NOT EXISTS chunks (
    id bigserial PRIMARY KEY,
    document_version_id bigint NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    section_id bigint NOT NULL REFERENCES sections(id) ON DELETE CASCADE,
    chunk_key text NOT NULL,
    parent_id bigint REFERENCES chunks(id) ON DELETE SET NULL,
    parent_key text,
    kind text NOT NULL CHECK (kind IN ('text', 'table', 'code')),
    text text NOT NULL,
    token_count integer NOT NULL CHECK (token_count >= 0),
    page integer,
    content_hash text NOT NULL,
    source_uri text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    search_vector tsvector GENERATED ALWAYS AS (to_tsvector('simple', coalesce(text, ''))) STORED,
    UNIQUE (document_version_id, chunk_key)
);

CREATE INDEX IF NOT EXISTS chunks_version_id ON chunks(document_version_id);
CREATE INDEX IF NOT EXISTS chunks_content_hash ON chunks(content_hash);
CREATE INDEX IF NOT EXISTS chunks_search_vector_gin ON chunks USING gin(search_vector);

CREATE TABLE IF NOT EXISTS embeddings (
    content_hash text NOT NULL,
    embedder_id text NOT NULL,
    embedding vector,
    sparse_vector jsonb NOT NULL DEFAULT '{}'::jsonb,
    dimensions integer,
    created_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (content_hash, embedder_id),
    CHECK (dimensions IS NULL OR dimensions > 0)
);

CREATE TABLE IF NOT EXISTS chunk_embeddings (
    document_version_id bigint NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    chunk_id bigint NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
    content_hash text NOT NULL,
    embedder_id text NOT NULL,
    PRIMARY KEY (document_version_id, chunk_id, embedder_id),
    FOREIGN KEY (content_hash, embedder_id)
        REFERENCES embeddings(content_hash, embedder_id)
        ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS chunk_embeddings_lookup
    ON chunk_embeddings(embedder_id, content_hash);

CREATE TABLE IF NOT EXISTS acl (
    id bigserial PRIMARY KEY,
    document_version_id bigint NOT NULL REFERENCES document_versions(id) ON DELETE CASCADE,
    is_public boolean NOT NULL DEFAULT false,
    principal text,
    group_name text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    CHECK (is_public OR principal IS NOT NULL OR group_name IS NOT NULL),
    UNIQUE (document_version_id, is_public, principal, group_name)
);

CREATE INDEX IF NOT EXISTS acl_principal_lookup ON acl(principal);
CREATE INDEX IF NOT EXISTS acl_group_lookup ON acl(group_name);

CREATE TABLE IF NOT EXISTS jobs (
    id uuid PRIMARY KEY,
    kind text NOT NULL,
    payload jsonb NOT NULL,
    status text NOT NULL CHECK (status IN ('queued', 'running', 'succeeded', 'failed')),
    attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
    error text,
    created_at timestamptz NOT NULL DEFAULT now(),
    started_at timestamptz,
    finished_at timestamptz,
    locked_at timestamptz
);

CREATE INDEX IF NOT EXISTS jobs_claim_queue
    ON jobs(status, created_at)
    WHERE status = 'queued';

CREATE TABLE IF NOT EXISTS query_traces (
    id uuid PRIMARY KEY,
    query text NOT NULL,
    requester text,
    product_version text,
    stages jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO schema_migrations(version)
VALUES ('001_initial')
ON CONFLICT (version) DO NOTHING;
