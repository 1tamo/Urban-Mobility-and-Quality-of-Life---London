# Data

This page explains which data we use, where they come from, how they are processed, and what each table contains.

## 1. Datasets

| Dataset | What it tells us | Used in |
|---|---|---|
| Underground station entry/exit counts, 2007–2017 | How many people pass through each Underground station's gates on a typical weekday, Saturday and Sunday, each year | Parts 0 and 1 |
| NUMBAT 2018–2025 | TfL's model of a typical day each year: people entering and leaving every station in 15-minute steps; for 2025 also passengers and trains on every stretch of track | Parts 0, 2 and 3 |
| TfL station footfall | Entries and exits per station on every real date, including event days | Part 4 |

### What each dataset cannot show

- **NUMBAT describes a typical day, not real dates.** TfL leaves out days with disruption, events or closures. It cannot show what happens on a match day; Part 4 uses station footfall for that.
- **NUMBAT values are modelled estimates**, which is why they have decimals. The 2007–2017 figures are gate counts and station footfall is card taps. The three cannot be joined into one trend line.
- **The 2007–2017 counts cover Underground gates only**, not the DLR, Overground or Elizabeth line.
- **Station footfall counts taps.** At DLR stations without ticket gates, some passengers do not tap, so footfall can be lower than real use.

## 2. Sources and licences

### Underground station entry/exit counts, 2007–2017

- **Publisher:** Transport for London, via the London Datastore
- **Page:** <https://data.london.gov.uk/dataset/london-underground-performance-reports-em8qy> (file "Entry and exit figures by station")
- **File:** `multi-year-station-entry-and-exit-figures.xls`
- **Licence:** Open Government Licence v2.0
- **Attribution:** "Contains public sector information licensed under the Open Government Licence v2.0."
- **Downloaded:** 16 November 2026

### NUMBAT 2018–2025

- **Publisher:** Transport for London
- **Location:** <https://crowding.data.tfl.gov.uk/>, folder `NUMBAT`, one subfolder per year
- **Files used:** for each year, the weekday, Saturday and Sunday files, e.g. `NBT25TWT_Outputs.xlsx`, `NBT25SAT_Outputs.xlsx`, `NBT25SUN_Outputs.xlsx`. The weekday file is `MTT` (Monday–Thursday) up to 2021 and `TWT` (Tuesday–Thursday) from 2022.
- **Licence:** TfL Transport Data Service terms (<https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service>), based on the Open Government Licence v2.0 with TfL amendments. Use requires registering with TfL's open data service (done 17 November 2026) and must not suggest TfL endorsement.
- **Attribution:** "Powered by TfL Open Data."
- **Downloaded:** 2025 on 16 November 2026; 2018–2024 on 22 November 2026

### TfL station footfall

- **Publisher:** Transport for London
- **Page:** <https://tfl.gov.uk/corporate/publications-and-reports/network-demand-data> ("Station footfall documents")
- **Files:** `StationFootfall_2023.csv`, `StationFootfall_2025_2026 .csv` (the second file name contains a space before `.csv`, as downloaded)
- **Coverage:** every day, 1 January–31 December 2023 and 1 January 2025–14 November 2026. 2024 is not covered by these files.
- **Licence:** published by TfL as open data; treated as covered by the same TfL Transport Data Service terms as NUMBAT. The page asks users to read TfL's Data Guide before use.
- **Attribution:** "Powered by TfL Open Data."
- **Downloaded:** 22 November 2026

### Station locations (our own reference data)

- **File:** `data/station_locations.csv`, kept in the repository.
- **Content:** latitude and longitude of the five study stations, copied from each station's Wikipedia page (link in the file), checked 25 November 2026.

### Background map

- **Source:** OpenStreetMap map tiles (<https://tile.openstreetmap.org>), downloaded by step 6 on its first run and kept in `data/processed/tiles/`.
- **Licence:** map data © OpenStreetMap contributors, Open Database Licence (ODbL). The attribution is printed on every map. We download only the 24 tiles needed, once, as allowed by the OpenStreetMap tile usage policy.

### Event calendar (our own data)

- **File:** `data/events_calendar.csv`, kept in the repository because we make it ourselves.
- **Columns:** `date`, `venue`, `event_type`, `event_name`, `attendance`, `source_url`.
- **Status:** started. It is used to explain the busiest days in Part 4.

### Raw files are not in this repository

Raw files are kept out of the repository because of their size. Download them from the links above into `data/raw/`, keeping the original file names.

## 3. Processing

Six scripts, run in order from the repository root:

```
python src/1_clean_numbat.py
python src/2_clean_entry_exit.py
python src/3_clean_footfall.py
python src/4_make_tables.py
python src/5_make_figures.py
python src/6_make_map.py
```

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `1_clean_numbat.py` | NUMBAT 2018–2025 files | `numbat_stations.csv`, `numbat_links.csv` |
| 2 | `2_clean_entry_exit.py` | 2007–2017 entry/exit file | `entry_exit_2007_2017.csv` |
| 3 | `3_clean_footfall.py` | station footfall files | `footfall_daily.csv` |
| 4 | `4_make_tables.py` | the four files above | one table per part (`part0_…` to `part4_…`) |
| 5 | `5_make_figures.py` | the part tables | six figures in `figures/` |
| 6 | `6_make_map.py` | `part2_station_trends.csv`, `station_locations.csv`, OpenStreetMap tiles | `figures/part2_map.gif`, `figures/part2_map_2025.png`, `docs/part2_map.html` |

All tables are written to `data/processed/`, which is not in the repository. Raw files are never changed.

### What the cleaning does

**NUMBAT (step 1)**
- The original sheets have one row per station and 96 columns, one per 15 minutes. The script turns them into one row per station per 15 minutes.
- It checks that the 15-minute values add up to the daily totals published in the file.
- It leaves out tram stops and tram lines, which NUMBAT does not model (their values are all zero).

**Entry/exit counts (step 2)**
- The original file has one sheet per year, with title rows above and formatting rows below the table. The script keeps only the station rows and stacks the years into one table.
- It translates the letter notes in the file into words, e.g. `A` = "estimated from previous year". Stratford has no notes in any year.

**Station footfall (step 3)**
- Joins the files into one table and turns dates such as `20250518` into `2025-05-18`.

### Things to know when reading the results

- **Passengers per train are calculated per hour, not per 15 minutes.** Each train is counted in only one 15-minute slot, so the number of trains per slot jumps (e.g. 4, 2, 4, 2) while passenger numbers change smoothly. Per hour, the highest value next to Stratford is 1,299 per train, below the capacity of about 1,500.
- **The Elizabeth line standing area is an estimate.** TfL publishes 1,043 standing places per train but not the floor area; we assume about 4 people per m², giving about 261 m².
- **The NUMBAT weekday changed definition in 2022**, from Monday–Thursday to Tuesday–Thursday.
- **Stratford's 2025 Saturday total in NUMBAT equals its 2024 total** to within one passenger, although the 15-minute values differ. TfL probably reused the 2024 count, so the 2024–2025 Saturday change at Stratford should not be read as real.
- **Pudding Mill Lane jumps in NUMBAT from 2022** (2–3× on weekdays and 6–8× at weekends compared with 2019). The cause is not yet known; it may be real growth around the station or a change in how TfL models it. Treat it with caution until checked.
- **Days with no taps** at a station in the footfall data mean the station was closed or data are missing. They are left out of Part 4. A few days have very low counts (shown as about 0× usual), which suggests the station was closed for most of the day.
- **Small stations swing more.** Stratford High Street usually has under 2,000 entries + exits a day, so a few hundred extra people double it. Part 4 therefore reports extra passengers as well as the ratio.

## 4. Tables

### Cleaned tables (steps 1–3)

These are large and are only used as inputs to step 4.

**`numbat_stations.csv`** — one row = one station, one year, one day type, one 15-minute slot

| Column | Meaning |
|---|---|
| `year` | 2018–2025 |
| `day_type` | `weekday`, `saturday`, `sunday` |
| `nlc` | TfL station number (e.g. Stratford = 719). Use it to match stations, because names vary between files. |
| `station` | Station name |
| `fare_zone` | Fare zone as written by TfL, e.g. `1`, `2/3` (on a boundary) |
| `time` | Start of the 15-minute slot, e.g. `08:15`. NUMBAT's day runs from 05:00 to 04:59. |
| `time_band` | `Early` 05–07, `AM Peak` 07–10, `Midday` 10–16, `PM Peak` 16–19, `Evening` 19–22, `Late` 22–05 |
| `entries` / `exits` | People entering / leaving the station in that slot (modelled) |

**`numbat_links.csv`** — one row = one stretch of track between two neighbouring stations, in one direction, typical 2025 weekday, one 15-minute slot

| Column | Meaning |
|---|---|
| `line` | Line name |
| `link` | TfL's code for the stretch of track |
| `from_station` / `to_station` | The two stations it connects |
| `direction` | TfL's direction code (e.g. `EB` eastbound, `WB` westbound) |
| `time`, `time_band` | As above |
| `passengers` / `trains` | Passengers / trains on it in that slot |

**`entry_exit_2007_2017.csv`** — one row = one Underground station, one year, one day type

| Column | Meaning |
|---|---|
| `year` | 2007–2017 |
| `nlc`, `station` | As above |
| `day_type` | `weekday`, `saturday`, `sunday` |
| `entries` / `exits` | People entering / leaving through the gates on a typical day (counted) |
| `note` | Publisher's note, in words (blank if none) |

**`footfall_daily.csv`** — one row = one station on one real date

| Column | Meaning |
|---|---|
| `date` | e.g. `2025-05-18` |
| `day_of_week` | e.g. `Sunday` |
| `station` | Station name |
| `entries` / `exits` | Card taps in / out that day |

### Part tables (step 4)

Small tables, one per part of the story. These are the tables to share with the team and to use for figures.

**`part0a_london_by_zone.csv`** — all stations, typical weekday, 2018–2025

| Column | Meaning |
|---|---|
| `year` | 2018–2025 |
| `zone_group` | `All London`, `Zone 1`, `Zone 2`, `Zones 3-4`, `Zones 5-6`, `Outside Zone 6`. Stations on a boundary (e.g. `2/3`) are counted in the lower zone. |
| `total` | Typical-weekday entries + exits |
| `vs_2019` | `total` ÷ the same group in 2019 |

**`part0b_station_growth.csv`** — all Underground stations with at least 5,000 typical-weekday entries + exits in 2007 (238 stations)

| Column | Meaning |
|---|---|
| `rank_by_increase` | 1 = largest increase |
| `station` | Station name |
| `total_2007` / `total_2017` | Typical-weekday entries + exits |
| `increase` | `total_2017` − `total_2007` |
| `ratio` | `total_2017` ÷ `total_2007` |

**`part1_stratford_growth.csv`** — Stratford Underground station, typical day, 2007–2017

| Column | Meaning |
|---|---|
| `year`, `day_type` | As above |
| `entries`, `exits`, `total` | People entering, leaving, and both together |

**`part2_station_trends.csv`** — the five study stations, typical day, 2018–2025

| Column | Meaning |
|---|---|
| `year`, `day_type` | As above |
| `station` | Stratford, Stratford International, Stratford High Street, Pudding Mill Lane, Hackney Wick |
| `time_band` | As above, plus `Whole day` |
| `entries`, `exits`, `total` | People entering, leaving, and both together |
| `vs_2019` | `total` ÷ the same station, day type and time band in 2019. 1.0 = same as 2019. |

**`part3_train_crowding.csv`** — trains next to Stratford, typical 2025 weekday, by hour

| Column | Meaning |
|---|---|
| `line` | Central, Elizabeth line, Jubilee |
| `from`, `to` | The stretch of track, e.g. Stratford → Mile End |
| `direction` | `leaving Stratford` or `arriving at Stratford` |
| `hour` | e.g. `08:00-09:00` |
| `passengers`, `trains` | Passengers and trains in that hour |
| `passengers_per_train` | Average people on each train |
| `seats` | Seats per train |
| `standing_per_m2` | People standing per m² of floor; 0 means everyone can sit |
| `ten_minutes_feels_like` | How long a 10-minute ride feels at that crowding: 10 × (1 + 0.42 × `standing_per_m2`), from Yap, Wong & Cats (2023; see section 5). Not extra clock time. |
| `feels_like_pre_2020_studies` | The same with 0.22, the average of pre-2020 studies quoted in that paper |
| `feels_like_low` / `feels_like_high` | The same with 0.05 / 0.79, the approximate 95% interval of 0.42 |

**`part4_daily_pressure.csv`** — the five study stations on every day of 2025

| Column | Meaning |
|---|---|
| `date`, `day_of_week`, `station`, `entries`, `exits` | As in `footfall_daily.csv` |
| `total` | `entries` + `exits` |
| `usual` | The station's median `total` on the same day of the week in 2025 |
| `pressure_index` | `total` ÷ `usual`. 2.0 = twice the usual number of people. |
| `extra_passengers` | `total` − `usual` |
| `level` | `normal` (below 1.5), `elevated` (1.5 to 2), `extreme` (2 or more). These thresholds are our choice, not safety limits. |

**`part4_busiest_days.csv`** — the 15 days of 2025 when a nearby station was busiest compared with usual

| Column | Meaning |
|---|---|
| `date`, `day_of_week` | The day |
| `busiest_nearby` | The nearby station with the highest pressure index that day |
| `busiest_nearby_index` / `busiest_nearby_extra` | Its pressure index / extra passengers |
| `stratford_index` / `stratford_extra` | Stratford's pressure index / extra passengers on the same day |
| `<station>_index` | Pressure index of each nearby station that day (blank if no data) |

## 5. Crowding valuation used in Part 3

- **Source:** Yap, M., Wong, H. & Cats, O. (2023). Public transport crowding valuation in a post-pandemic era. *Transportation*, 52, 287–306 (2025 issue). <https://doi.org/10.1007/s11116-023-10420-1> (open access)
- **What it estimates:** how much worse a minute on a crowded train feels, from 20,970 observed route choices on the Central and Victoria lines, 13–17 June 2022, using Oyster/contactless and train load-weigh data.
- **Result used:** in-vehicle time × (1 + 0.42 × standing passengers per m²), counted from when the train is fully seated (t = 2.21).
- **Limits:** we cannot re-estimate it, because the individual journey and train-weight data are not public. Observed densities in the study did not exceed 3 per m². Part 3 therefore also reports results with 0.22 and with 0.05–0.79 (section 4).

## 6. Attribution for anything we publish

- Powered by TfL Open Data.
- Contains public sector information licensed under the Open Government Licence v2.0.
- Maps: Map data © OpenStreetMap contributors.
