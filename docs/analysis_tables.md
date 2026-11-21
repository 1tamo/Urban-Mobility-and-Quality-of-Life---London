# Analysis Tables

**Last Updated:** 22 November 2026

This page describes the small tables used to draw the project's figures. Each table answers one question and can be described in one sentence.

They are built from the base tables produced by the cleaning scripts. The base tables (`station_demand_long.csv`, `link_demand_long.csv`, `lu_entry_exit_2007_2017_long.csv`) are large and in long format. They are inputs for analysis, not for presentation.

All analysis tables are saved in `data/processed/` with the prefix `stratford_` (plus `events_calendar.csv`). Like other data files, they are not committed to Git.

## Overview

| Table | One row = | Used in |
|---|---|---|
| `stratford_entry_exit_2007_2017.csv` | Stratford LU station, one year, one day type | Part 1 |
| `stratford_area_numbat.csv` | One study station, one year, one day type | Part 2 |
| `stratford_crowding_2025.csv` | One line, one direction, one hour, leaving or arriving at Stratford | Part 3 |
| `stratford_area_daily.csv` | One study station, one date | Part 4 |
| `events_calendar.csv` | One event at a venue near the Park, one date | Part 4 |

## 1. `stratford_entry_exit_2007_2017.csv`

Typical-day entries and exits at Stratford LU station, 2007–2017.

| Column | Type | Description |
|---|---|---|
| `year` | int | 2007–2017 |
| `day_type` | text | `weekday`, `saturday`, `sunday` |
| `entries` | float | Typical-day entries |
| `exits` | float | Typical-day exits |
| `total` | float | `entries` + `exits` |

Source: LU station entry/exit counts 2007–2017 (London Datastore). Covers LU gates only, not other modes at Stratford.

## 2. `stratford_area_numbat.csv`

Typical-day demand at the five study stations, by year.

| Column | Type | Description |
|---|---|---|
| `year` | int | 2018–2025 (2016–2017 if comparable) |
| `day_type` | text | `weekday`, `saturday`, `sunday` |
| `station` | text | Study station name |
| `nlc` | int | Station code |
| `period` | text | Time period chosen for the heatmap (e.g. `AM Peak`, `Total`) |
| `entries` | float | Modelled entries in that period |
| `exits` | float | Modelled exits in that period |
| `total` | float | `entries` + `exits` |
| `index_2019` | float | `total` ÷ the same station's 2019 value (2019 = 1.0) |

Source: NUMBAT typical-day outputs. "Weekday" uses `TWT` (Tuesday–Thursday) where available. 2020–2021 are pandemic years.

## 3. `stratford_crowding_2025.csv`

Average on-board crowding on the links next to Stratford, by hour.

| Column | Type | Description |
|---|---|---|
| `line` | text | `Central`, `Elizabeth`, `Jubilee` |
| `link` | text | e.g. `Stratford → Mile End` |
| `direction` | text | `from_stratford`, `to_stratford` |
| `hour` | text | e.g. `08:00–09:00` |
| `passengers` | float | Passengers on the link in that hour |
| `trains` | int | Trains on the link in that hour |
| `passengers_per_train` | float | `passengers` ÷ `trains` |
| `seats` | int | Seats per train |
| `standing_area_m2` | float | Standing area per train |
| `standing_density` | float | (`passengers_per_train` − `seats`) ÷ `standing_area_m2`; 0 if seats are not full |
| `perceived_min_per_10` | float | Perceived time of a 10-minute ride: 10 × (1 + 0.42 × `standing_density`) |

Sources: NUMBAT 2025 `TWT` link loads and frequencies; TfL rolling stock information sheets; Yap, Wong & Cats (2023). The Elizabeth line standing area is an estimate (see `docs/research_design.md`, section 8).

## 4. `stratford_area_daily.csv`

Daily demand at the study stations, compared with each station's normal level.

| Column | Type | Description |
|---|---|---|
| `date` | date | YYYY-MM-DD |
| `day_of_week` | text | `Mon` … `Sun` |
| `station` | text | Study station name |
| `entries` | int | Entries that day |
| `exits` | int | Exits that day |
| `total` | int | `entries` + `exits` |
| `median_same_dow` | float | Median `total` for the same station and day of the week, over the same year |
| `pressure_index` | float | `total` ÷ `median_same_dow` |
| `extra_passengers` | float | `total` − `median_same_dow` |
| `pressure_level` | text | `normal` (< 1.5), `elevated` (≥ 1.5), `extreme` (≥ 2.0) |
| `event_flag` | bool | True if `events_calendar.csv` lists an event that day |
| `event_name` | text | Event name(s), blank otherwise |

Source: TfL Network Demand station footfall files. Thresholds are analytical choices, not safety limits.

## 5. `events_calendar.csv`

Events near the Park that may affect demand. Built by hand from public sources.

| Column | Type | Description |
|---|---|---|
| `date` | date | YYYY-MM-DD |
| `venue` | text | e.g. `London Stadium` |
| `event_type` | text | `football`, `concert`, `athletics`, `marathon`, `other` |
| `event_name` | text | e.g. `West Ham v ...` |
| `attendance` | int | Reported attendance, blank if unknown |
| `source_url` | text | Where the event was confirmed |
