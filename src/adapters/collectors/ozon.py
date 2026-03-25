import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.entities import Item
from src.domain.enums import ItemType, Marketplace
from src.domain.interfaces import ICollector

logger = logging.getLogger(__name__)

BASE_URL = "https://api-seller.ozon.ru"


class OzonCollector(ICollector):
    def __init__(
        self, client_id: str, api_key: str, breaker: pybreaker.CircuitBreaker, batch_size: int = 100
    ) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Client-Id": client_id, "Api-Key": api_key},
            timeout=30.0,
        )
        self._breaker = breaker
        self._batch_size = batch_size

    def fetch_new_items(self) -> list[Item]:
        items = self._fetch_reviews()
        logger.info("Ozon: fetched %d items", len(items))
        return items

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _fetch_reviews(self) -> list[Item]:
        return self._breaker.call(self._do_fetch_reviews)

    def _do_fetch_reviews(self) -> list[Item]:
        response = self._client.post(
            "/v1/review/list",
            json={
                "status": "UNPROCESSED",
                "limit": min(self._batch_size, 100),
                "sort_dir": "ASC",
            },
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for review in data.get("reviews", []):
            text = review.get("comment", {}).get("text", "")
            if not text:
                continue
            items.append(Item(
                marketplace=Marketplace.OZON,
                item_type=ItemType.REVIEW,
                external_id=str(review["id"]),
                text=text,
                product_id=str(review.get("sku", "")),
                author_name=review.get("author_name"),
                rating=review.get("comment", {}).get("rating"),
                raw_json=review,
            ))
        return items
