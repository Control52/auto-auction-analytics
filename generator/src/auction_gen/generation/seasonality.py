"""Сезонность: когда торгов больше, когда меньше, и как цены растут со временем.

Всё здесь — простые функции от времени, без случайности:
подставил время — получил число-множитель.
"""

import math
from datetime import UTC, datetime, timedelta

PEAK_HOUR = 13.0  # час пика торгов
PEAK_WIDTH_HOURS = 2.5  # ширина пика: торги идут примерно с 9 до 17
NIGHT_LEVEL = 0.05  # ночью торги почти стоят, но онлайн-лоты всё равно бывают

TRADING_DAY_LEVEL = 1.0  # свой день торгов площадки
OTHER_WEEKDAY_LEVEL = 0.3  # будни, но не свой день
WEEKEND_LEVEL = 0.1  # выходные
SATURDAY = 5  # datetime.weekday(): 0 = понедельник ... 5 = суббота, 6 = воскресенье

TREND_START = datetime(2026, 1, 1, tzinfo=UTC)  # от этой даты считается рост цен (по UTC)
YEARLY_PRICE_GROWTH = 0.05  # +5% в год

MINUTES_PER_HOUR = 60
DAYS_PER_YEAR = 365.25


def daily_factor(local: datetime) -> float:
    """Активность внутри дня: 1.0 в час пика, плавно спадает к утру и вечеру."""
    hour = local.hour + local.minute / MINUTES_PER_HOUR
    # «колокол» (кривая Гаусса) с вершиной в PEAK_HOUR
    peak = math.exp(-((hour - PEAK_HOUR) ** 2) / (2 * PEAK_WIDTH_HOURS**2))
    return max(NIGHT_LEVEL, peak)


def weekly_factor(local: datetime, trading_weekday: int) -> float:
    """Активность внутри недели: свой день торгов, другие будни или выходные."""
    if local.weekday() == trading_weekday:
        return TRADING_DAY_LEVEL
    if local.weekday() >= SATURDAY:
        return WEEKEND_LEVEL
    return OTHER_WEEKDAY_LEVEL


def activity(at_utc: datetime, utc_offset_hours: int, trading_weekday: int) -> float:
    """Насколько активна площадка в момент at_utc: число от 0 до 1."""
    local = at_utc + timedelta(hours=utc_offset_hours)  # местное время площадки
    return daily_factor(local) * weekly_factor(local, trading_weekday)


def price_trend(at: datetime) -> float:
    """Множитель цены из-за роста рынка: 1.0 на TREND_START, дальше растёт."""
    years = (at - TREND_START).days / DAYS_PER_YEAR
    return 1 + YEARLY_PRICE_GROWTH * years
