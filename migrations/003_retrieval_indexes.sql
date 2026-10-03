ALTER TABLE chunks ADD COLUMN IF NOT EXISTS identifier_vector tsvector
    GENERATED ALWAYS AS (
        to_tsvector('simple', regexp_replace(coalesce(text, ''), '[_./-]', ' ', 'g'))
    ) STORED;

CREATE INDEX IF NOT EXISTS chunks_identifier_vector_gin
    ON chunks USING gin(identifier_vector);

CREATE INDEX IF NOT EXISTS embeddings_hnsw_384_cosine
    ON embeddings USING hnsw ((embedding::vector(384)) vector_cosine_ops)
    WHERE dimensions = 384;
