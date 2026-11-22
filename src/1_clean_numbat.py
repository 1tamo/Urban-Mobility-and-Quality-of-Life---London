"""Step 1: clean the NUMBAT files, 2018-2025.

Reads the NUMBAT Excel files in data/raw/ and writes two tables to
data/processed/:

    numbat_stations.csv  one row = one station, one year, one day type,
                         one 15-minute slot
                         columns: year, day_type, nlc, station, time, time_band,
                         entries, exits
    numbat_links.csv     one row = one link (stretch of track between two
                         neighbouring stations, one direction) on a typical
                         2025 weekday, one 15-minute slot
                         columns: line, link, from_station, to_station,
                         direction, time, time_band, passengers, trains

Day types are weekday, saturday and sunday. NUMBAT's weekday file is
Monday-Thursday (MTT) up to 2021 and Tuesday-Thursday (TWT) from 2022.
Trams are left out: NUMBAT does not model them. Raw files are never changed.

Run from the repository root:
    python src/1_clean_numbat.py
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "processed"

YEARS = range(2018, 2026)
LINKS_YEAR = 2025
SLOT = re.compile(r"^\d{4}-\d{4}$")  # 15-minute columns, e.g. "0800-0815"
BANDS = [("Early", "05:00"), ("AM Peak", "07:00"), ("Midday", "10:00"),
         ("PM Peak", "16:00"), ("Evening", "19:00"), ("Late", "22:00")]


def find_file(year: int, day_type: str) -> Path:
    """NUMBAT file for one year and day type (file names vary slightly by year)."""
    codes = {"weekday": ["MTT", "TWT"], "saturday": ["SAT"], "sunday": ["SUN"]}[day_type]
    for code in codes:
        for name in (f"NBT{year % 100}{code}_Outputs.xlsx", f"NBT{year % 100}{code}_outputs.xlsx"):
            if (RAW / name).exists():
                return RAW / name
    raise FileNotFoundError(f"No NUMBAT {year} {day_type} file in data/raw/ (see docs/data.md)")


def read_sheet(path: Path, sheet: str) -> pd.DataFrame:
    """NUMBAT sheets have three header rows; the third holds the column names."""
    df = pd.read_excel(path, sheet_name=sheet, header=2)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def time_band(time: str) -> str:
    """NUMBAT time band for a slot start time such as '08:15'."""
    if time < "05:00":
        return "Late"
    return [name for name, start in BANDS if time >= start][-1]


def to_long(wide: pd.DataFrame, id_cols: list[str], value: str) -> pd.DataFrame:
    """Turn the 96 slot columns into rows, and check nothing was lost."""
    slots = [c for c in wide.columns if SLOT.match(c)]
    assert len(slots) == 96, f"expected 96 slots, found {len(slots)}"
    long = wide.melt(id_vars=id_cols, value_vars=slots, var_name="slot", value_name=value)
    # Check: the 15-minute values add up to the published daily total.
    diff = (long.groupby(id_cols[0])[value].sum() - wide.set_index(id_cols[0])["Total"]).abs().max()
    assert diff < 0.01, f"15-minute values do not add up to the daily total ({diff})"
    long["time"] = long["slot"].str[:2] + ":" + long["slot"].str[2:4]
    return long.drop(columns="slot")


def clean_stations(path: Path, year: int, day_type: str) -> pd.DataFrame:
    id_cols = ["NLC", "ASC", "Station"]
    entries = to_long(read_sheet(path, "Station_Entries"), id_cols, "entries")
    exits = to_long(read_sheet(path, "Station_Exits"), id_cols, "exits")
    df = entries.merge(exits, on=id_cols + ["time"], validate="one_to_one")
    df = df[~df["ASC"].astype(str).str.endswith("t")]  # drop tram stops
    df["year"] = year
    df["day_type"] = day_type
    df["time_band"] = df["time"].map(time_band)
    df = df.rename(columns={"NLC": "nlc", "Station": "station"})
    return df[["year", "day_type", "nlc", "station", "time", "time_band", "entries", "exits"]]


def clean_links(path: Path) -> pd.DataFrame:
    id_cols = ["Link", "Line", "Dir", "From Station", "To Station"]
    loads = to_long(read_sheet(path, "Link_Loads"), id_cols, "passengers")
    trains = to_long(read_sheet(path, "Link_Frequencies"), ["Link"], "trains")
    df = loads.merge(trains, on=["Link", "time"], validate="one_to_one")
    df = df[df["Line"] != "London Trams"]  # drop tram links
    df["time_band"] = df["time"].map(time_band)
    df = df.rename(columns={"Link": "link", "Line": "line", "Dir": "direction",
                            "From Station": "from_station", "To Station": "to_station"})
    return df[["line", "link", "from_station", "to_station", "direction",
               "time", "time_band", "passengers", "trains"]]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    stations = []
    for year in YEARS:
        for day_type in ["weekday", "saturday", "sunday"]:
            path = find_file(year, day_type)
            print(f"Reading {path.name}")
            stations.append(clean_stations(path, year, day_type))
    stations = pd.concat(stations, ignore_index=True)
    stations.to_csv(OUT / "numbat_stations.csv", index=False)
    print(f"numbat_stations.csv: {len(stations):,} rows, {YEARS[0]}-{YEARS[-1]}")

    links = clean_links(find_file(LINKS_YEAR, "weekday"))
    links.to_csv(OUT / "numbat_links.csv", index=False)
    print(f"numbat_links.csv: {len(links):,} rows, {links['link'].nunique()} links")


if __name__ == "__main__":
    main()
