import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.entities import Item
from src.domain.enums import ItemType, Marketplace
from src.domain.interfaces import ICollector

logger = logging.getLogger(__name__)

BASE_URL = "https://api.partner.market.yandex.ru"


class YandexCollector(ICollector):
    def __init__(
        self, token: str, business_id: str, breaker: pybreaker.CircuitBreaker, batch_size: int = 100
    ) -> None:
        self._business_id = business_id
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Api-Key": token},
            timeout=30.0,
        )
        self._breaker = breaker
        self._batch_size = batch_size

    def fetch_new_items(self) -> list[Item]:
        items = self._fetch_feedbacks()
        logger.info("Yandex: fetched %d items", len(items))
        return items

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _fetch_feedbacks(self) -> list[Item]:
        return self._breaker.call(self._do_fetch_feedbacks)

    def _do_fetch_feedbacks(self) -> list[Item]:
        response = self._client.post(
            f"/v2/businesses/{self._business_id}/goods-feedback",
            json={"reactionStatus": "NEED_REACTION"},
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for fb in data.get("result", {}).get("feedbacks", []):
            text = fb.get("comment", {}).get("text", "") or fb.get("text", "")
            if not text:
                continue
            items.append(Item(
                marketplace=Marketplace.YANDEX,
                item_type=ItemType.REVIEW,
                external_id=str(fb["feedbackId"]),
                text=text,
                product_id=str(fb.get("offer", {}).get("offerId", "")),
                author_name=fb.get("author", {}).get("name"),
                rating=fb.get("grade"),
                raw_json=fb,
            ))
        return items[: self._batch_size]
