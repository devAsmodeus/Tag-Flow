import logging
import time

from src.infrastructure.database import Database
from src.infrastructure.metrics import MetricsCollector
from src.services.collection import CollectionService
from src.services.responding import ResponseService
from src.services.sending import SendingService
from src.services.tagging import TaggingService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(
        self,
        collection_service: CollectionService,
        tagging_service: TaggingService,
        response_service: ResponseService,
        sending_service: SendingService,
        db: Database,
    ) -> None:
        self._collection = collection_service
        self._tagging = tagging_service
        self._response = response_service
        self._sending = sending_service
        self._db = db

    def run(self) -> None:
        metrics = MetricsCollector()
        pipeline_start = time.time()
        logger.info("Pipeline run started", extra={"run_id": metrics.run_id})

        new_items = self._run_stage(
            "collection", metrics, self._collection.collect_all
        )

        tagged = self._run_stage(
            "tagging", metrics, self._tagging.tag_unprocessed
        )

        generated = self._run_stage(
            "responding", metrics, self._response.generate_responses
        )

        # sent = self._run_stage(
        #     "sending", metrics, self._sending.send_pending
        # )
        sent = 0

        metrics.flush(self._db)

        elapsed = int((time.time() - pipeline_start) * 1000)
        logger.info(
            "Pipeline completed: collected=%s, tagged=%s, generated=%s, sent=%s",
            new_items, tagged, generated, sent,
            extra={"run_id": metrics.run_id, "duration_ms": elapsed},
        )

    def _run_stage(self, stage: str, metrics: MetricsCollector, func) -> int:
        start = time.time()
        try:
            result = func()
            duration_ms = int((time.time() - start) * 1000)
            metrics.record(stage=stage, processed=result, duration_ms=duration_ms)
            logger.info("Stage %s: %d processed in %dms", stage, result, duration_ms)
            return result
        except Exception as e:
            duration_ms = int((time.time() - start) * 1000)
            metrics.record(stage=stage, failed=1, duration_ms=duration_ms)
            logger.error("Stage %s failed: %s", stage, e, exc_info=True)
            return 0
