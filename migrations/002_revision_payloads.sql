ALTER TABLE chunks ADD COLUMN payload jsonb NOT NULL DEFAULT '{}'::jsonb;
-- A private empty policy needs a deny-all sentinel, distinct from no policy.
ALTER TABLE acl DROP CONSTRAINT acl_check;
ALTER TABLE jobs ADD COLUMN result jsonb;
ALTER TABLE jobs ADD COLUMN lease_token uuid;
ALTER TABLE embeddings ADD CONSTRAINT embedding_dimensions_match
    CHECK (embedding IS NOT NULL AND vector_dims(embedding) = dimensions);
