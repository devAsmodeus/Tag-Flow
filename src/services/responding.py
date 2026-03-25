import logging

from src.domain.entities import Response
from src.domain.interfaces import IResponder, IResponseRepository, ITagRepository

logger = logging.getLogger(__name__)


class ResponseService:
    def __init__(
        self,
        responder: IResponder,
        tag_repo: ITagRepository,
        response_repo: IResponseRepository,
    ) -> None:
        self._responder = responder
        self._tag_repo = tag_repo
        self._response_repo = response_repo

    def generate_responses(self) -> int:
        pairs = self._tag_repo.get_items_needing_response()
        generated_count = 0

        for item, tag in pairs:
            try:
                text = self._responder.generate(item, tag)
                response = Response(
                    item_id=item.id,
                    response_text=text,
                    model_name=tag.model_name,
                )
                self._response_repo.insert(response)
                generated_count += 1
                logger.debug("Generated response for item %s", item.external_id)
            except Exception as e:
                logger.error(
                    "Response generation failed for item %s (id=%s): %s",
                    item.external_id,
                    item.id,
                    e,
                    exc_info=True,
                )

        logger.info("Response generation complete: %d/%d generated", generated_count, len(pairs))
        return generated_count
