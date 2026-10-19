"""Сборка продаж: один лот целиком и пачка лотов на один момент времени.

Здесь сходятся все части генератора: справочники (catalog), сезонность
(seasonality), числа лота (metrics) и выбросы (anomalies).
"""

import random
import uuid
from dataclasses import replace
from datetime import datetime

from auction_gen.generation.anomalies import AnomalyKind, AnomalyPolicy
from auction_gen.generation.catalog import Catalog
from auction_gen.generation.metrics import (
    MILEAGE_STEP_KM,
    MIN_BIDS_TO_SELL,
    PRICE_STEP_USD,
    LotMetrics,
    generate_metrics,
    round_to,
)
from auction_gen.generation.seasonality import activity
from auction_gen.models import Auction, LotSale, SaleStatus

MIN_BATCH_SIZE = 1  # даже глубокой ночью хотя бы один лот, чтобы поток не замирал
FIRST_LOT_NUMBER = 1  # с какого номера начинается нумерация лотов на площадке

# --- выбросы ---
PRICE_SPIKE_MIN = 4  # PRICE_SPIKE: итоговая цена в 4–7 раз выше стартовой
PRICE_SPIKE_MAX = 7  #   (обычно итог выше старта всего в 1.1–1.8 раза)
MILEAGE_ROLLBACK_MIN = 0.05  # MILEAGE_ROLLBACK: от настоящего пробега остаётся 5–15%
MILEAGE_ROLLBACK_MAX = 0.15
FULL_PRICE_GRADE_CODE = "4.5"  # ACCIDENT_FULL_PRICE: битую машину оценивают как целую с оценкой 4.5
BID_WAR_BIDS_MIN = 3  # BID_WAR: ставок в 3–5 раз больше обычного ...
BID_WAR_BIDS_MAX = 5
BID_WAR_PRICE_MIN = 1.8  # ... и итоговая цена в 1.8–2.2 раза выше стартовой
BID_WAR_PRICE_MAX = 2.2


class LotGenerator:
    """Придумывает продажи: по одной или пачкой."""

    def __init__(
        self, catalog: Catalog, anomaly_policy: AnomalyPolicy, rng: random.Random, lots_at_peak: int
    ) -> None:
        self._catalog = catalog
        self._anomaly_policy = anomaly_policy
        self._rng = rng
        self._lots_at_peak = lots_at_peak  # размер пачки, если бы все площадки были в пике

        # веса для выбора: популярная модель и частая оценка выпадают чаще
        self._model_weights = [p.popularity for p in catalog.model_profiles.values()]
        self._grade_weights = [p.frequency for p in catalog.grade_profiles.values()]
        self._accident_grades = [g for g in catalog.grades if g.is_accident]
        self._full_price_grade = next(
            g for g in catalog.grades if g.grade_code == FULL_PRICE_GRADE_CODE
        )

        # номер следующего лота на каждой площадке
        self._next_lot_number = {a.auction_id: FIRST_LOT_NUMBER for a in catalog.auctions}

    def _auction_weights(self, at: datetime) -> list[float]:
        """Вес площадки сейчас = её размер × её активность в этот момент."""
        weights = []
        for auction in self._catalog.auctions:
            profile = self._catalog.auction_profiles[auction.auction_id]
            weights.append(
                profile.volume
                * activity(at, profile.utc_offset_hours, auction.trading_weekday)
            )
        return weights

    def batch_size(self, at: datetime) -> int:
        """Сколько лотов в пачке: днём много, ночью мало."""
        total_volume = sum(p.volume for p in self._catalog.auction_profiles.values())
        # доля от максимума: 1.0 — все площадки в пике, 0.01 — почти все спят
        share = sum(self._auction_weights(at)) / total_volume
        return max(MIN_BATCH_SIZE, round(self._lots_at_peak * share))

    def generate_batch(self, at: datetime) -> list[LotSale]:
        """Пачка лотов на момент at. Площадки выбираются по весу: активные — чаще."""
        auctions = self._rng.choices(
            self._catalog.auctions, weights=self._auction_weights(at), k=self.batch_size(at)
        )
        return [self.generate_lot(at, auction) for auction in auctions]

    def generate_lot(self, at: datetime, auction: Auction) -> LotSale:
        """Один лот на площадке auction в момент at."""
        rng = self._rng
        model = rng.choices(self._catalog.models, weights=self._model_weights)[0]
        grade = rng.choices(self._catalog.grades, weights=self._grade_weights)[0]
        anomaly = self._anomaly_policy.decide()

        if anomaly == AnomalyKind.ACCIDENT_FULL_PRICE:
            # в базу пишем битую оценку, а цену считаем как у целой машины
            price_grade = self._full_price_grade
            grade = rng.choice(self._accident_grades)
        else:
            price_grade = grade

        metrics = generate_metrics(
            rng,
            at,
            self._catalog.model_profiles[model.model_id],
            self._catalog.grade_profiles[price_grade.grade_id],
        )
        metrics = self._apply_anomaly(metrics, anomaly)

        lot_number = self._next_lot_number[auction.auction_id]
        self._next_lot_number[auction.auction_id] += 1

        return LotSale(
            lot_sale_id=uuid.uuid4(),
            auction_id=auction.auction_id,
            model_id=model.model_id,
            grade_id=grade.grade_id,
            event_ts=at,
            lot_number=lot_number,
            manufacture_year=metrics.manufacture_year,
            mileage_km=metrics.mileage_km,
            start_price_usd=metrics.start_price_usd,
            final_price_usd=metrics.final_price_usd,
            bids_count=metrics.bids_count,
            sale_status=metrics.sale_status,
            is_anomaly=anomaly is not None,
        )

    def _apply_anomaly(self, m: LotMetrics, anomaly: AnomalyKind | None) -> LotMetrics:
        """Испортить числа лота согласно выбросу. replace — копия с изменёнными полями."""
        rng = self._rng
        if anomaly == AnomalyKind.PRICE_SPIKE:
            price = m.start_price_usd * rng.uniform(PRICE_SPIKE_MIN, PRICE_SPIKE_MAX)
            return replace(
                m,
                final_price_usd=round_to(price, PRICE_STEP_USD),
                bids_count=max(m.bids_count, MIN_BIDS_TO_SELL),  # раз продали — ставок хватило
                sale_status=SaleStatus.SOLD,
            )
        if anomaly == AnomalyKind.MILEAGE_ROLLBACK:
            mileage = m.mileage_km * rng.uniform(MILEAGE_ROLLBACK_MIN, MILEAGE_ROLLBACK_MAX)
            return replace(m, mileage_km=round_to(mileage, MILEAGE_STEP_KM))
        if anomaly == AnomalyKind.BID_WAR:
            bids_factor = rng.randint(BID_WAR_BIDS_MIN, BID_WAR_BIDS_MAX)
            bids = max(m.bids_count, MIN_BIDS_TO_SELL) * bids_factor
            price = m.start_price_usd * rng.uniform(BID_WAR_PRICE_MIN, BID_WAR_PRICE_MAX)
            return replace(
                m,
                final_price_usd=round_to(price, PRICE_STEP_USD),
                bids_count=bids,
                sale_status=SaleStatus.SOLD,
            )
        # ACCIDENT_FULL_PRICE уже учтён при выборе оценки, у обычного лота ничего не меняем
        return m
