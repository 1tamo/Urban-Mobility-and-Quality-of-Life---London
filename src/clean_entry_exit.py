"""
Clean the historical LU station entry/exit counts (2007-2017).

Decisions follow docs/data_audit.md (historical entry/exit section).
Raw data are never modified. No rows are removed: issues are flagged.

Output: data/processed/lu_entry_exit_2007_2017_long.csv
    One row per station x year x day type (Weekday / Saturday / Sunday)
    x measure (entries / exits). Columns match the NUMBAT station table so
    that both can be combined by src/build_master.py.

Usage (from the repository root, with the .venv activated):

    python src/clean_entry_exit.py
"""

import pandas as pd

from entry_exit_common import RAW_FILE, REPO_ROOT, VALUE_COLS, note_flags, read_year, year_sheets

OUT_FILE = REPO_ROOT / "data" / "processed" / "lu_entry_exit_2007_2017_long.csv"
NUMBAT_STATIONS = REPO_ROOT / "data" / "processed" / "station_demand_long.csv"

DAY_CODES = {"Weekday": ("WKD", "Weekday (typical)"),
             "Saturday": ("SAT", "Saturday"),
             "Sunday": ("SUN", "Sunday")}


def main() -> None:
    if not RAW_FILE.exists():
        raise FileNotFoundError(f"{RAW_FILE} not found (see docs/data_sources.md).")

    frames = []
    for year, sheet in year_sheets().items():
        df, _ = read_year(year, sheet)
        id_cols = ["year", "nlc", "Station", "Note"] + (["Borough"] if "Borough" in df else [])
        long = df.melt(id_vars=id_cols, value_vars=list(VALUE_COLS),
                       var_name="column", value_name="value")
        long["measure"] = long["column"].map(lambda c: VALUE_COLS[c][0])
        long["day_name"] = long["column"].map(lambda c: VALUE_COLS[c][1])

        # Validation: every original value appears exactly once in the long table.
        assert len(long) == len(df) * len(VALUE_COLS)
        assert abs(long["value"].sum() - df[list(VALUE_COLS)].sum().sum()) < 1e-6

        # Flag stations with zero counts on every day type in that year.
        daily = long.groupby("nlc")["value"].transform("sum")
        long["zero_all_day"] = daily.eq(0)
        frames.append(long)
        print(f"  {year}: {len(df)} stations -> {len(long):,} rows")

    df = pd.concat(frames, ignore_index=True)

    # Station names are stored with trailing spaces in some years: strip them.
    df["station"] = df["Station"].str.strip()

    # Borough is only given in 2014-2017. Station boroughs do not change over
    # time, so fill earlier years from the most recent year available.
    if "Borough" in df:
        borough = (df.dropna(subset=["Borough"]).sort_values("year")
                     .groupby("nlc")["Borough"].last())
        df["borough"] = df["nlc"].map(borough)

    # Translate note codes into readable flags; add zero-day and linkage flags.
    df["Note"] = df["Note"].fillna("")
    flags = df["Note"].map(note_flags)
    numbat_nlc = set()
    if NUMBAT_STATIONS.exists():
        numbat_nlc = set(pd.read_csv(NUMBAT_STATIONS, usecols=["nlc"])["nlc"].unique())
    flags = [
        f + (["zero_all_day"] if zero and "station_closed" not in f else [])
          + (["not_in_numbat_2025"] if numbat_nlc and nlc not in numbat_nlc else [])
        for f, zero, nlc in zip(flags, df["zero_all_day"], df["nlc"])
    ]
    df["scope_note"] = [";".join(dict.fromkeys(f)) for f in flags]

    df["source"] = "LU_entry_exit_counts"
    df["day_type"] = df["day_name"].map(lambda d: DAY_CODES[d][0])
    df["day_label"] = df["day_name"].map(lambda d: DAY_CODES[d][1])
    df["time_slot"] = "full_day"
    df["time_band"] = "Full day"
    df["in_scope"] = True
    df["note_raw"] = df["Note"]

    cols = ["source", "year", "day_type", "day_label", "nlc", "station", "borough",
            "time_slot", "time_band", "measure", "value", "in_scope", "scope_note", "note_raw"]
    df = df[cols].sort_values(["year", "nlc", "day_type", "measure"]).reset_index(drop=True)
    assert not df.duplicated(["year", "nlc", "day_type", "measure"]).any()

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    print(f"\n{OUT_FILE.name}: {len(df):,} rows, {df['nlc'].nunique()} stations, "
          f"{df['year'].min()}-{df['year'].max()}")
    counts = df.assign(flag=df["scope_note"].str.split(";")).explode("flag")
    counts = counts[counts["flag"] != ""].groupby("flag")[["nlc", "year"]].apply(
        lambda g: len(g.drop_duplicates()))
    print("Station-years by flag:")
    for flag, n in counts.items():
        print(f"  {flag}: {n}")


if __name__ == "__main__":
    main()
