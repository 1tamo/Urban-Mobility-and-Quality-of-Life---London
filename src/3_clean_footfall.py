"""Step 3: clean TfL station footfall (entries and exits per station per day).

Reads every StationFootfall_*.csv file in data/raw/ and writes
data/processed/footfall_daily.csv:

    one row = one station on one real date
    columns: date, day_of_week, station, entries, exits

Unlike NUMBAT, these are real dates, so event days are included.
Raw files are never changed.

Run from the repository root:
    python src/3_clean_footfall.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT_FILE = ROOT / "data" / "processed" / "footfall_daily.csv"


def main() -> None:
    files = sorted(RAW.glob("StationFootfall_*.csv"))
    if not files:
        raise FileNotFoundError("No StationFootfall_*.csv files in data/raw/ (see docs/data.md)")

    parts = []
    for path in files:
        df = pd.read_csv(path, encoding="utf-8-sig")  # some files start with a hidden BOM character
        print(f"Reading {path.name}: {len(df):,} rows")
        parts.append(df)
    df = pd.concat(parts, ignore_index=True)

    df = df.rename(columns={"TravelDate": "date", "DayOfWeek": "day_of_week", "Station": "station",
                            "EntryTapCount": "entries", "ExitTapCount": "exits"})
    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d").dt.date
    df["station"] = df["station"].str.strip()
    df = df.drop_duplicates(["date", "station"])  # in case two files overlap
    df = df.sort_values(["date", "station"])[["date", "day_of_week", "station", "entries", "exits"]]

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"{OUT_FILE.name}: {len(df):,} rows, {df['station'].nunique()} stations, "
          f"{df['date'].min()} to {df['date'].max()}")


if __name__ == "__main__":
    main()
