import logging
import uuid
from dataclasses import dataclass

from src.infrastructure.database import Database

logger = logging.getLogger(__name__)


@dataclass
class StageMetric:
    stage: str
    marketplace: str | None = None
    items_processed: int = 0
    items_failed: int = 0
    duration_ms: int = 0


class MetricsCollector:
    def __init__(self) -> None:
        self.run_id: str = uuid.uuid4().hex[:12]
        self._metrics: list[StageMetric] = []

    def record(
        self,
        stage: str,
        marketplace: str | None = None,
        processed: int = 0,
        failed: int = 0,
        duration_ms: int = 0,
    ) -> None:
        self._metrics.append(StageMetric(
            stage=stage,
            marketplace=marketplace,
            items_processed=processed,
            items_failed=failed,
            duration_ms=duration_ms,
        ))

    def flush(self, db: Database) -> None:
        if not self._metrics:
            return

        sql = """
            INSERT INTO pipeline_metrics
                (run_id, stage, marketplace, items_processed, items_failed, duration_ms)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        with db.cursor(dict_cursor=False) as cur:
            for m in self._metrics:
                cur.execute(sql, (
                    self.run_id, m.stage, m.marketplace,
                    m.items_processed, m.items_failed, m.duration_ms,
                ))

        logger.info("Flushed %d metrics for run %s", len(self._metrics), self.run_id)
        self._metrics.clear()
