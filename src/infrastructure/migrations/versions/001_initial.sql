DO $$ BEGIN
    CREATE TYPE marketplace_enum AS ENUM ('wb', 'ozon', 'yandex');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE item_type_enum AS ENUM ('review', 'question');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE sentiment_enum AS ENUM ('positive', 'negative', 'neutral');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE urgency_enum AS ENUM ('low', 'medium', 'high');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE send_status_enum AS ENUM ('pending', 'sent', 'failed');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

CREATE TABLE IF NOT EXISTS items (
    id              BIGSERIAL PRIMARY KEY,
    marketplace     marketplace_enum NOT NULL,
    item_type       item_type_enum NOT NULL,
    external_id     VARCHAR(255) NOT NULL,
    product_id      VARCHAR(255),
    author_name     VARCHAR(255),
    rating          SMALLINT,
    text            TEXT NOT NULL,
    raw_json        JSONB,
    fetched_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(marketplace, external_id)
);

CREATE TABLE IF NOT EXISTS tags (
    id                BIGSERIAL PRIMARY KEY,
    item_id           BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    sentiment         sentiment_enum,
    topic             VARCHAR(100),
    urgency           urgency_enum DEFAULT 'low',
    requires_response BOOLEAN NOT NULL DEFAULT TRUE,
    extra             JSONB,
    model_name        VARCHAR(100),
    tagged_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(item_id)
);

CREATE TABLE IF NOT EXISTS responses (
    id              BIGSERIAL PRIMARY KEY,
    item_id         BIGINT NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    response_text   TEXT NOT NULL,
    model_name      VARCHAR(100),
    generated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(item_id)
);

CREATE TABLE IF NOT EXISTS send_log (
    id              BIGSERIAL PRIMARY KEY,
    response_id     BIGINT NOT NULL REFERENCES responses(id) ON DELETE CASCADE,
    marketplace     marketplace_enum NOT NULL,
    external_id     VARCHAR(255) NOT NULL,
    status          send_status_enum NOT NULL DEFAULT 'pending',
    error_message   TEXT,
    attempts        SMALLINT NOT NULL DEFAULT 0,
    sent_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_send_log_retryable
    ON send_log(status) WHERE status = 'failed';
