from collections import defaultdict
from pathlib import Path
import argparse
import pandas as pd


# Пути
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"


def load_matches():
    files = sorted(RAW_DIR.glob("*.csv"))
    tables = []
    required_columns = ["Date", "HomeTeam", "AwayTeam", "FTR"]

    for file in files:
        table = pd.read_csv(file, encoding="latin-1")
        table.columns = table.columns.str.strip()
        table = table[required_columns].copy()

        # Преобразуем даты отдельно для каждого сезона
        table["Date"] = pd.to_datetime(
            table["Date"],
            dayfirst=True,
            format="mixed",
            errors="coerce"
        )

        invalid_dates = table["Date"].isna().sum()

        if invalid_dates > 0:
            raise ValueError(f"Некорректные даты в файле {file.name}")

        tables.append(table)

    matches = pd.concat(tables, ignore_index=True)

    matches["HomeTeam"] = matches["HomeTeam"].astype(str).str.strip()
    matches["AwayTeam"] = matches["AwayTeam"].astype(str).str.strip()
    matches["FTR"] = matches["FTR"].astype(str).str.strip().str.upper()

    matches = matches.dropna(subset=required_columns)

    matches = matches[
        (matches["HomeTeam"] != "")
        & (matches["AwayTeam"] != "")
        & (matches["FTR"].isin(["H", "D", "A"]))
    ]

    matches = matches.sort_values("Date").reset_index(drop=True)

    return matches


def calculate_features(history, n, prefix):
    last_matches = history[-n:]

    if len(last_matches) < n:
        return None

    return {
        f"{prefix}_wins": last_matches.count("W"),
        f"{prefix}_draws": last_matches.count("D"),
        f"{prefix}_losses": last_matches.count("L"),
    }


def build_dataset(matches, n):
    history = defaultdict(list)
    rows = []

    # Обрабатываем матчи по датам
    for date, day_matches in matches.groupby("Date"):
        day_matches = day_matches.to_dict("records")

        # рассчитываем признаки для всех матчей этого дня
        for match in day_matches:
            home_team = match["HomeTeam"]
            away_team = match["AwayTeam"]

            home_features = calculate_features(
                history[home_team], n, "home"
            )

            away_features = calculate_features(
                history[away_team], n, "away"
            )

            if home_features is None or away_features is None:
                continue

            row = {
                "Date": date,
                "HomeTeam": home_team,
                "AwayTeam": away_team,
                **home_features,
                **away_features,
                "target": match["FTR"],
            }

            rows.append(row)

        # добавляем результаты матчей дня в историю команд
        for match in day_matches:
            home_team = match["HomeTeam"]
            away_team = match["AwayTeam"]
            result = match["FTR"]

            if result == "H":
                history[home_team].append("W")
                history[away_team].append("L")
            elif result == "A":
                history[home_team].append("L")
                history[away_team].append("W")
            else:
                history[home_team].append("D")
                history[away_team].append("D")

    columns = [
        "Date",
        "HomeTeam",
        "AwayTeam",
        "home_wins",
        "home_draws",
        "home_losses",
        "away_wins",
        "away_draws",
        "away_losses",
        "target",
    ]

    return pd.DataFrame(rows, columns=columns)


def main():
    parser = argparse.ArgumentParser(
        description="Создание датасета по результатам предыдущих матчей"
    )

    parser.add_argument(
        "--n",
        type=int,
        default=5,
        help="Количество предыдущих матчей каждой команды"
    )

    args = parser.parse_args()

    # Загружаем матчи
    matches = load_matches()

    # Создаём датасет
    dataset = build_dataset(matches, args.n)

    # Проверка
    missing_values = dataset.isna().sum().sum()

    duplicate_matches = dataset.duplicated(
        subset=["Date", "HomeTeam", "AwayTeam"]
    ).sum()

    # Сохраняем датасет
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    output_path = PROCESSED_DIR / f"dataset_n{args.n}.csv"
    dataset.to_csv(output_path, index=False)

    # Вывод
    print(f"Загружено матчей: {len(matches)}")
    print(f"Количество предыдущих матчей(N): {args.n}")
    print(dataset.shape)
    print(f"Пропущенных значений: {missing_values}")
    print(f"Повторяющихся матчей: {duplicate_matches}")
    print("\nРаспределение результатов матчей:")
    print(dataset["target"].value_counts())

if __name__ == "__main__":
    main()
