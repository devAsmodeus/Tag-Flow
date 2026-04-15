DO $$ BEGIN
    CREATE TYPE emotion_enum AS ENUM (
        'anger', 'disappointment', 'frustration',
        'surprise', 'gratitude', 'indifference'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE intent_enum AS ENUM (
        'return', 'exchange', 'complaint',
        'info', 'gratitude'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE response_tone_enum AS ENUM (
        'apology', 'gratitude', 'clarification', 'informational'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE tags
    ADD COLUMN IF NOT EXISTS subtopic       VARCHAR(200),
    ADD COLUMN IF NOT EXISTS emotion        emotion_enum,
    ADD COLUMN IF NOT EXISTS product_issue  VARCHAR(200),
    ADD COLUMN IF NOT EXISTS intent         intent_enum,
    ADD COLUMN IF NOT EXISTS keywords       TEXT[],
    ADD COLUMN IF NOT EXISTS response_tone  response_tone_enum;
