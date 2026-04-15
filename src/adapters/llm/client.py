import logging

import httpx
import pybreaker
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        breaker: pybreaker.CircuitBreaker | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = httpx.Client(timeout=httpx.Timeout(180.0, connect=10.0))
        self._breaker = breaker

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=10, max=30),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def generate(self, model: str, prompt: str, timeout: float = 120.0) -> str:
        if self._breaker:
            return self._breaker.call(self._do_generate, model, prompt, timeout)
        return self._do_generate(model, prompt, timeout)

    def _do_generate(self, model: str, prompt: str, timeout: float) -> str:
        response = self._client.post(
            f"{self._base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False,
                "think": False,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["response"]

    @retry(
        stop=stop_after_attempt(2),
        wait=wait_exponential(multiplier=10, max=30),
        retry=retry_if_exception_type((httpx.ConnectError, httpx.TimeoutException)),
    )
    def chat(self, model: str, messages: list[dict], timeout: float = 180.0) -> str:
        if self._breaker:
            return self._breaker.call(self._do_chat, model, messages, timeout)
        return self._do_chat(model, messages, timeout)

    def _do_chat(self, model: str, messages: list[dict], timeout: float) -> str:
        response = self._client.post(
            f"{self._base_url}/api/chat",
            json={"model": model, "messages": messages, "stream": False},
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()["message"]["content"]

    def close(self) -> None:
        self._client.close()
