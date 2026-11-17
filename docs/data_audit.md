# Data Audit

**Status:** NUMBAT 2025 and LU entry/exit counts 2007–2017 audited and cleaned; performance data not yet audited  
**Last Updated:** 18 November 2026

## 1. Purpose and method

This document records what the raw data actually contain before any cleaning, and the cleaning decision taken for each issue found.

The audit was produced by `src/inspect_data.py`. The script reads the raw files without modifying them and writes one report per day type to `reports/audit_numbat_<DAY>.md`. To reproduce it:

```
python src/inspect_data.py --day all
```

The checks follow a standard cleaning checklist:

1. Structure: what one row represents.
2. Blank cells.
3. Duplicate rows and duplicate row IDs.
4. Numbers stored as text.
5. Impossible (negative) values.
6. Internal consistency: whether the 15-minute values and the time bands each add up to the daily Total.
7. Linkage of station and link IDs to the NUMBAT Definitions file.

## 2. NUMBAT 2025: structure

All five day-type files (`MON`, `TWT`, `FRI`, `SAT`, `SUN`) have identical structure; only the values differ.

| Sheet | Rows | One row represents | Unique row ID |
|---|---|---|---|
| `Station_Entries` / `Station_Exits` | 471 | a station | `NLC` |
| `Station_Boarders` / `Station_Alighters` | 1,166 | a platform × line | `ID` + `Line` |
| `Station_Flows` | 5,627 | a movement between two points inside a station | `ID` (not fully unique; see 3.2) |
| `Link_Loads` / `Link_Frequencies` | 1,214 | a link between two adjacent stations, one direction | `Link` |
| `Line_Boarders` | 21 | a line (plus an empty row and a network TOTAL row) | `Line Code` |

Each sheet has three header rows (hour, quarter-hour number, column names). Columns are identifier columns, then a daily `Total`, six time bands (`Early`, `AM Peak`, `Midday`, `PM Peak`, `Evening`, `Late`), and 96 15-minute columns from `0500-0515` to `0445-0500`. The traffic day runs from 05:00 to 04:59.

Platform IDs in `Station_Boarders` / `Station_Alighters` are not unique on their own. Lines that share a platform (e.g. Metropolitan and Hammersmith & City at Barbican) each have their own row with the same platform `ID`.

## 3. NUMBAT 2025: findings

### 3.1 Checks passed (all sheets, all day types)

- No blank cells, apart from one empty row in `Line_Boarders`.
- No numbers stored as text; no negative values.
- The 96 15-minute values sum exactly to `Total`, and so do the six time bands.
- Every `Link` appears in both `Link_Loads` and `Link_Frequencies`. No link has passengers but zero trains, so passengers per train can be computed wherever there is a load.
- All 471 station NLC codes are found in the Definitions file.
- Network exits differ from entries by less than 0.2% on every day type, so the data are internally consistent.

### 3.2 Issues found

| # | Sheet | Finding | Explanation |
|---|---|---|---|
| A | `Line_Boarders` | 1 empty row and 1 `TOTAL` row (network sum) | Summing the sheet would double count. |
| B | `Station_Entries` / `Exits` / `Boarders` / `Alighters` | 39 stations have zero demand all day on every day type | All 39 are **London Trams** stops (ASC codes ending in `t`). Trams are not modelled in NUMBAT 2025: the `_Cover` sheet lists LU, LO, DLR and Elizabeth line only. |
| C | `Link_Loads` / `Link_Frequencies` | 79 links have zero passengers and zero trains all day | 71 are London Trams links. The other 8 are branch connector links with no scheduled service in 2025 (DLR at Canning Town / Canary Wharf, LO Weaver at Hackney Downs, Northern line at Kennington). |
| D | `Station_Flows` | 13 rows are exact duplicates; another 15 rows share an `ID` with a different node name but identical values | These occur at a few interchanges, mostly involving National Rail nodes (Clapham Junction, London Bridge, King's Cross). The extra exact copies are 0.03% of total flow. |
| E | `Link_Loads` vs Definitions | 10 link codes are not in the Definitions file | The Definitions file is the 2024 version. The unmatched links match the changes listed on the 2025 `_Cover` sheet (Metropolitan fast/semi-fast links), plus the branch connectors in C. |

## 4. Cleaning decisions

| Issue | Decision | Reason |
|---|---|---|
| A | Drop the empty row and the `TOTAL` row from `Line_Boarders`. | They are not line observations. |
| B | Keep London Trams stations in the cleaned tables, flagged `in_scope = False` with reason `trams_not_modelled`. Exclude them from analyses by default. | Their zeros mean "not modelled", not "no passengers": they must not enter averages or rankings as real zeros. Keeping them, rather than deleting them, preserves the full station list. |
| C | Keep all 79 links. Flag the 71 tram links `in_scope = False` (`trams_not_modelled`) and the 8 others `no_service`. | Tram links are out of scope. For the others, zero reflects the timetable and is a valid value. |
| D | Drop the 13 exact duplicate rows. Keep the 15 same-ID rows unchanged for now and flag them. | `Station_Flows` is not used in the first analyses; revisit if it becomes relevant. |
| E | No change. Join link attributes (e.g. distance) only where codes match, and report the unmatched links. | The links are valid 2025 links missing from an older reference file. |
| Structure | Use `ID` + `Line` as the key for platform-level sheets. | Shared platforms. |

**Why the zeros are not station closures.** A station with zero demand all day could indicate a closure in other data sources. In NUMBAT 2025 this is not possible: days affected by closures are excluded and a full scheduled service is assumed. All 39 zero-demand stations are tram stops, which NUMBAT 2025 does not model. Closures and disruptions should be studied with calendar-date data (e.g. TfL Network Demand station footfall), which is relevant to H3/H4.

General rules for all cleaning:
- Raw files are never modified.
- Cleaning is done by a script and written to `data/processed/`.
- Rows are flagged rather than deleted wherever possible.
- Every removed or flagged row is counted in the cleaning output.

## 5. Cleaning implementation

The decisions above are implemented in `src/clean_numbat.py`. The script writes three tables to `data/processed/` (local only, not uploaded) and a log to `reports/cleaning_log_numbat2025.md`.

| Output | One row represents | Rows |
|---|---|---|
| `station_demand_long.csv` (master table) | station × day type × 15-min slot × measure (entries / exits) | 452,160 |
| `link_demand_long.csv` | link × day type × 15-min slot (passengers, trains, passengers per train) | 582,720 |
| `camden_town_detail.csv` | Camden Town × day type × 15-min slot (entries, exits, boarders / alighters by platform) | 480 |

Validation built into the script:
- For every station, link and day type, the reshaped 15-minute values sum back to the original daily `Total`.
- Key columns have no duplicates.

No rows are removed. Tram stations and links are flagged `in_scope = False`; links without trains in a day type are flagged `no_service`. `Line_Boarders` and `Station_Flows` are not used in these outputs.

**Open item for Pilot 03.** A few Elizabeth line links show more than 1,500 passengers per train in the morning peak (maximum 1,787, Stratford → Whitechapel). That is above the plausible capacity of a train. The cause may be how trains are counted on links where branches merge. Passengers per train must be checked before it is used as a pressure indicator.

## 6. Historical LU station entry/exit counts (2007–2017)

Audited by `src/inspect_entry_exit.py` (report: `reports/audit_entry_exit_2007_2017.md`) and cleaned by `src/clean_entry_exit.py`. Both scripts read the file through `src/entry_exit_common.py`, so they handle it in exactly the same way.

### 6.1 Structure

- One sheet per year (2007–2017). Each row is one LU station in one year: typical-day counts for Weekday, Saturday and Sunday, for entries and exits, plus an annual total in millions.
- These are **counts** (measured), whereas NUMBAT values are **modelled** estimates. Each source has its own day types: here a single "Weekday"; NUMBAT has `MON`/`TWT`/`FRI`.
- The rows include 268–273 stations. Overground, DLR and Elizabeth line stations are not covered.
- Other sheets are not used:
  - `Notes` (documentation only);
  - `workings` (the publisher's intermediate calculations);
  - `Sheet1`, a pasted table of station facts (opening dates, lines) that appears to be copied from a third-party web page and is not TfL count data.

### 6.2 Findings

- **Checks passed:** no blanks, no text in number columns, no negative values and no duplicate NLCs. For every station and year, the annual figure equals the documented weighting (253 × weekday + 52 × Saturday + 59 × Sunday, entries + exits). All 268 stations open in 2017 are found in NUMBAT 2025.
- **Formatting issues:**
  - Station names have trailing spaces in some years.
  - The 2008 sheet has about 14,000 formatting-only rows below the table.
  - The publisher's total row is labelled in some years, unlabelled in others, and missing in 2015.
- **Publisher totals:** in 2013 and 2016 the total row does not match the sum of the station rows (differences up to 9,691).
- **Note codes:**
  - `A` (estimated from the previous year): 59 station-years.
  - `N`/`Closed` (station closed): 4.
  - `T`/`B` (Waterloo & City line effects).
  - `C` and `D` appear in 2016–2017 but are **not explained** in the file.
- **Zero counts on all days:** these are real closures, e.g. Shoreditch 2007, Blackfriars 2009–2011 (rebuilding), Edgware Road (Bakerloo) 2013, Tufnell Park 2015 and Lambeth North 2016. Some are not marked `N`.
- **Coverage changes:**
  - Seven former East London line stations appear only in 2007; the line closed in December 2007 and later reopened as part of the Overground.
  - Wood Lane and Heathrow Terminal 5 appear from 2008.
- **Borough:** only given in 2014–2017.

### 6.3 Cleaning decisions

| Issue | Decision |
|---|---|
| Header, formatting and total rows | Keep station rows only (rows with a numeric NLC). Use station rows rather than the publisher's totals, which are inconsistent in 2013 and 2016. |
| Trailing spaces | Strip station names. |
| Note codes | Keep the raw code (`note_raw`) and translate it into readable flags in `scope_note`. Undocumented codes become `undocumented_note_C` / `undocumented_note_D`. |
| Estimated values (`A`) | Keep, flagged `estimated_from_previous_year`. Analyses of change over time should test sensitivity to excluding them. |
| Zero counts | Keep. Flag `station_closed` (if noted) or `zero_all_day`. These zeros carry real information about closures. |
| Stations not in NUMBAT 2025 | Keep, flagged `not_in_numbat_2025`. |
| Borough | Fill 2007–2013 from the most recent year available for the same NLC (station boroughs do not change). |

### 6.4 Camden Town: evidence of a station access restriction

In every year from 2007 to 2017, Sunday **exits** at Camden Town are about 1.5–2.1 times Sunday **entries** (e.g. 2014: 33,767 exits vs 17,679 entries). On Saturdays the two are close.

This is consistent with the station being exit-only on Sunday afternoons to prevent crowding. According to the London Underground Railway Society (Newsflash NF 22/19), it became fully open on Sundays from 6 January 2019. In NUMBAT 2025, Sunday entries and exits are similar (25,909 vs 27,773).

This makes Camden Town a candidate case for H3/H4 (an access restriction associated with a redistribution of departures to other stations), alongside the 2025 pedestrianisation. The restriction dates still need confirmation from an official TfL source.

## 7. Combined master table

`src/build_master.py` combines the cleaned NUMBAT 2025 station table and the cleaned LU counts into `data/processed/station_demand_master.csv`: 469,878 rows covering 2007–2017 (counts) and 2025 (NUMBAT).

Two columns must be used whenever rows from different sources are compared:
- `measurement`: `modelled` or `counted`.
- `temporal_resolution`: `15min` or `full_day`.

NUMBAT 2025 and the LU counts differ in method, day-type definitions and station coverage. Differences between them are therefore not automatically real changes in demand.

## 8. Not yet audited

- `lu-performance-data.xlsx` and `tfl-tube-performance.xlsx` (line-level performance).
- NUMBAT 2016–2024 (not yet downloaded; NUMBAT 2024 is needed for the Camden before/after comparison).

## 9. Decision log

Every decision that changed, flagged or excluded data, in the order it was applied, with its effect. This list summarises sections 4, 6.3 and 7; each decision is documented in full there.

**General rules**
- Raw files are never modified. All cleaning is done by scripts that write to `data/processed/`.
- Problematic rows are flagged rather than deleted. **Rows deleted across all cleaning: 0.**

**NUMBAT 2025** (`src/clean_numbat.py`; log: `reports/cleaning_log_numbat2025.md`)
1. Used only the station entry/exit, platform boarders/alighters, link load and link frequency sheets. `Line_Boarders` (empty row + TOTAL row) and `Station_Flows` (13 exact duplicate rows, 15 same-ID rows) are not used in the outputs, so those issues did not need fixing.
2. Reshaped the 96 15-minute columns into rows (wide → long) for all five day types. Checked that the reshaped values sum back to each original daily `Total`: all matched (maximum difference 0.0000).
3. Kept 39 London Trams stations and 71 tram links, flagged `in_scope = False`, `trams_not_modelled`. NUMBAT 2025 does not model trams, so their zeros are not real zeros.
4. Kept links with no trains in a day type, flagged `no_service`: 14 distinct links across the five day types (8 on weekdays, more at weekends).
5. Added link distance from the 2024 Definitions file where link codes match. 10 links (2025 network changes) have no distance.
6. Used `ID` + `Line` as the key for platform-level data, because shared platforms appear once per line.
7. Computed `passengers_per_train` only where at least one train runs; otherwise blank. Values above 1,500 on some Elizabeth line links are kept but must be checked before use.

**LU station entry/exit counts 2007–2017** (`src/clean_entry_exit.py`)
8. Ignored the `Notes`, `workings` and `Sheet1` sheets (documentation, intermediate calculations and a third-party station table).
9. Kept station rows only (numeric NLC). Dropped title, weight and formatting rows, including about 14,000 empty formatting rows in 2008, and the publisher's total rows. The total rows are inconsistent with the station rows in 2013 and 2016.
10. Stripped trailing spaces from station names.
11. Reshaped each year's six value columns into rows. Checked that every original value appears exactly once, with an identical sum.
12. Kept the raw note code (`note_raw`) and translated it into flags. Station-years affected:
    - `estimated_from_previous_year`: 59
    - `station_closed`: 4
    - `includes_waterloo_city_line`: 9
    - `bank_excludes_waterloo_city_interchange`: 8
    - `undocumented_note_C`: 3
    - `undocumented_note_D`: 3
13. Flagged 4 station-years with zero counts on all days that are not marked as closed (`zero_all_day`). Kept the zeros: they reflect real closures.
14. Flagged 7 former East London line stations (2007 only) as `not_in_numbat_2025`.
15. Filled `borough` for 2007–2013 from the most recent year available for the same NLC.

**Master table** (`src/build_master.py`)
16. Combined NUMBAT 2025 (452,160 rows) and the LU counts (17,718 rows) into `station_demand_master.csv` (469,878 rows). Checked that the row count equals the sum of the inputs and that keys are unique.
17. Added `measurement` (`modelled` / `counted`) and `temporal_resolution` (`15min` / `full_day`) so that rows from different methods are never compared unknowingly.
18. Filled missing station attributes across sources by NLC: borough for NUMBAT stations (from LU counts), and ASC code and fare zone for LU stations (from NUMBAT).
