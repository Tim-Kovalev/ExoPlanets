"""
Streamlit-приложение: индекс обитаемости экзопланет.
Загружает данные из SQLite и считает ESI / обитаемую зону / комплексный индекс.
"""

import sqlite3

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

    # Фильтр в боковой панели
    min_score = st.sidebar.slider(
        "Минимальный комплексный индекс (ESI)",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.05,
    )

    # Оставляем только планеты с Complex_Score не ниже порога
    filtered_df = df[df["Complex_Score"] >= min_score].copy()

    # Если после фильтрации ничего не осталось — предупреждение и выход
    if filtered_df.empty:
        st.warning("Нет планет, удовлетворяющих условиям фильтра")
        return

    # Топ-50 планет по комплексному скору среди отфильтрованных
    top_df = filtered_df.sort_values("Complex_Score", ascending=False).head(50)

    # Русские названия столбцов только для отображения
    display_df = top_df.rename(
        columns={
            "pl_name": "Название",
            "pl_rade": "Радиус (R)",
            "pl_bmasse": "Масса (M)",
            "pl_eqt": "Температура планеты (К)",
            "st_teff": "Температура звезды (К)",
            "st_rad": "Радиус звезды (R)",
            "pl_orbsmax": "Большая полуось (а.е.)",
            "ESI": "ESI",
            "In_HZ": "В обитаемой зоне",
            "Complex_Score": "Комплексный индекс",
        }
    )

    st.dataframe(display_df, use_container_width=True)

    # --- Scatter Plot: температура vs радиус ---
    fig_scatter = px.scatter(
        top_df,
        x="pl_eqt",
        y="pl_rade",
        color="Complex_Score",
        hover_name="pl_name",
        labels={
            "pl_eqt": "Температура (К)",
            "pl_rade": "Радиус (R)",
            "Complex_Score": "Комплексный индекс",
        },
        title="Температура и радиус экзопланет",
    )
    # Прямоугольник зоны обитаемости (температура 180–310 К, радиус 0.5–2.5 R⊕)
    fig_scatter.add_shape(
        type="rect",
        x0=180,
        x1=310,
        y0=0.5,
        y1=2.5,
        line=dict(color="green", width=2, dash="dash"),
        fillcolor="rgba(0, 200, 0, 0.1)",
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- Сравнение с Землёй: Radar Chart ---
    st.subheader("Сравнение с Землей")
    planet_name = st.selectbox("Выберите планету:", filtered_df["pl_name"])

    # Строка выбранной планеты из отфильтрованного набора
    selected = filtered_df[filtered_df["pl_name"] == planet_name].iloc[0]

    categories = ["Радиус", "Масса", "Температура", "ESI"]
    # Земля: радиус=1, масса=1, температура 288/288=1, ESI=1
    earth_values = [1.0, 1.0, 1.0, 1.0]
    # Планета: радиус, масса, нормализованная температура, ESI
    planet_values = [
        float(selected["pl_rade"]),
        float(selected["pl_bmasse"]),
        float(selected["pl_eqt"]) / 288,
        float(selected["ESI"]),
    ]

    fig_radar = go.Figure()
    # След для Земли (синий)
    fig_radar.add_trace(
        go.Scatterpolar(
            r=earth_values,
            theta=categories,
            fill="toself",
            name="Земля",
            line_color="blue",
        )
    )
    # След для выбранной планеты (красный)
    fig_radar.add_trace(
        go.Scatterpolar(
            r=planet_values,
            theta=categories,
            fill="toself",
            name=planet_name,
            line_color="red",
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        showlegend=True,
        title=f"Сравнение: {planet_name} и Земля",
    )
    st.plotly_chart(fig_radar, use_container_width=True)


if __name__ == "__main__":
    main()
