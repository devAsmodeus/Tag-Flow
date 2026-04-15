DO $$ BEGIN
    CREATE TYPE responsibility_enum AS ENUM (
        'seller', 'marketplace', 'both', 'none'
    );
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

ALTER TABLE tags
    ADD COLUMN IF NOT EXISTS responsibility responsibility_enum;
