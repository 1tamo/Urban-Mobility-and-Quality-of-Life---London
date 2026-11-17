"""
Shared reading logic for the historical LU station entry/exit file
(multi-year-station-entry-and-exit-figures.xls, 2007-2017).

Used by src/inspect_entry_exit.py (audit) and src/clean_entry_exit.py
(cleaning), so both scripts read the file in exactly the same way.
"""

import re
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_FILE = REPO_ROOT / "data" / "raw" / "multi-year-station-entry-and-exit-figures.xls"

# Day weights used by TfL to gross typical days up to an annual figure
# (Notes sheet): 253 weekdays, 52 Saturdays, 59 Sundays (incl. bank holidays).
WEIGHTS = {"Weekday": 253, "Saturday": 52, "Sunday": 59}

# Value columns after reading with header row 6. pandas adds ".1" to the
# second set of Weekday/Saturday/Sunday columns, which are the exits.
VALUE_COLS = {
    "Weekday": ("entries", "Weekday"),
    "Saturday": ("entries", "Saturday"),
    "Sunday": ("entries", "Sunday"),
    "Weekday.1": ("exits", "Weekday"),
    "Saturday.1": ("exits", "Saturday"),
    "Sunday.1": ("exits", "Sunday"),
}

# Note codes documented on the Notes sheet. "C" and "D" appear in 2016-2017
# but are not explained in the file.
NOTE_MEANINGS = {
    "N": "station_closed",
    "Closed": "station_closed",
    "T": "includes_waterloo_city_line",
    "B": "bank_excludes_waterloo_city_interchange",
    "A": "estimated_from_previous_year",
    "C": "undocumented_note_C",
    "D": "undocumented_note_D",
}

# Sheets that are not yearly data and are not used.
#   "workings": intermediate calculations by the publisher.
#   "Sheet1": a pasted table of station facts (opening dates, lines),
#   apparently copied from a third-party web page; not TfL count data.
IGNORED_SHEETS = ["Notes", "workings", "Sheet1"]


def year_sheets(path: Path = RAW_FILE) -> dict[int, str]:
    """Map year -> sheet name for every '<YYYY> Entry & Exit' sheet."""
    sheets = pd.ExcelFile(path).sheet_names
    out = {}
    for s in sheets:
        m = re.match(r"^(\d{4}) Entry & Exit$", s)
        if m:
            out[int(m.group(1))] = s
    return dict(sorted(out.items()))


def read_year(year: int, sheet: str, path: Path = RAW_FILE) -> tuple[pd.DataFrame, pd.Series | None]:
    """Read one year sheet.

    Returns the station rows (rows with a numeric NLC) and the publisher's
    'Total' row, if present. Header rows above row 6 (title, copyright,
    weights) and formatting-only rows below the table are skipped.
    """
    df = pd.read_excel(path, sheet_name=sheet, header=6)
    df.columns = [str(c).strip() for c in df.columns]
    is_station = pd.to_numeric(df["nlc"], errors="coerce").notna()
    # The publisher's total row has no NLC but has numbers. It is labelled
    # "Total" in some years and unlabelled in others (and missing in 2015).
    has_numbers = pd.to_numeric(df["Weekday.1"], errors="coerce").notna()
    total_rows = df[~is_station & has_numbers]
    total = total_rows.iloc[0] if len(total_rows) else None
    stations = df[is_station].copy()
    stations["nlc"] = stations["nlc"].astype(int)
    stations["Station"] = stations["Station"].astype(str).str.strip()
    stations["Note"] = stations["Note"].astype(str).str.strip().replace({"nan": ""})
    if "Borough" in stations.columns:
        stations["Borough"] = stations["Borough"].astype(str).str.strip()
    stations["year"] = year
    return stations, total


def note_flags(note: str) -> list[str]:
    """Translate a note such as 'B+A' into a list of flag names."""
    if not isinstance(note, str) or not note.strip():
        return []
    parts = [p.strip() for p in note.replace("+", " ").split()]
    return [NOTE_MEANINGS.get(p, f"unknown_note_{p}") for p in parts]
