"""Step 4: build one small table per part of the story.

Reads the cleaned tables from steps 1-3 and writes to data/processed/:

    part0_growth_2007_2017.csv   all Underground stations: typical-weekday
                                 entries + exits in 2007 and 2017
    part0_trend_by_zone.csv      London-wide typical-weekday entries + exits by
                                 year (2018-2025) and fare zone
    part1_stratford_growth.csv   Stratford Underground station, typical-day
                                 entries and exits, 2007-2017
    part2_station_trends.csv     the five study stations, typical-day entries
                                 and exits by year (2018-2025) and time band
    part3_train_crowding.csv     crowding on trains next to Stratford, by hour,
                                 typical 2025 weekday
    part4_daily_pressure.csv     the five study stations on every day of 2025,
                                 compared with their usual level
    part4_busiest_days.csv       the 15 days of 2025 when a nearby station was
                                 busiest compared with usual, and Stratford on
                                 the same days

Columns are explained in docs/data.md.

Run from the repository root:
    python src/4_make_tables.py
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
NEARBY = ["Stratford International", "Stratford High Street", "Pudding Mill Lane", "Hackney Wick"]
TIME_BANDS = ["Early", "AM Peak", "Midday", "PM Peak", "Evening", "Late", "Whole day"]
EVENT_YEAR = 2025
BASE_YEAR = 2019  # comparison year for Parts 0 and 2
MIN_WEEKDAY_2007 = 5000   # Part 0: leave out very small stations
ZONE_GROUPS = {"1": "Zone 1", "2": "Zone 2", "3": "Zones 3-4", "4": "Zones 3-4",
               "5": "Zones 5-6", "6": "Zones 5-6"}

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
# Yap, Wong & Cats (2023): in-vehicle time is weighted by (1 + 0.42 x standing passengers per m2).
CROWDING_WEIGHT = 0.42
# Sensitivity checks: average of pre-2020 studies quoted in that paper, and the
# approximate 95% interval of 0.42 (from its t-value of 2.21).
OTHER_WEIGHTS = {"feels_like_pre_2020_studies": 0.22, "feels_like_low": 0.05, "feels_like_high": 0.79}


def part0_growth() -> pd.DataFrame:
    df = pd.read_csv(DATA / "entry_exit_2007_2017.csv")
    df = df[(df["day_type"] == "weekday") & df["year"].isin([2007, 2017])].copy()
    df["total"] = df["entries"] + df["exits"]
    wide = df.pivot_table(index=["nlc", "station"], columns="year", values="total").dropna().reset_index()
    wide = wide[wide[2007] >= MIN_WEEKDAY_2007].rename(columns={2007: "total_2007", 2017: "total_2017"})
    wide["increase"] = wide["total_2017"] - wide["total_2007"]
    wide["ratio"] = (wide["total_2017"] / wide["total_2007"]).round(2)
    wide[["total_2007", "total_2017", "increase"]] = wide[["total_2007", "total_2017", "increase"]].astype(int)
    wide = wide.sort_values("increase", ascending=False)
    wide["rank_by_increase"] = range(1, len(wide) + 1)
    return wide[["rank_by_increase", "station", "total_2007", "total_2017", "increase", "ratio"]]


def zone_group(zone: str) -> str:
    first = zone.split("/")[0]
    if first in ZONE_GROUPS:
        return ZONE_GROUPS[first]
    return "Outside Zone 6" if first.isdigit() else "Other"


def part0_trend() -> pd.DataFrame:
    df = pd.read_csv(DATA / "numbat_stations.csv", usecols=["year", "day_type", "fare_zone",
                                                            "entries", "exits"])
    df = df[df["day_type"] == "weekday"].copy()
    df["zone_group"] = df["fare_zone"].astype(str).map(zone_group)
    by_zone = df.groupby(["year", "zone_group"], as_index=False)[["entries", "exits"]].sum()
    london = df.groupby("year", as_index=False)[["entries", "exits"]].sum()
    london["zone_group"] = "All London"
    out = pd.concat([london, by_zone], ignore_index=True)
    out = out[out["zone_group"] != "Other"]
    out["total"] = out["entries"] + out["exits"]
    base = out[out["year"] == BASE_YEAR].set_index("zone_group")["total"]
    out["vs_2019"] = (out["total"] / out["zone_group"].map(base)).round(2)
    out["total"] = out["total"].round().astype(int)
    return out[["year", "zone_group", "total", "vs_2019"]].sort_values(["zone_group", "year"])


def part1() -> pd.DataFrame:
    df = pd.read_csv(DATA / "entry_exit_2007_2017.csv")
    df = df[df["nlc"] == STRATFORD].copy()
    df["total"] = df["entries"] + df["exits"]
    return df[["year", "day_type", "entries", "exits", "total"]].sort_values(["day_type", "year"])


def part2() -> pd.DataFrame:
    df = pd.read_csv(DATA / "numbat_stations.csv")
    df = df[df["nlc"].isin(STUDY_STATIONS)]
    keys = ["year", "day_type", "nlc"]
    by_band = df.groupby(keys + ["time_band"], as_index=False)[["entries", "exits"]].sum()
    whole_day = df.groupby(keys, as_index=False)[["entries", "exits"]].sum()
    whole_day["time_band"] = "Whole day"
    out = pd.concat([by_band, whole_day], ignore_index=True)
    out["station"] = out["nlc"].map(STUDY_STATIONS)
    out["total"] = out["entries"] + out["exits"]
    # Compare each year with the same station, day type and time band in 2019.
    base = out[out["year"] == BASE_YEAR].set_index(["day_type", "nlc", "time_band"])["total"]
    out["vs_2019"] = out["total"] / out.set_index(["day_type", "nlc", "time_band"]).index.map(base)
    out[["entries", "exits", "total"]] = out[["entries", "exits", "total"]].round().astype(int)
    out["vs_2019"] = out["vs_2019"].round(2)
    out["time_band"] = pd.Categorical(out["time_band"], TIME_BANDS, ordered=True)
    out = out.sort_values(["day_type", "station", "time_band", "year"])
    return out[["year", "day_type", "station", "time_band", "entries", "exits", "total", "vs_2019"]]


def part3() -> pd.DataFrame:
    df = pd.read_csv(DATA / "numbat_links.csv")
    df = df.copy()
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
    for column, weight in OTHER_WEIGHTS.items():
        out[column] = 10 * (1 + weight * out["standing_per_m2"])

    out["order"] = (out["hour"] - 5) % 24  # NUMBAT's day starts at 05:00
    out["hour"] = out["hour"].map(lambda h: f"{h:02d}:00-{(h + 1) % 24:02d}:00")
    out = out.sort_values(["line", "direction", "order"])
    out["passengers"] = out["passengers"].round().astype(int)
    out = out.round({"passengers_per_train": 0, "standing_per_m2": 2, "ten_minutes_feels_like": 1,
                     **{column: 1 for column in OTHER_WEIGHTS}})
    out["passengers_per_train"] = out["passengers_per_train"].astype(int)
    return out[["line", "from", "to", "direction", "hour", "passengers", "trains",
                "passengers_per_train", "seats", "standing_per_m2", "ten_minutes_feels_like",
                *OTHER_WEIGHTS]]


def part4_daily() -> pd.DataFrame:
    df = pd.read_csv(DATA / "footfall_daily.csv", parse_dates=["date"])
    df = df[df["station"].isin(STUDY_STATIONS.values()) & (df["date"].dt.year == EVENT_YEAR)].copy()
    df["total"] = df["entries"] + df["exits"]
    # A day with no taps at all means the station was closed or data are missing,
    # not that nobody travelled: leave it out of the comparison.
    df = df[df["total"] > 0]
    # "Usual" = the station's median on the same day of the week over the year.
    df["usual"] = df.groupby(["station", "day_of_week"])["total"].transform("median")
    df["pressure_index"] = (df["total"] / df["usual"]).round(2)
    df["extra_passengers"] = (df["total"] - df["usual"]).round().astype(int)
    df["level"] = pd.cut(df["pressure_index"], [0, 1.5, 2.0, float("inf")], right=False,
                         labels=["normal", "elevated", "extreme"])
    df["date"] = df["date"].dt.date
    return df[["date", "day_of_week", "station", "entries", "exits", "total", "usual",
               "pressure_index", "extra_passengers", "level"]].sort_values(["date", "station"])


def part4_busiest(daily: pd.DataFrame) -> pd.DataFrame:
    index = daily.pivot_table(index=["date", "day_of_week"], columns="station", values="pressure_index")
    extra = daily.pivot_table(index=["date", "day_of_week"], columns="station", values="extra_passengers")
    out = pd.DataFrame(index=index.index)
    out["busiest_nearby"] = index[NEARBY].idxmax(axis=1)
    out["busiest_nearby_index"] = index[NEARBY].max(axis=1)
    out["busiest_nearby_extra"] = [extra.loc[i, s] for i, s in out["busiest_nearby"].items()]
    out["stratford_index"] = index["Stratford"]
    out["stratford_extra"] = extra["Stratford"]
    for station in NEARBY:
        out[f"{station}_index"] = index[station]
    out = out.reset_index().sort_values("busiest_nearby_index", ascending=False).head(15)
    out["busiest_nearby_extra"] = out["busiest_nearby_extra"].round().astype("Int64")
    out["stratford_extra"] = out["stratford_extra"].round().astype("Int64")
    return out


def main() -> None:
    daily = part4_daily()
    for name, build in [("part0_growth_2007_2017.csv", part0_growth),
                        ("part0_trend_by_zone.csv", part0_trend),
                        ("part1_stratford_growth.csv", part1),
                        ("part2_station_trends.csv", part2),
                        ("part3_train_crowding.csv", part3),
                        ("part4_daily_pressure.csv", lambda: daily),
                        ("part4_busiest_days.csv", lambda: part4_busiest(daily))]:
        table = build()
        table.to_csv(DATA / name, index=False)
        print(f"{name}: {len(table)} rows")


if __name__ == "__main__":
    main()
