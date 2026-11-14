# Индекс обитаемости экзопланет

MVP для хакатона **TulaHack 2026** (задача 3: «Поиск планеты, пригодной для жизни»).

Streamlit-приложение загружает данные NASA Exoplanet Archive, считает Earth Similarity Index (ESI), проверяет обитаемую зону и показывает топ планет с 3D-визуализацией и сравнением с Землёй.

## Требования

- Python 3.10+
- Интернет (только для первой загрузки данных с NASA)

## Структура проекта

```
TulaHack/
├── requirements.txt   # зависимости
├── data_loader.py     # загрузка данных NASA → SQLite
├── calculations.py    # ESI, обитаемая зона, комплексный индекс
├── app.py             # Streamlit-интерфейс
└── exoplanets.db      # кэш данных (создаётся скриптом data_loader.py)
```

## Установка

1. Склонируйте или скопируйте папку проекта.

2. Откройте терминал в папке проекта и создайте виртуальное окружение:

```bash
python -m venv .venv
```

На Windows, если команда `python` не находится, используйте:

```powershell
py -m venv .venv
```

3. Установите зависимости:

**Windows (PowerShell):**

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Если активация через `Activate.ps1` выдаёт ошибку про Execution Policy, либо выполните:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

либо просто вызывайте Python/Streamlit напрямую из `.venv\Scripts\` без активации.

**Linux / macOS:**

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Загрузка данных

Перед первым запуском приложения нужно один раз скачать данные NASA:

**Windows:**

```powershell
.\.venv\Scripts\python.exe data_loader.py
```

**Linux / macOS:**

```bash
python data_loader.py
```

Скрипт создаст файл `exoplanets.db`. При повторном запуске, если база уже есть, загрузка пропускается.

Чтобы обновить данные заново — удалите `exoplanets.db` и снова запустите `data_loader.py`.

## Запуск приложения

**Windows:**

```powershell
.\.venv\Scripts\streamlit.exe run app.py
```

**Linux / macOS:**

```bash
streamlit run app.py
```

Откройте в браузере адрес, который покажет Streamlit (обычно [http://localhost:8501](http://localhost:8501)).

## Как пользоваться

1. В боковой панели задайте минимальный комплексный индекс.
2. Вкладка **Топ-50** — таблица лучших планет по фильтру.
3. Вкладка **3D Анализ** — 3D-график; клик по точке обновляет radar-сравнение с Землёй.

## Стек

- Python 3.10+
- Streamlit
- Plotly
- pandas, requests
- SQLite
