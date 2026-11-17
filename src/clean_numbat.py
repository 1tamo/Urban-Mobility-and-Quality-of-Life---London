"""
Clean the TfL NUMBAT 2025 typical-day outputs.

This script turns the raw NUMBAT Excel files into tidy CSV tables in
data/processed/. Every cleaning step follows a decision recorded in
docs/data_audit.md (section 4). Raw files are never modified.

Outputs (all in data/processed/):

    station_demand_long.csv
        Master station-level table, one row per
        station x day type x 15-minute slot x measure (entries / exits).
        Designed so that other sources (e.g. historical entry/exit counts)
        can be appended later with the same columns.

    link_demand_long.csv
        One row per link x day type x 15-minute slot, with passenger load,
        number of trains and passengers per train.

    camden_town_detail.csv
        Fine-grained table for one station (Camden Town), one row per
        day type x 15-minute slot, with entries, exits and boarders /
        alighters by platform.

A cleaning log with row counts and validation results is written to
reports/cleaning_log_numbat2025.md.

Usage (from the repository root, with the .venv activated):

    python src/clean_numbat.py
"""

import re
from datetime import date
from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
OUT_DIR = REPO_ROOT / "data" / "processed"
REPORT_DIR = REPO_ROOT / "reports"
DEFINITIONS_FILE = RAW_DIR / "PTSP Oasis for NUMBAT definitions.xlsx"

YEAR = 2025
DAY_TYPES = ["MON", "TWT", "FRI", "SAT", "SUN"]
DAY_LABELS = {
    "MON": "Monday",
    "TWT": "Tuesday-Thursday",
    "FRI": "Friday",
    "SAT": "Saturday",
    "SUN": "Sunday",
}

# Detail station for the fine-grained table (see docs/data_audit.md).
DETAIL_NLC = 535  # Camden Town
DETAIL_NAME = "camden_town"

# Time bands, as verified in the audit: each band is exactly the sum of
# these 15-minute slots. Times are start times (HHMM) of the slots.
TIME_BANDS = [
    ("Early", "0500", "0700"),
    ("AM Peak", "0700", "1000"),
    ("Midday", "1000", "1600"),
    ("PM Peak", "1600", "1900"),
    ("Evening", "1900", "2200"),
    ("Late", "2200", "0500"),  # runs past midnight
]

QHR_PATTERN = re.compile(r"^\d{4}-\d{4}$")
TOLERANCE = 0.01

log_lines: list[str] = []


def log(message: str) -> None:
    """Print a message and keep it for the cleaning log."""
    print(message)
    log_lines.append(message)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def read_sheet(path: Path, sheet: str) -> pd.DataFrame:
    """Read a NUMBAT sheet, using the third header row as column names."""
    df = pd.read_excel(path, sheet_name=sheet, header=2)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def qhr_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if QHR_PATTERN.match(c)]


def time_band(slot_start: str) -> str:
    """Return the time band for a slot start time such as '0715'."""
    for band, start, end in TIME_BANDS:
        if start < end and start <= slot_start < end:
            return band
        if start > end and (slot_start >= start or slot_start < end):
            return band
    raise ValueError(f"No time band for {slot_start}")


def slot_table(qhr_cols: list[str]) -> pd.DataFrame:
    """Lookup table describing the 96 slots (order, start time, band)."""
    return pd.DataFrame(
        {
            "time_slot": qhr_cols,
            "slot_index": range(1, len(qhr_cols) + 1),
            "slot_start": [f"{c[:2]}:{c[2:4]}" for c in qhr_cols],
            "time_band": [time_band(c[:4]) for c in qhr_cols],
        }
    )


def to_long(df: pd.DataFrame, id_cols: list[str], value_name: str) -> pd.DataFrame:
    """Reshape the 96 slot columns into rows (wide -> long)."""
    q = qhr_columns(df)
    long = df.melt(id_vars=id_cols, value_vars=q, var_name="time_slot",
                   value_name=value_name)
    return long


def check_sum(long: pd.DataFrame, wide: pd.DataFrame, key: list[str],
              value: str, label: str) -> None:
    """Validation: long values must add back up to the original daily Total."""
    summed = long.groupby(key)[value].sum()
    original = wide.set_index(key)["Total"]
    diff = (summed - original.reindex(summed.index)).abs().max()
    status = "OK" if diff <= TOLERANCE else "FAILED"
    log(f"  check {label}: long sums vs original Total, max difference "
        f"{diff:.4f} -> {status}")
    if status == "FAILED":
        raise AssertionError(f"Validation failed for {label}")


# ---------------------------------------------------------------------------
# Station demand (master table)
# ---------------------------------------------------------------------------
def build_station_demand(day: str, path: Path, slots: pd.DataFrame) -> pd.DataFrame:
    parts = []
    for sheet, measure in [("Station_Entries", "entries"), ("Station_Exits", "exits")]:
        wide = read_sheet(path, sheet)
        id_cols = ["NLC", "ASC", "Station", "Fare Zone"]
        long = to_long(wide, id_cols, "value")
        check_sum(long, wide, ["NLC"], "value", f"{day} {sheet}")
        long["measure"] = measure
        parts.append(long)
    df = pd.concat(parts, ignore_index=True)

    # Decision B: London Trams stops are not modelled in NUMBAT 2025.
    # Keep them, but flag them so they are excluded from analyses by default.
    is_tram = df["ASC"].astype(str).str.endswith("t")
    df["in_scope"] = ~is_tram
    df["scope_note"] = is_tram.map({True: "trams_not_modelled", False: ""})

    df = df.merge(slots, on="time_slot", how="left")
    df["source"] = "NUMBAT"
    df["year"] = YEAR
    df["day_type"] = day
    df["day_label"] = DAY_LABELS[day]
    df = df.rename(columns={"NLC": "nlc", "ASC": "asc", "Station": "station",
                            "Fare Zone": "fare_zone"})
    return df


# ---------------------------------------------------------------------------
# Link demand (supporting table)
# ---------------------------------------------------------------------------
def build_link_demand(day: str, path: Path, slots: pd.DataFrame,
                      distances: pd.Series | None) -> pd.DataFrame:
    id_cols = ["Link", "Line", "Dir", "Order", "From NLC", "From Station",
               "To NLC", "To Station"]
    loads_w = read_sheet(path, "Link_Loads")
    freqs_w = read_sheet(path, "Link_Frequencies")
    loads = to_long(loads_w, id_cols, "passengers")
    freqs = to_long(freqs_w, ["Link"], "trains")
    check_sum(loads, loads_w, ["Link"], "passengers", f"{day} Link_Loads")
    check_sum(freqs, freqs_w, ["Link"], "trains", f"{day} Link_Frequencies")

    df = loads.merge(freqs, on=["Link", "time_slot"], how="left", validate="one_to_one")

    # Passengers per train: only defined where at least one train runs.
    df["passengers_per_train"] = (df["passengers"] / df["trains"]).where(df["trains"] > 0)

    # Decision C: flag tram links (out of scope) and links with no service all day.
    is_tram = df["Line"].eq("London Trams")
    daily_trains = freqs_w.set_index("Link")["Total"]
    no_service = df["Link"].map(daily_trains).eq(0) & ~is_tram
    df["in_scope"] = ~is_tram
    df["scope_note"] = ""
    df.loc[is_tram, "scope_note"] = "trams_not_modelled"
    df.loc[no_service, "scope_note"] = "no_service"

    # Decision E: add link distance where the link code matches the
    # (2024) Definitions file; unmatched links keep a blank distance.
    if distances is not None:
        df["distance_m"] = df["Link"].str.split("@").str[0].map(distances)

    df = df.merge(slots, on="time_slot", how="left")
    df["year"] = YEAR
    df["day_type"] = day
    df = df.rename(columns={
        "Link": "link", "Line": "line", "Dir": "direction", "Order": "link_order",
        "From NLC": "from_nlc", "From Station": "from_station",
        "To NLC": "to_nlc", "To Station": "to_station",
    })
    return df


# ---------------------------------------------------------------------------
# Detail station table
# ---------------------------------------------------------------------------
def build_detail(day: str, path: Path, station_long: pd.DataFrame,
                 slots: pd.DataFrame) -> pd.DataFrame:
    s = station_long[station_long["nlc"] == DETAIL_NLC]
    wide = s.pivot_table(index="time_slot", columns="measure", values="value",
                         aggfunc="sum").reset_index()

    for sheet, prefix in [("Station_Boarders", "board"), ("Station_Alighters", "alight")]:
        df = read_sheet(path, sheet)
        df = df[df["NLC"] == DETAIL_NLC]
        for _, row in df.iterrows():
            # e.g. "Northern (Edgware branch) // NB" -> "board_northern_edgware_branch_nb"
            label = re.sub(r"[^a-z0-9]+", "_", str(row["Platform"]).lower()).strip("_")
            col = f"{prefix}_{label}"
            values = row[qhr_columns(df)].rename(col)
            wide = wide.merge(values.rename_axis("time_slot").reset_index(),
                              on="time_slot", how="left")

    wide = slots.merge(wide, on="time_slot", how="left")
    wide.insert(0, "day_type", day)
    wide.insert(1, "day_label", DAY_LABELS[day])
    return wide


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(exist_ok=True)

    distances = None
    if DEFINITIONS_FILE.exists():
        links_def = pd.read_excel(DEFINITIONS_FILE, sheet_name="LinksRail")
        distances = links_def.drop_duplicates("LinkCode").set_index("LinkCode")["DistanceM"]
    else:
        log("Definitions file not found: link distances will be blank.")

    stations, links, detail = [], [], []
    for day in DAY_TYPES:
        path = RAW_DIR / f"NBT25{day}_Outputs.xlsx"
        if not path.exists():
            raise FileNotFoundError(f"{path} not found (see docs/data_sources.md).")
        log(f"Cleaning {path.name}")
        slots = slot_table(qhr_columns(read_sheet(path, "Station_Entries")))

        st = build_station_demand(day, path, slots)
        stations.append(st)
        links.append(build_link_demand(day, path, slots, distances))
        detail.append(build_detail(day, path, st, slots))

    # --- Master station table -------------------------------------------
    station_cols = ["source", "year", "day_type", "day_label", "nlc", "asc",
                    "station", "fare_zone", "time_slot", "slot_index",
                    "slot_start", "time_band", "measure", "value",
                    "in_scope", "scope_note"]
    station_df = pd.concat(stations, ignore_index=True)[station_cols]
    key = ["source", "year", "day_type", "nlc", "time_slot", "measure"]
    assert not station_df.duplicated(key).any(), "Duplicate keys in station table"
    station_df.to_csv(OUT_DIR / "station_demand_long.csv", index=False)

    # --- Link table -------------------------------------------------------
    link_df = pd.concat(links, ignore_index=True)
    link_cols = ["year", "day_type", "link", "line", "direction", "link_order",
                 "from_nlc", "from_station", "to_nlc", "to_station",
                 "distance_m", "time_slot", "slot_index", "slot_start",
                 "time_band", "passengers", "trains", "passengers_per_train",
                 "in_scope", "scope_note"]
    link_df = link_df[[c for c in link_cols if c in link_df.columns]]
    assert not link_df.duplicated(["day_type", "link", "time_slot"]).any()
    link_df.to_csv(OUT_DIR / "link_demand_long.csv", index=False)

    # --- Detail table -----------------------------------------------------
    detail_df = pd.concat(detail, ignore_index=True)
    detail_df.to_csv(OUT_DIR / f"{DETAIL_NAME}_detail.csv", index=False)

    # --- Summary for the log ---------------------------------------------
    n_tram_st = station_df.loc[~station_df["in_scope"], "nlc"].nunique()
    n_tram_lk = link_df.loc[link_df["scope_note"] == "trams_not_modelled", "link"].nunique()
    n_nosvc = link_df.loc[link_df["scope_note"] == "no_service", "link"].nunique()
    n_nodist = link_df.loc[link_df["distance_m"].isna(), "link"].nunique() if "distance_m" in link_df else "n/a"
    log("")
    log(f"station_demand_long.csv: {len(station_df):,} rows "
        f"({station_df['nlc'].nunique()} stations x {len(DAY_TYPES)} day types "
        f"x 96 slots x 2 measures)")
    log(f"  stations flagged trams_not_modelled: {n_tram_st}")
    log(f"link_demand_long.csv: {len(link_df):,} rows "
        f"({link_df['link'].nunique()} links x {len(DAY_TYPES)} day types x 96 slots)")
    log(f"  links flagged trams_not_modelled: {n_tram_lk}; no_service: {n_nosvc}; "
        f"without distance (not in Definitions): {n_nodist}")
    log(f"{DETAIL_NAME}_detail.csv: {len(detail_df):,} rows, "
        f"{detail_df.shape[1]} columns")
    log("Rows removed: none (all issues handled by flags; Line_Boarders and "
        "Station_Flows are not used in these outputs).")

    report = [
        "# Cleaning log: NUMBAT 2025",
        "",
        f"_Generated by `src/clean_numbat.py` on {date.today().isoformat()}. "
        "Decisions follow docs/data_audit.md, section 4._",
        "",
        "```",
        *log_lines,
        "```",
        "",
    ]
    (REPORT_DIR / "cleaning_log_numbat2025.md").write_text("\n".join(report), encoding="utf-8")
    print(f"\nOutputs written to {OUT_DIR.relative_to(REPO_ROOT)}/ and "
          f"reports/cleaning_log_numbat2025.md")


if __name__ == "__main__":
    main()
