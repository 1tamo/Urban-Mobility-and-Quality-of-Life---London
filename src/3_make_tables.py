"""Step 3: build one small table per part of the story.

Reads the cleaned tables from steps 1 and 2 and writes to data/processed/:

    part1_stratford_growth.csv   Stratford Underground station, typical-day
                                 entries and exits, 2007-2017
    part2_station_demand.csv     the five study stations, typical-day entries
                                 and exits by time band (currently 2025 only)
    part3_train_crowding.csv     crowding on trains next to Stratford, by hour,
                                 typical 2025 Tuesday-Thursday

Columns are explained in docs/data.md.

Run from the repository root:
    python src/3_make_tables.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed"

STRATFORD = 719
STUDY_STATIONS = {  # station code (NLC): name
    719: "Stratford",
    504: "Stratford International",
    749: "Stratford High Street",
    859: "Pudding Mill Lane",
    6978: "Hackney Wick",
}
TIME_BANDS = ["Early", "AM Peak", "Midday", "PM Peak", "Evening", "Late", "Whole day"]

# Seats and standing floor area per train (TfL rolling stock data sheets).
# Elizabeth line: 1,043 standing places at about 4 people per m2 (estimate).
TRAINS = {
    "Central": (272, 155.02),
    "Jubilee": (234, 145.92),
    "Elizabeth line": (454, 1043 / 4),
}
# Links next to Stratford: (line, from, to, direction relative to Stratford).
LINKS = [
    ("Central", "Stratford", "Mile End", "leaving Stratford"),
    ("Central", "Mile End", "Stratford", "arriving at Stratford"),
    ("Elizabeth line", "Stratford", "Whitechapel", "leaving Stratford"),
    ("Elizabeth line", "Whitechapel", "Stratford", "arriving at Stratford"),
    ("Jubilee", "Stratford", "West Ham", "leaving Stratford"),
    ("Jubilee", "West Ham", "Stratford", "arriving at Stratford"),
]
LINE_NAMES = {"Central": "Central", "Jubilee": "Jubilee", "Elizabeth Line": "Elizabeth line"}
CROWDING_WEIGHT = 0.42  # Yap, Wong & Cats (2023): per standing passenger per m2


def part1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "entry_exit_2007_2017.csv")
    df = df[df["nlc"] == STRATFORD].copy()
    df["total"] = df["entries"] + df["exits"]
    return df[["year", "day_type", "entries", "exits", "total"]].sort_values(["day_type", "year"])


def part2() -> pd.DataFrame:
    df = pd.read_csv(DATA / "numbat_stations.csv")
    df = df[df["nlc"].isin(STUDY_STATIONS) & df["day_type"].isin(["tue_thu", "saturday", "sunday"])]
    by_band = df.groupby(["day_type", "nlc", "time_band"], as_index=False)[["entries", "exits"]].sum()
    whole_day = df.groupby(["day_type", "nlc"], as_index=False)[["entries", "exits"]].sum()
    whole_day["time_band"] = "Whole day"
    out = pd.concat([by_band, whole_day], ignore_index=True)
    out["year"] = 2025
    out["station"] = out["nlc"].map(STUDY_STATIONS)
    out["total"] = out["entries"] + out["exits"]
    out[["entries", "exits", "total"]] = out[["entries", "exits", "total"]].round().astype(int)
    out["time_band"] = pd.Categorical(out["time_band"], TIME_BANDS, ordered=True)
    out = out.sort_values(["day_type", "station", "time_band"])
    return out[["year", "day_type", "station", "time_band", "entries", "exits", "total"]]


def part3() -> pd.DataFrame:
    df = pd.read_csv(DATA / "numbat_links.csv")
    df = df[df["day_type"] == "tue_thu"].copy()
    df["line"] = df["line"].map(LINE_NAMES)
    df = df.rename(columns={"from_station": "from", "to_station": "to"}).drop(columns="direction")
    wanted = pd.DataFrame(LINKS, columns=["line", "from", "to", "direction"])
    df = df.merge(wanted, on=["line", "from", "to"])
    assert df.groupby(["line", "from", "to"]).ngroups == len(LINKS), "a link is missing"

    # Passengers per train are worked out per hour, not per 15 minutes: each train
    # is counted in only one 15-minute slot, so 15-minute values jump up and down.
    df["hour"] = df["time"].str[:2].astype(int)
    out = df.groupby(["line", "from", "to", "direction", "hour"], as_index=False)[
        ["passengers", "trains"]].sum()
    out = out[out["trains"] > 0].copy()  # leave out night hours with no trains
    out["passengers_per_train"] = out["passengers"] / out["trains"]
    out["seats"] = out["line"].map(lambda l: TRAINS[l][0])
    floor = out["line"].map(lambda l: TRAINS[l][1])
    out["standing_per_m2"] = ((out["passengers_per_train"] - out["seats"]).clip(lower=0) / floor)
    out["ten_minutes_feels_like"] = 10 * (1 + CROWDING_WEIGHT * out["standing_per_m2"])

    out["order"] = (out["hour"] - 5) % 24  # NUMBAT's day starts at 05:00
    out["hour"] = out["hour"].map(lambda h: f"{h:02d}:00-{(h + 1) % 24:02d}:00")
    out = out.sort_values(["line", "direction", "order"])
    out["passengers"] = out["passengers"].round().astype(int)
    out = out.round({"passengers_per_train": 0, "standing_per_m2": 2, "ten_minutes_feels_like": 1})
    out["passengers_per_train"] = out["passengers_per_train"].astype(int)
    return out[["line", "from", "to", "direction", "hour", "passengers", "trains",
                "passengers_per_train", "seats", "standing_per_m2", "ten_minutes_feels_like"]]


def main() -> None:
    for name, build in [("part1_stratford_growth.csv", part1),
                        ("part2_station_demand.csv", part2),
                        ("part3_train_crowding.csv", part3)]:
        table = build()
        table.to_csv(DATA / name, index=False)
        print(f"{name}: {len(table)} rows")


if __name__ == "__main__":
    main()
