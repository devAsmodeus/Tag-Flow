import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from src.domain.entities import Item
from src.domain.enums import ItemType, Marketplace
from src.domain.interfaces import ICollector

logger = logging.getLogger(__name__)

BASE_URL = "https://feedbacks-api.wildberries.ru"


class WildberriesCollector(ICollector):
    def __init__(
        self, token: str, breaker: pybreaker.CircuitBreaker, batch_size: int = 100
    ) -> None:
        self._client = httpx.Client(
            base_url=BASE_URL,
            headers={"Authorization": token},
            timeout=30.0,
        )
        self._breaker = breaker
        self._batch_size = batch_size

    def fetch_new_items(self) -> list[Item]:
        items: list[Item] = []
        items.extend(self._fetch_feedbacks())
        items.extend(self._fetch_questions())
        logger.info("WB: fetched %d items", len(items))
        return items

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _fetch_feedbacks(self) -> list[Item]:
        return self._breaker.call(self._do_fetch_feedbacks)

    def _do_fetch_feedbacks(self) -> list[Item]:
        response = self._client.get(
            "/api/v1/feedbacks",
            params={
                "isAnswered": "false",
                "take": min(self._batch_size, 1000),
                "skip": 0,
            },
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for fb in data.get("data", {}).get("feedbacks", []):
            text = fb.get("text", "")
            if not text:
                continue
            items.append(Item(
                marketplace=Marketplace.WB,
                item_type=ItemType.REVIEW,
                external_id=str(fb["id"]),
                text=text,
                product_id=str(fb.get("productDetails", {}).get("nmId", "")),
                author_name=fb.get("userName"),
                rating=fb.get("productValuation"),
                raw_json=fb,
            ))
        return items

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=5, max=60),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def _fetch_questions(self) -> list[Item]:
        return self._breaker.call(self._do_fetch_questions)

    def _do_fetch_questions(self) -> list[Item]:
        response = self._client.get(
            "/api/v1/questions",
            params={
                "isAnswered": "false",
                "take": min(self._batch_size, 1000),
                "skip": 0,
            },
        )
        response.raise_for_status()
        data = response.json()

        items = []
        for q in data.get("data", {}).get("questions", []):
            text = q.get("text", "")
            if not text:
                continue
            items.append(Item(
                marketplace=Marketplace.WB,
                item_type=ItemType.QUESTION,
                external_id=str(q["id"]),
                text=text,
                product_id=str(q.get("productDetails", {}).get("nmId", "")),
                author_name=q.get("userName"),
                raw_json=q,
            ))
        return items
