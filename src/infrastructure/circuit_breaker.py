import logging

import pybreaker

logger = logging.getLogger(__name__)


class _LogListener(pybreaker.CircuitBreakerListener):
    def state_change(self, cb: pybreaker.CircuitBreaker, old_state, new_state):
        logger.warning(
            "Circuit breaker '%s': %s -> %s",
            cb.name, old_state.name, new_state.name,
        )

    def failure(self, cb: pybreaker.CircuitBreaker, exc):
        logger.debug("Circuit breaker '%s' recorded failure: %s", cb.name, exc)


_listener = _LogListener()


def create_breaker(
    name: str, fail_max: int = 5, reset_timeout: int = 60
) -> pybreaker.CircuitBreaker:
    return pybreaker.CircuitBreaker(
        name=name,
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        listeners=[_listener],
    )


# Pre-configured breakers for each marketplace and LLM
wb_breaker = create_breaker("wildberries")
ozon_breaker = create_breaker("ozon")
yandex_breaker = create_breaker("yandex")
ollama_breaker = create_breaker("ollama", fail_max=3, reset_timeout=120)
