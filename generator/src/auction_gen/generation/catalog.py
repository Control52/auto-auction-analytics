"""Справочники: какие бывают площадки, модели и оценки.

Для каждой записи справочника рядом лежит «профиль» — числа, которые нужны
только генератору, чтобы данные выглядели правдоподобно. В базу профили не пишутся.
"""

from dataclasses import dataclass

from auction_gen.models import Auction, CarModel, Grade


@dataclass(frozen=True, slots=True)
class AuctionProfile:
    utc_offset_hours: int  # часовой пояс: торги идут днём по местному времени
    volume: int  # размер площадки: чем больше, тем больше лотов


@dataclass(frozen=True, slots=True)
class ModelProfile:
    base_price_usd: int  # цена почти новой машины в хорошем состоянии
    popularity: int  # как часто модель встречается на торгах


@dataclass(frozen=True, slots=True)
class GradeProfile:
    price_factor: float  # множитель цены: 4.5 = 1.0, лучше — дороже, хуже — дешевле
    frequency: int  # как часто встречается оценка


# name, city, country, trading_weekday, utc_offset_hours, volume
_AUCTIONS = [
    ("USS Tokyo", "Токио", "Япония", 3, 9, 10),
    ("USS Nagoya", "Нагоя", "Япония", 3, 9, 8),
    ("TAA Yokohama", "Иокогама", "Япония", 1, 9, 5),
    ("JU Aichi", "Нагоя", "Япония", 5, 9, 4),
    ("HAA Kobe", "Кобе", "Япония", 2, 9, 4),
    ("Hyundai Glovis", "Соннам", "Южная Корея", 0, 9, 6),
    ("Lotte Auto Auction", "Ансон", "Южная Корея", 2, 9, 4),
    ("Manheim Pennsylvania", "Манхайм", "США", 1, -5, 8),
    ("Copart Dallas", "Даллас", "США", 3, -6, 6),
    ("IAA Los Angeles", "Лос-Анджелес", "США", 4, -8, 5),
    ("BCA Blackbushe", "Блэкбуш", "Великобритания", 0, 0, 5),
]

# brand, model, body_type, fuel_type, base_price_usd, popularity
_MODELS = [
    ("Toyota", "Prius", "Хэтчбек", "Гибрид", 28_000, 10),
    ("Toyota", "Aqua", "Хэтчбек", "Гибрид", 20_000, 8),
    ("Toyota", "Corolla", "Седан", "Бензин", 22_000, 9),
    ("Toyota", "Camry", "Седан", "Бензин", 30_000, 7),
    ("Toyota", "RAV4", "Кроссовер", "Гибрид", 33_000, 8),
    ("Toyota", "Land Cruiser", "Внедорожник", "Дизель", 85_000, 4),
    ("Toyota", "Alphard", "Минивэн", "Бензин", 55_000, 5),
    ("Toyota", "Hiace", "Фургон", "Дизель", 35_000, 4),
    ("Honda", "Fit", "Хэтчбек", "Бензин", 17_000, 8),
    ("Honda", "Vezel", "Кроссовер", "Гибрид", 25_000, 7),
    ("Honda", "Freed", "Минивэн", "Гибрид", 24_000, 6),
    ("Honda", "Civic", "Хэтчбек", "Бензин", 25_000, 5),
    ("Honda", "CR-V", "Кроссовер", "Бензин", 32_000, 5),
    ("Nissan", "Note", "Хэтчбек", "Гибрид", 19_000, 8),
    ("Nissan", "X-Trail", "Кроссовер", "Бензин", 30_000, 6),
    ("Nissan", "Serena", "Минивэн", "Гибрид", 28_000, 6),
    ("Nissan", "Leaf", "Хэтчбек", "Электро", 30_000, 3),
    ("Mazda", "CX-5", "Кроссовер", "Бензин", 29_000, 6),
    ("Mazda", "3", "Хэтчбек", "Бензин", 23_000, 4),
    ("Subaru", "Forester", "Кроссовер", "Бензин", 29_000, 5),
    ("Subaru", "Impreza", "Хэтчбек", "Бензин", 22_000, 4),
    ("Mitsubishi", "Delica", "Минивэн", "Дизель", 38_000, 3),
    ("Mitsubishi", "Outlander", "Кроссовер", "Гибрид", 35_000, 3),
    ("Suzuki", "Jimny", "Внедорожник", "Бензин", 20_000, 5),
    ("Suzuki", "Swift", "Хэтчбек", "Бензин", 15_000, 5),
    ("Lexus", "RX", "Кроссовер", "Гибрид", 60_000, 4),
    ("Lexus", "LX", "Внедорожник", "Бензин", 95_000, 2),
    ("Hyundai", "Accent", "Седан", "Бензин", 16_000, 5),
    ("Hyundai", "Tucson", "Кроссовер", "Бензин", 28_000, 5),
    ("Hyundai", "Santa Fe", "Кроссовер", "Дизель", 34_000, 4),
    ("Kia", "Rio", "Седан", "Бензин", 16_000, 5),
    ("Kia", "Sportage", "Кроссовер", "Бензин", 28_000, 5),
    ("Kia", "Carnival", "Минивэн", "Дизель", 38_000, 3),
    ("Genesis", "G80", "Седан", "Бензин", 55_000, 2),
    ("Ford", "F-150", "Пикап", "Бензин", 45_000, 6),
    ("Chevrolet", "Tahoe", "Внедорожник", "Бензин", 60_000, 3),
    ("Tesla", "Model 3", "Седан", "Электро", 40_000, 5),
    ("BMW", "X5", "Кроссовер", "Дизель", 65_000, 4),
    ("Mercedes-Benz", "E-Class", "Седан", "Бензин", 60_000, 4),
    ("Volkswagen", "Golf", "Хэтчбек", "Бензин", 27_000, 5),
]

# grade_code, is_accident, price_factor, frequency
_GRADES = [
    ("S", False, 1.25, 2),
    ("6", False, 1.20, 3),
    ("5", False, 1.12, 6),
    ("4.5", False, 1.00, 20),
    ("4", False, 0.92, 25),
    ("3.5", False, 0.82, 18),
    ("3", False, 0.72, 10),
    ("2", False, 0.55, 3),
    ("1", False, 0.40, 2),
    ("R", True, 0.60, 7),
    ("RA", True, 0.70, 4),
]


class Catalog:
    """Все справочники и их профили. Номера (id) начинаются с 1."""

    def __init__(self) -> None:
        self.auctions: list[Auction] = []
        self.models: list[CarModel] = []
        self.grades: list[Grade] = []

        # профиль по номеру записи: auction_profiles[1] — профиль площадки № 1
        self.auction_profiles: dict[int, AuctionProfile] = {}
        self.model_profiles: dict[int, ModelProfile] = {}
        self.grade_profiles: dict[int, GradeProfile] = {}

        for i, (name, city, country, weekday, utc, volume) in enumerate(_AUCTIONS, start=1):
            self.auctions.append(Auction(i, name, city, country, weekday))
            self.auction_profiles[i] = AuctionProfile(utc, volume)

        for i, (brand, model, body, fuel, price, popularity) in enumerate(_MODELS, start=1):
            self.models.append(CarModel(i, brand, model, body, fuel))
            self.model_profiles[i] = ModelProfile(price, popularity)

        for i, (code, is_accident, price_factor, frequency) in enumerate(_GRADES, start=1):
            self.grades.append(Grade(i, code, is_accident))
            self.grade_profiles[i] = GradeProfile(price_factor, frequency)
