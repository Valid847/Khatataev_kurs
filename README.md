# Курсовая работа: прогнозирование исходов матчей EPL

Предсказание результата матча Английской Премьер-лиги (1X2) по результатам
предыдущих матчей команд. Данные: [Football-Data.co.uk](https://www.football-data.co.uk/),
сезоны 2015/16--2024/25. Текст работы лежит в `docs/` (собирается в Overleaf).

## Запуск

```bash
uv sync
uv run python scripts/download_data.py
for n in 3 5 10 15 20; do uv run python scripts/build_dataset.py --n $n; done
```

Затем откройте `notebooks/01_logistic_regression.ipynb`.

## Структура

- `scripts/` — скачивание данных и сборка датасетов
- `notebooks/` — эксперименты
- `notes/` — заметки по датасетам и статьям
- `docs/` — LaTeX-текст курсовой
- `data/` — сырые и обработанные данные (в git не хранятся)
