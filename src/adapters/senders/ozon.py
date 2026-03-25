import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.interfaces import ISender

logger = logging.getLogger(__name__)

BASE_URL = "https://api-seller.ozon.ru"


class OzonSender(ISender):
    def __init__(self, client_id: str, api_key: str) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Client-Id": client_id, "Api-Key": api_key},
            timeout=30.0,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def send_response(self, external_id: str, text: str) -> bool:
        comment_resp = self._client.post(
            "/v1/review/comment/create",
            json={"review_id": int(external_id), "text": text},
        )
        comment_resp.raise_for_status()

        status_resp = self._client.post(
            "/v1/review/change-status",
            json={"review_ids": [int(external_id)], "status": "PROCESSED"},
        )
        status_resp.raise_for_status()

        logger.info("Ozon: review %s answered and marked PROCESSED", external_id)
        return True
