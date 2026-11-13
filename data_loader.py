"""
Модуль загрузки данных экзопланет с NASA Exoplanet Archive.
Кэширует результат в локальную SQLite-базу exoplanets.db.
"""

import os
import sqlite3

import pandas as pd
import requests

# Имя файла локальной базы данных
DB_PATH = "exoplanets.db"

# URL TAP API NASA Exoplanet Archive
TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"

# SQL-запрос: только строки с заполненными целевыми колонками
TAP_QUERY = (
    "select pl_name, pl_rade, pl_bmasse, pl_eqt, st_teff, st_rad, pl_orbsmax "
    "from ps "
    "where pl_rade is not null and pl_bmasse is not null "
    "and pl_eqt is not null and st_teff is not null "
    "and st_rad is not null and pl_orbsmax is not null"
)


def load_exoplanets() -> None:
    """Загружает данные с NASA, очищает и сохраняет в SQLite."""
    # Кэширование: если база уже есть — повторная загрузка не нужна
    if os.path.exists(DB_PATH):
        print("База данных уже существует. Загрузка не требуется.")
        return

    # Параметры GET-запроса к TAP API
    params = {
        "query": TAP_QUERY,
        "format": "csv",
    }

    # Выполняем запрос к NASA Exoplanet Archive
    response = requests.get(TAP_URL, params=params, timeout=120)
    response.raise_for_status()

    # Читаем CSV-ответ в DataFrame
    from io import StringIO

    df = pd.read_csv(StringIO(response.text))

    # Удаляем строки с пустыми значениями
    df = df.dropna()

    # Сохраняем в SQLite-таблицу planets (перезаписываем при наличии)
    with sqlite3.connect(DB_PATH) as conn:
        df.to_sql("planets", conn, if_exists="replace", index=False)

    print(f"Успешно загружено строк: {len(df)}")


if __name__ == "__main__":
    load_exoplanets()
