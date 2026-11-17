# Data Audit

**Status:** NUMBAT 2025 audited; historical files not yet audited  
**Last Updated:** 17 November 2026

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

## 5. Not yet audited

- `multi-year-station-entry-and-exit-figures.xls` (2007–2017). Its sheets have inconsistent sizes (e.g. 2008 has 14,263 rows), it contains extra `workings` and `Sheet1` sheets, and some values are estimated (note "A").
- `lu-performance-data.xlsx` and `tfl-tube-performance.xlsx`.

These will be audited before they are used in the combined dataset.
