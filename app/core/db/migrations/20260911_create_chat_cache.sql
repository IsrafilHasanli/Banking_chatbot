CREATE TABLE IF NOT EXISTS chat_cache (
    id SERIAL PRIMARY KEY,
    cache_key VARCHAR(64) NOT NULL,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT uq_chat_cache_cache_key UNIQUE (cache_key)
);

CREATE INDEX IF NOT EXISTS ix_chat_cache_cache_key ON chat_cache (cache_key);
CREATE INDEX IF NOT EXISTS ix_chat_cache_user_id ON chat_cache (user_id);
CREATE INDEX IF NOT EXISTS ix_chat_cache_expires_at ON chat_cache (expires_at);
