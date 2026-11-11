"""Download EPL data for seasons 2015/16--2024/25."""
from pathlib import Path
import requests

ROOT_DIR = Path(__file__).resolve().parents[1]

SEASONS = {"2015-16":"1516", "2016-17":"1617", "2017-18":"1718", "2018-19":"1819", "2019-20":"1920", "2020-21":"2021", "2021-22":"2122", "2022-23":"2223", "2023-24":"2324", "2024-25":"2425"}

def main():
    out = ROOT_DIR / "data" / "raw"
    out.mkdir(parents=True, exist_ok=True)
    for label, code in SEASONS.items():
        response = requests.get(f"https://www.football-data.co.uk/mmz4281/{code}/E0.csv", timeout=30)
        response.raise_for_status()
        (out / f"epl_{label}.csv").write_bytes(response.content)

if __name__ == "__main__":
    main()