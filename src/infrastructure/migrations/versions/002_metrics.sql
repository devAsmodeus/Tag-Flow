CREATE TABLE IF NOT EXISTS pipeline_metrics (
    id              BIGSERIAL PRIMARY KEY,
    run_id          VARCHAR(36) NOT NULL,
    stage           VARCHAR(50) NOT NULL,
    marketplace     VARCHAR(20),
    items_processed INT NOT NULL DEFAULT 0,
    items_failed    INT NOT NULL DEFAULT 0,
    duration_ms     INT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_metrics_run_id ON pipeline_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_metrics_created ON pipeline_metrics(created_at DESC);
