"""
Combine all cleaned station-level demand tables into one master table.

Inputs (created by the cleaning scripts):
    data/processed/station_demand_long.csv          (NUMBAT 2025, 15-minute)
    data/processed/lu_entry_exit_2007_2017_long.csv (LU counts, full day)

Output:
    data/processed/station_demand_master.csv
    One row per source x year x day type x station x time slot x measure.

The sources differ in method and resolution, so two columns make this
explicit and must be used when comparing rows from different sources:
    measurement           "modelled" (NUMBAT) or "counted" (LU counts)
    temporal_resolution   "15min" or "full_day"

Usage (from the repository root, with the .venv activated):

    python src/build_master.py
"""

import pandas as pd

from entry_exit_common import REPO_ROOT

PROCESSED = REPO_ROOT / "data" / "processed"
SOURCES = {
    "station_demand_long.csv": {"measurement": "modelled", "temporal_resolution": "15min"},
    "lu_entry_exit_2007_2017_long.csv": {"measurement": "counted", "temporal_resolution": "full_day"},
}
COLUMNS = ["source", "measurement", "temporal_resolution", "year", "day_type",
           "day_label", "nlc", "asc", "station", "borough", "fare_zone",
           "time_slot", "slot_index", "slot_start", "time_band", "measure",
           "value", "in_scope", "scope_note"]
OUT_FILE = PROCESSED / "station_demand_master.csv"


def main() -> None:
    parts = []
    for name, extra in SOURCES.items():
        path = PROCESSED / name
        if not path.exists():
            raise FileNotFoundError(f"{path} not found: run the cleaning scripts first.")
        df = pd.read_csv(path, dtype={"fare_zone": str})
        for col, value in extra.items():
            df[col] = value
        parts.append(df)
        print(f"  {name}: {len(df):,} rows")

    master = pd.concat(parts, ignore_index=True)

    # Fill station attributes that only one source provides, by NLC:
    # borough (from LU counts) and ASC code / fare zone (from NUMBAT).
    for col in ["borough", "asc", "fare_zone"]:
        lookup = master.dropna(subset=[col]).drop_duplicates("nlc", keep="last").set_index("nlc")[col]
        master[col] = master[col].fillna(master["nlc"].map(lookup))

    master = master[COLUMNS]
    key = ["source", "year", "day_type", "nlc", "time_slot", "measure"]
    assert not master.duplicated(key).any(), "Duplicate keys in master table"
    assert len(master) == sum(len(p) for p in parts)

    master.to_csv(OUT_FILE, index=False)
    print(f"\n{OUT_FILE.name}: {len(master):,} rows")
    print(master.groupby(["source", "measurement", "temporal_resolution"])
                .agg(rows=("value", "size"), years=("year", lambda y: f"{y.min()}-{y.max()}"),
                     stations=("nlc", "nunique")).to_string())


if __name__ == "__main__":
    main()
