"""
Модуль расчётов пригодности экзопланет для жизни.
Содержит ESI, проверку обитаемой зоны и комплексный скор.
"""


def calculate_esi(radius: float, mass: float, temp: float) -> float:
    """
    Считает Earth Similarity Index (ESI) по радиусу, массе и температуре.

    :param radius: радиус планеты в радиусах Земли (pl_rade)
    :param mass: масса планеты в массах Земли (pl_bmasse)
    :param temp: равновесная температура планеты в К (pl_eqt)
    :return: ESI от 0 до 1, округлённый до 3 знаков
    """
    # Компонент по радиусу (относительно Земли = 1)
    esi_r = 1 - abs((radius - 1) / (radius + 1))
    # Компонент по массе (относительно Земли = 1)
    esi_m = 1 - abs((mass - 1) / (mass + 1))
    # Компонент по температуре (относительно 288 К — средняя температура Земли)
    esi_t = 1 - abs((temp - 288) / (temp + 288))
    # Геометрическое среднее трёх компонентов
    esi = (esi_r * esi_m * esi_t) ** (1 / 3)
    return round(esi, 3)


def is_in_habitable_zone(st_teff: float, st_rad: float, pl_orbsmax: float) -> bool:
    """
    Проверяет, находится ли планета в обитаемой зоне звезды.

    :param st_teff: эффективная температура звезды в К
    :param st_rad: радиус звезды в радиусах Солнца
    :param pl_orbsmax: большая полуось орбиты планеты в а.е.
    :return: True, если планета в обитаемой зоне, иначе False
    """
    # Светимость звезды в единицах светимости Солнца
    luminosity = (st_rad ** 2) * ((st_teff / 5778) ** 4)
    # Внутренняя граница обитаемой зоны (а.е.)
    inner_hz = (luminosity / 1.1) ** 0.5
    # Внешняя граница обитаемой зоны (а.е.)
    outer_hz = (luminosity / 0.53) ** 0.5
    return inner_hz <= pl_orbsmax <= outer_hz


def calculate_complex_score(esi: float, in_hz: bool) -> float:
    """
    Считает комплексный скор: ESI с бонусом за обитаемую зону.

    :param esi: значение Earth Similarity Index
    :param in_hz: находится ли планета в обитаемой зоне
    :return: итоговый скор (не больше 1.0)
    """
    # Бонус +0.2 за нахождение в обитаемой зоне, но не выше 1.0
    if in_hz:
        return min(esi + 0.2, 1.0)
    return esi
