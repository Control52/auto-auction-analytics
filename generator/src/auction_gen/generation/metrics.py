"""Метрики одного лота: год выпуска, пробег, цены, ставки, продана ли машина.

Числа связаны между собой, как в жизни:
старше машина → больше пробег → ниже цена;
лучше оценка → выше цена и больше ставок;
мало ставок → машина не продана.
"""

import random
from dataclasses import dataclass
from datetime import datetime

from auction_gen.generation.catalog import GradeProfile, ModelProfile
from auction_gen.generation.seasonality import price_trend
from auction_gen.models import SaleStatus

# --- возраст ---
MAX_AGE_YEARS = 15  # самые старые машины на торгах
TYPICAL_AGE_YEARS = 4  # чаще всего продают машины такого возраста

# --- пробег ---
KM_PER_YEAR = 10_000  # сколько в среднем машина проезжает за год
MIN_MILEAGE_SHARE = 0.7  # кто-то ездит меньше: от 70% среднего пробега ...
MAX_MILEAGE_SHARE = 1.3  # ... до 130%
MILEAGE_STEP_KM = 100  # пробег округляем до 100 км

# --- цена ---
AGE_DISCOUNT_PER_YEAR = 0.12  # каждый год машина дешевеет на 12%
MILEAGE_DISCOUNT_PER_10K_KM = 0.02  # каждые 10 000 км пробега — ещё минус 2%
KM_IN_10K = 10_000
START_PRICE_MIN_SHARE = 0.6  # стартовая цена — от 60% рыночной ...
START_PRICE_MAX_SHARE = 0.8  # ... до 80%
FINAL_PRICE_MIN_SHARE = 0.9  # итоговая цена — от 90% рыночной ...
FINAL_PRICE_MAX_SHARE = 1.1  # ... до 110%
PRICE_STEP_USD = 100  # цены округляем до $100

# --- ставки ---
BASE_BIDS = 8  # среднее число ставок на машину с оценкой 4.5
MIN_BIDS_TO_SELL = 5  # меньше ставок — продавец не отдаёт машину, лот unsold
UNSOLD_FINAL_PRICE_USD = 0  # непроданная машина: денег никто не заплатил


@dataclass(frozen=True, slots=True)
class LotMetrics:
    """Все придуманные числа одного лота (без площадки, модели и оценки)."""

    manufacture_year: int
    mileage_km: int
    start_price_usd: int
    final_price_usd: int
    bids_count: int
    sale_status: SaleStatus


def round_to(value: float, step: int) -> int:
    """Округлить до шага: round_to(12_345, 100) = 12_300."""
    return int(round(value / step) * step)


def car_age(rng: random.Random) -> int:
    """Возраст машины в годах: от 0 до MAX_AGE_YEARS, чаще около TYPICAL_AGE_YEARS."""
    # треугольное распределение: чаще всего выпадает вершина «треугольника»
    return round(rng.triangular(0, MAX_AGE_YEARS, TYPICAL_AGE_YEARS))


def mileage_km(rng: random.Random, age: int) -> int:
    """Пробег: возраст × средний пробег за год × случайный разброс."""
    share = rng.uniform(MIN_MILEAGE_SHARE, MAX_MILEAGE_SHARE)
    return round_to(age * KM_PER_YEAR * share, MILEAGE_STEP_KM)


def market_price_usd(
    model: ModelProfile, grade: GradeProfile, age: int, mileage: int, at: datetime
) -> float:
    """Сколько машина «должна» стоить, без случайности."""
    age_factor = (1 - AGE_DISCOUNT_PER_YEAR) ** age
    mileage_factor = 1 - MILEAGE_DISCOUNT_PER_10K_KM * mileage / KM_IN_10K
    return model.base_price_usd * age_factor * mileage_factor * grade.price_factor * price_trend(at)


def bids_count(rng: random.Random, grade: GradeProfile) -> int:
    """Число ставок: чем лучше состояние машины, тем больше желающих."""
    mean = BASE_BIDS * grade.price_factor
    return rng.randint(0, round(2 * mean))  # от 0 до двойного среднего


def generate_metrics(
    rng: random.Random, at: datetime, model: ModelProfile, grade: GradeProfile
) -> LotMetrics:
    """Придумать все числа одного лота, проданного в момент at."""
    age = car_age(rng)
    mileage = mileage_km(rng, age)
    market = market_price_usd(model, grade, age, mileage, at)

    start_share = rng.uniform(START_PRICE_MIN_SHARE, START_PRICE_MAX_SHARE)
    start = round_to(market * start_share, PRICE_STEP_USD)
    bids = bids_count(rng, grade)

    if bids < MIN_BIDS_TO_SELL:
        status = SaleStatus.UNSOLD
        final = UNSOLD_FINAL_PRICE_USD
    else:
        status = SaleStatus.SOLD
        final_share = rng.uniform(FINAL_PRICE_MIN_SHARE, FINAL_PRICE_MAX_SHARE)
        final = round_to(market * final_share, PRICE_STEP_USD)

    return LotMetrics(
        manufacture_year=at.year - age,
        mileage_km=mileage,
        start_price_usd=start,
        final_price_usd=final,
        bids_count=bids,
        sale_status=status,
    )
