"""
Streamlit-приложение: индекс обитаемости экзопланет
Загружает данные из SQLite и считает ESI / обитаемую зону / комплексный индекс
"""

import sqlite3

import pandas as pd
import streamlit as st

from calculations import (
    calculate_complex_score,
    calculate_esi,
    is_in_habitable_zone,
)

# Конфигурация страницы
st.set_page_config(page_title="Индекс обитаемости экзопланет", layout="wide")


@st.cache_data
def load_data() -> pd.DataFrame:
    """Читает таблицу planets из локальной SQLite-базы exoplanets.db."""
    with sqlite3.connect("exoplanets.db") as conn:
        df = pd.read_sql("SELECT * FROM planets", conn)
    return df


def main() -> None:
    """Основная логика приложения."""
    st.title("🪐 Индекс обитаемости экзопланет")

    # Загрузка данных из кэша / SQLite
    df = load_data()

    # Earth Similarity Index по радиусу, массе и температуре
    df["ESI"] = df.apply(
        lambda row: calculate_esi(row["pl_rade"], row["pl_bmasse"], row["pl_eqt"]),
        axis=1,
    )

    # Признак нахождения в обитаемой зоне звезды
    df["In_HZ"] = df.apply(
        lambda row: is_in_habitable_zone(
            row["st_teff"], row["st_rad"], row["pl_orbsmax"]
        ),
        axis=1,
    )

    # Комплексный скор: ESI + бонус за обитаемую зону
    df["Complex_Score"] = df.apply(
        lambda row: calculate_complex_score(row["ESI"], row["In_HZ"]),
        axis=1,
    )

    # Топ-50 планет по комплексному скору
    top_df = df.sort_values("Complex_Score", ascending=False).head(50)

    # Русские названия столбцов только для отображения
    display_df = top_df.rename(
        columns={
            "pl_name": "Название",
            "pl_rade": "Радиус (R⊕)",
            "pl_bmasse": "Масса (M⊕)",
            "pl_eqt": "Температура планеты (К)",
            "st_teff": "Температура звезды (К)",
            "st_rad": "Радиус звезды (R☉)",
            "pl_orbsmax": "Большая полуось (а.е.)",
            "ESI": "ESI",
            "In_HZ": "В обитаемой зоне",
            "Complex_Score": "Комплексный индекс",
        }
    )

    st.dataframe(display_df, use_container_width=True)


if __name__ == "__main__":
    main()
