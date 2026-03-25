import logging

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.interfaces import ISender

logger = logging.getLogger(__name__)

BASE_URL = "https://api.partner.market.yandex.ru"


class YandexSender(ISender):
    def __init__(self, token: str, business_id: str) -> None:
        self._business_id = business_id
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Api-Key": token},
            timeout=30.0,
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def send_response(self, external_id: str, text: str) -> bool:
        response = self._client.post(
            f"/v2/businesses/{self._business_id}/goods-feedback/comments/update",
            json={"feedbackId": int(external_id), "comment": {"text": text}},
        )
        response.raise_for_status()
        logger.info("Yandex: feedback %s answered", external_id)
        return True
