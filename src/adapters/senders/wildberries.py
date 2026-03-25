import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.interfaces import ISender

logger = logging.getLogger(__name__)

BASE_URL = "https://feedbacks-api.wildberries.ru"


class WildberriesSender(ISender):
    def __init__(self, token: str) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": token},
            timeout=30.0,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def send_response(self, external_id: str, text: str) -> bool:
        if self._send_feedback_answer(external_id, text):
            return True
        return self._send_question_answer(external_id, text)

    def _send_feedback_answer(self, external_id: str, text: str) -> bool:
        try:
            response = self._client.patch(
                "/api/v1/feedbacks/answer",
                json={"id": external_id, "answer": {"text": text}},
            )
            if response.status_code == 200:
                logger.info("WB: feedback %s answered", external_id)
                return True
        except httpx.HTTPError as e:
            logger.debug("WB feedback answer failed for %s: %s", external_id, e)
        return False

    def _send_question_answer(self, external_id: str, text: str) -> bool:
        try:
            response = self._client.patch(
                "/api/v1/questions",
                json={"id": external_id, "answer": {"text": text}},
            )
            if response.status_code == 200:
                logger.info("WB: question %s answered", external_id)
                return True
        except httpx.HTTPError as e:
            logger.debug("WB question answer failed for %s: %s", external_id, e)
        return False
