"""Повтор при ошибке: если запись в базу не удалась, попробовать ещё раз.
"""

import logging
import time
from collections.abc import Callable

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Все попытки кончились, а ошибка осталась."""


class RetryPolicy:
    """Сколько раз повторять и с какими паузами."""

    def __init__(
        self, max_attempts: int, base_delay: float, max_delay: float, backoff_factor: float
    ) -> None:
        self._max_attempts = max_attempts  
        self._base_delay = base_delay  
        self._max_delay = max_delay
        self._backoff_factor = backoff_factor

    def execute[T](self, fn: Callable[[], T]) -> T:
        attempt = 0
        while True:
            try:
                return fn()
            except Exception as exc:
                attempt += 1
                if attempt >= self._max_attempts:
                    raise RetryError(f"не удалось после {self._max_attempts} попыток") from exc
                delay = self._delay(attempt)
                logger.warning(
                    "Попытка %d/%d не удалась (%s), повтор через %.1f с",
                    attempt,
                    self._max_attempts,
                    exc,
                    delay,
                )
                time.sleep(delay)

    def _delay(self, attempt: int) -> float:
        return min(self._base_delay * self._backoff_factor ** (attempt - 1), self._max_delay)
