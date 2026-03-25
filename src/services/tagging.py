import logging

from src.domain.interfaces import IItemRepository, ITagger, ITagRepository

logger = logging.getLogger(__name__)


class TaggingService:
    def __init__(
        self,
        tagger: ITagger,
        item_repo: IItemRepository,
        tag_repo: ITagRepository,
    ) -> None:
        self._tagger = tagger
        self._item_repo = item_repo
        self._tag_repo = tag_repo

    def tag_unprocessed(self) -> int:
        items = self._item_repo.get_untagged()
        tagged_count = 0

        for item in items:
            try:
                tag = self._tagger.tag(item)
                self._tag_repo.insert(tag)
                tagged_count += 1
                logger.debug(
                    "Tagged item %s: sentiment=%s, topic=%s",
                    item.external_id,
                    tag.sentiment,
                    tag.topic,
                )
            except Exception as e:
                logger.error(
                    "Tagging failed for item %s (id=%s): %s",
                    item.external_id,
                    item.id,
                    e,
                    exc_info=True,
                )

        logger.info("Tagging complete: %d/%d items tagged", tagged_count, len(items))
        return tagged_count
