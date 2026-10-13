"""
Справочники (DIM_*) — что вообще бывает: площадки, модели, оценки.
Факт (FACT_LOT_SALE) — что произошло: одна машина выставили на торги.
"""

from __future__ import annotations

import enum
import uuid
from dataclasses import dataclass
from datetime import datetime


class SaleStatus(enum.StrEnum):
    SOLD = "sold"
    UNSOLD = "unsold"


@dataclass(frozen=True, slots=True)
class Auction:
    """DIM_AUCTION: аукционная площадка."""

    auction_id: int
    name: str
    city: str
    country: str
    trading_weekday: int # 0=Monday, 6=Sunday


@dataclass(frozen=True, slots=True)
class CarModel:
    """DIM_MODEL: модель автомобиля."""

    model_id: int
    brand: str
    model: str
    body_type: str
    fuel_type: str


@dataclass(frozen=True, slots=True)
class Grade:
    """DIM_GRADE: аукционная оценка состояния."""

    grade_id: int
    grade_code: str
    is_accident: bool


@dataclass(frozen=True, slots=True)
class LotSale:
    """FACT_LOT_SALE: результат торгов по одному лоту.

    Зерно: одна строка = одна машина, прошедшая торги на одной площадке в одну минуту.
    """

    lot_sale_id: uuid.UUID
    auction_id: int
    model_id: int
    grade_id: int
    event_ts: datetime
    lot_number: int
    manufacture_year: int
    mileage_km: int
    start_price_usd: int
    final_price_usd: int
    bids_count: int
    sale_status: SaleStatus
    is_anomaly: bool
