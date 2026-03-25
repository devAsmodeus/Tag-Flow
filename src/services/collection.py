import logging

from src.domain.interfaces import ICollector, IItemRepository

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self, collectors: list[ICollector], item_repo: IItemRepository) -> None:
        self._collectors = collectors
        self._item_repo = item_repo

    def collect_all(self) -> int:
        total_new = 0
        for collector in self._collectors:
            try:
                items = collector.fetch_new_items()
                for item in items:
                    item_id = self._item_repo.insert(item)
                    if item_id is not None:
                        total_new += 1
            except Exception as e:
                logger.error(
                    "Collection failed for %s: %s",
                    collector.__class__.__name__,
                    e,
                    exc_info=True,
                )
        logger.info("Collection complete: %d new items", total_new)
        return total_new
