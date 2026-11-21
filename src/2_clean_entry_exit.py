"""Step 2: clean the Underground station entry/exit counts, 2007-2017.

Reads data/raw/multi-year-station-entry-and-exit-figures.xls (one sheet per
year) and writes data/processed/entry_exit_2007_2017.csv:

    one row = one Underground station, one year, one day type
    columns: year, nlc, station, day_type, entries, exits, note

`note` translates the letter codes in the original file (e.g. "A" becomes
"estimated from previous year"). Raw files are never changed.

Run from the repository root:
    python src/2_clean_entry_exit.py
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = ROOT / "data" / "raw" / "multi-year-station-entry-and-exit-figures.xls"
OUT_FILE = ROOT / "data" / "processed" / "entry_exit_2007_2017.csv"

# The first three value columns are entries, the next three exits
# (pandas adds ".1" to the repeated names).
COLUMNS = {
    "Weekday": ("entries", "weekday"), "Saturday": ("entries", "saturday"),
    "Sunday": ("entries", "sunday"), "Weekday.1": ("exits", "weekday"),
    "Saturday.1": ("exits", "saturday"), "Sunday.1": ("exits", "sunday"),
}
# Meaning of the note codes, from the file's Notes sheet. C and D are not explained there.
NOTES = {
    "A": "estimated from previous year", "N": "station closed", "Closed": "station closed",
    "T": "includes Waterloo & City line", "B": "excludes Waterloo & City interchange",
    "C": "unexplained code C", "D": "unexplained code D",
}


def read_year(sheet: str, year: int) -> pd.DataFrame:
    df = pd.read_excel(RAW_FILE, sheet_name=sheet, header=6)
    df.columns = [str(c).strip() for c in df.columns]
    df = df[pd.to_numeric(df["nlc"], errors="coerce").notna()]  # station rows only
    df["Note"] = df["Note"].fillna("").astype(str).str.strip()
    long = df.melt(id_vars=["nlc", "Station", "Note"], value_vars=list(COLUMNS),
                   var_name="column", value_name="value")
    long["measure"] = long["column"].map(lambda c: COLUMNS[c][0])
    long["day_type"] = long["column"].map(lambda c: COLUMNS[c][1])
    out = long.pivot_table(index=["nlc", "Station", "Note", "day_type"], columns="measure",
                           values="value").reset_index()
    assert len(out) == len(df) * 3, f"{year}: rows lost while reshaping"
    out["year"] = year
    return out


def translate(note: str) -> str:
    codes = note.replace("+", " ").split()
    return "; ".join(NOTES.get(c, f"code {c}") for c in codes)


def main() -> None:
    sheets = pd.ExcelFile(RAW_FILE).sheet_names
    years = {int(m.group(1)): s for s in sheets if (m := re.match(r"^(\d{4}) Entry & Exit$", s))}
    df = pd.concat([read_year(s, y) for y, s in sorted(years.items())], ignore_index=True)

    df["nlc"] = df["nlc"].astype(int)
    df["station"] = df["Station"].astype(str).str.strip()
    df["note"] = df["Note"].map(translate)
    df[["entries", "exits"]] = df[["entries", "exits"]].round().astype(int)
    df = df[["year", "nlc", "station", "day_type", "entries", "exits", "note"]]
    df = df.sort_values(["year", "station", "day_type"]).reset_index(drop=True)
    assert not df.duplicated(["year", "nlc", "day_type"]).any()

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)
    print(f"{OUT_FILE.name}: {len(df):,} rows, {df['nlc'].nunique()} stations, "
          f"{df['year'].min()}-{df['year'].max()}")


if __name__ == "__main__":
    main()
