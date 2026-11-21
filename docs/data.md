# Data

This page explains which data we use, where they come from, how they are processed, and what each table contains.

## 1. Datasets

| Dataset | What it tells us | Used in | Status |
|---|---|---|---|
| Underground station entry/exit counts, 2007–2017 | How many people pass through each Underground station's gates on a typical weekday, Saturday and Sunday, each year | Part 1 | In use |
| NUMBAT 2025 | TfL's model of a typical 2025 day: people entering and leaving every station, and passengers and trains on every stretch of track, in 15-minute steps | Parts 2 and 3 | In use |
| NUMBAT 2018–2024 | The same for earlier years | Part 2 | To download |
| TfL station footfall | Entries and exits per station on real dates, including event days | Part 4 | To download |

### What each dataset cannot show

- **NUMBAT describes a typical day, not real dates.** TfL leaves out days with disruption, events or closures, and assumes every train runs on time. It cannot show what happens on a match day; Part 4 needs the station footfall data for that.
- **NUMBAT values are modelled estimates**, which is why they have decimals. The 2007–2017 figures are gate counts. The two cannot be joined into one trend line.
- **The 2007–2017 counts cover Underground gates only**, not the DLR, Overground or Elizabeth line.

## 2. Sources and licences

### Underground station entry/exit counts, 2007–2017

- **Publisher:** Transport for London, via the London Datastore
- **Page:** <https://data.london.gov.uk/dataset/london-underground-performance-reports-em8qy> (file "Entry and exit figures by station")
- **File:** `multi-year-station-entry-and-exit-figures.xls`
- **Licence:** Open Government Licence v2.0
- **Attribution:** "Contains public sector information licensed under the Open Government Licence v2.0."
- **Downloaded:** 16 November 2026

### NUMBAT 2025

- **Publisher:** Transport for London
- **Folder:** <https://crowding.data.tfl.gov.uk/#!NUMBAT%2FNUMBAT%202025%2F>
- **Files:** `NBT25MON_Outputs.xlsx`, `NBT25TWT_Outputs.xlsx`, `NBT25FRI_Outputs.xlsx`, `NBT25SAT_Outputs.xlsx`, `NBT25SUN_Outputs.xlsx`
- **Licence:** TfL Transport Data Service terms (<https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service>), based on the Open Government Licence v2.0 with TfL amendments. Use requires registering with TfL's open data service (done 17 November 2026) and must not suggest TfL endorsement.
- **Attribution:** "Powered by TfL Open Data."
- **Downloaded:** 16 November 2026

Earlier NUMBAT years are in the same folder structure and under the same licence.

### Raw files are not in this repository

Raw files are kept out of the repository because of their size (about 64 MB). Download them from the links above into `data/raw/`, keeping the original file names.

## 3. Processing

Four scripts, run in order from the repository root:

```
python src/1_clean_numbat.py
python src/2_clean_entry_exit.py
python src/3_make_tables.py
python src/4_make_figures.py
```

| Step | Script | Reads | Writes |
|---|---|---|---|
| 1 | `1_clean_numbat.py` | 5 NUMBAT 2025 files | `numbat_stations.csv`, `numbat_links.csv` |
| 2 | `2_clean_entry_exit.py` | 2007–2017 entry/exit file | `entry_exit_2007_2017.csv` |
| 3 | `3_make_tables.py` | the three files above | `part1_stratford_growth.csv`, `part2_station_demand.csv`, `part3_train_crowding.csv` |
| 4 | `4_make_figures.py` | the part tables | `figures/part1_stratford_growth.png`, `figures/part3_train_crowding.png` |

All tables are written to `data/processed/`, which is not in the repository. Raw files are never changed.

### What the cleaning does

**NUMBAT (step 1)**
- The original sheets have one row per station and 96 columns, one per 15 minutes. The script turns them into one row per station per 15 minutes.
- It checks that the 15-minute values add up to the daily totals published in the file.
- It leaves out tram stops and tram lines, which NUMBAT does not model (their values are all zero).

**Entry/exit counts (step 2)**
- The original file has one sheet per year, with title rows above and formatting rows below the table. The script keeps only the station rows and stacks the years into one table.
- It translates the letter notes in the file into words, e.g. `A` = "estimated from previous year". Stratford has no notes in any year.

### Checks worth knowing about

- **Both datasets passed basic checks:** no blank cells, no negative values, no duplicated stations, and totals add up.
- **Passengers per train are calculated per hour, not per 15 minutes.** Each train is counted in only one 15-minute slot, so the number of trains per slot jumps (e.g. 4, 2, 4, 2) while passenger numbers change smoothly. Per 15 minutes, some Elizabeth line trains would appear to carry over 1,700 people, more than a train holds. Per hour, the highest value next to Stratford is 1,299, below the capacity of about 1,500.
- **The Elizabeth line standing area is an estimate.** TfL publishes 1,043 standing places per train but not the floor area; we assume about 4 people per m², giving about 261 m².

## 4. Tables

### Cleaned tables (steps 1 and 2)

These are large and are only used as inputs to step 3.

**`numbat_stations.csv`** — one row = one station, one day type, one 15-minute slot (207,360 rows)

| Column | Meaning |
|---|---|
| `day_type` | `monday`, `tue_thu` (Tuesday to Thursday), `friday`, `saturday`, `sunday` |
| `nlc` | TfL station number (e.g. Stratford = 719). Use it to match stations, because names vary between files. |
| `station` | Station name |
| `time` | Start of the 15-minute slot, e.g. `08:15`. NUMBAT's day runs from 05:00 to 04:59. |
| `time_band` | `Early` 05–07, `AM Peak` 07–10, `Midday` 10–16, `PM Peak` 16–19, `Evening` 19–22, `Late` 22–05 |
| `entries` / `exits` | People entering / leaving the station in that slot (modelled) |

**`numbat_links.csv`** — one row = one stretch of track between two neighbouring stations, in one direction, one day type, one 15-minute slot (548,640 rows)

| Column | Meaning |
|---|---|
| `day_type`, `time`, `time_band` | As above |
| `line` | Line name |
| `link` | TfL's code for the stretch of track |
| `from_station` / `to_station` | The two stations it connects |
| `direction` | TfL's direction code (e.g. `EB` eastbound, `WB` westbound) |
| `passengers` | Passengers travelling along it in that slot |
| `trains` | Trains running along it in that slot |

**`entry_exit_2007_2017.csv`** — one row = one Underground station, one year, one day type (8,859 rows)

| Column | Meaning |
|---|---|
| `year` | 2007–2017 |
| `nlc`, `station` | As above |
| `day_type` | `weekday`, `saturday`, `sunday` |
| `entries` / `exits` | People entering / leaving through the gates on a typical day (counted) |
| `note` | Publisher's note, in words (blank if none) |

### Part tables (step 3)

Small tables, one per part of the story. These are the tables to share with the team and to use for figures.

**`part1_stratford_growth.csv`** — Stratford Underground station, typical day, 2007–2017 (33 rows)

| Column | Meaning |
|---|---|
| `year`, `day_type` | As above |
| `entries`, `exits`, `total` | People entering, leaving, and both together |

**`part2_station_demand.csv`** — the five study stations, typical day, by time band (2025 only for now; 105 rows)

| Column | Meaning |
|---|---|
| `year` | 2025 (earlier years to be added) |
| `day_type` | `tue_thu`, `saturday`, `sunday` |
| `station` | Stratford, Stratford International, Stratford High Street, Pudding Mill Lane, Hackney Wick |
| `time_band` | As above, plus `Whole day` |
| `entries`, `exits`, `total` | People entering, leaving, and both together |

**`part3_train_crowding.csv`** — trains next to Stratford, typical 2025 Tuesday–Thursday, by hour (119 rows)

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
| `ten_minutes_feels_like` | How long a 10-minute ride feels at that crowding: 10 × (1 + 0.42 × `standing_per_m2`), from Yap, Wong & Cats (2023). Not extra clock time. |

## 5. Attribution for anything we publish

- Powered by TfL Open Data.
- Contains public sector information licensed under the Open Government Licence v2.0.
