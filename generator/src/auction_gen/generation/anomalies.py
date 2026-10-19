"""Редкие выбросы: лоты, которые выбиваются из нормы.
"""

import enum
import random


class AnomalyKind(enum.StrEnum):

    PRICE_SPIKE = "price_spike"  # цена в несколько раз выше нормы
    MILEAGE_ROLLBACK = "mileage_rollback"  # скрученный пробег: старая машина с пробегом новой
    ACCIDENT_FULL_PRICE = "accident_full_price"  # битая машина (R/RA) по цене целой
    BID_WAR = "bid_war"  # «война ставок»: ставок в разы больше обычного


class AnomalyPolicy:
    def __init__(self, probability: float, rng: random.Random) -> None:
        self._probability = probability
        self._rng = rng

    def decide(self) -> AnomalyKind | None:
        if self._rng.random() >= self._probability:
            return None
        return self._rng.choice(list(AnomalyKind))
