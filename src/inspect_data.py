"""
Data audit for the TfL NUMBAT typical-day outputs.

This script only LOOKS at the raw data. It never changes or saves the raw
files. It answers the questions from our cleaning checklist before any
cleaning decision is made:

    1. Look        - what is one row? how many rows and columns?
    2. Blanks      - are any cells empty?
    3. Duplicates  - is any row (or row ID) in the table twice?
    4. Types       - are numbers stored as numbers?
    5. Impossible  - are there negative passenger counts?
    6. Consistency - do the 96 quarter-hours add up to the daily Total?
    7. Linkage     - do station / link IDs match the NUMBAT Definitions file?

Usage (from the repository root, with the .venv activated):

    python src/inspect_data.py              # audit Monday only (default)
    python src/inspect_data.py --day TWT    # audit one day type
    python src/inspect_data.py --day all    # audit all five day types

The result is printed and also written to reports/audit_numbat_<DAY>.md
"""

import argparse
import re
from datetime import date
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Paths: everything is relative to the repository root, so the script works
# on any computer where the repository is cloned.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
REPORT_DIR = REPO_ROOT / "reports"
DEFINITIONS_FILE = RAW_DIR / "PTSP Oasis for NUMBAT definitions.xlsx"

DAY_TYPES = ["MON", "TWT", "FRI", "SAT", "SUN"]

# The seven daily time bands that come before the 15-minute columns.
TIME_BANDS = ["Early", "AM Peak", "Midday", "PM Peak", "Evening", "Late"]

# Column(s) that should identify one row uniquely in each sheet.
ROW_ID = {
    "Link_Loads": ["Link"],
    "Link_Frequencies": ["Link"],
    "Line_Boarders": ["Line Code"],
    "Station_Flows": ["ID"],
    "Station_Entries": ["NLC"],
    "Station_Exits": ["NLC"],
    # Platform IDs are shared by lines that use the same platform
    # (e.g. Met / Circle / H&C at Barbican), so the row ID is ID + Line.
    "Station_Boarders": ["ID", "Line"],
    "Station_Alighters": ["ID", "Line"],
}

# Tolerance when comparing sums: NUMBAT values are model estimates with many
# decimals, so tiny rounding differences are expected.
SUM_TOLERANCE = 0.01

QHR_PATTERN = re.compile(r"^\d{4}-\d{4}$")  # e.g. "0500-0515"


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------
def read_numbat_sheet(path: Path, sheet: str) -> pd.DataFrame:
    """Read one NUMBAT sheet.

    Each sheet has three header rows: hour, quarter-hour number, and the real
    column names. We use the third row (index 2) as the header.
    """
    df = pd.read_excel(path, sheet_name=sheet, header=2)
    df.columns = [str(c).strip() for c in df.columns]
    return df


def split_columns(df: pd.DataFrame) -> tuple[list, list, list]:
    """Split columns into: identifier columns, time-band columns, 15-min columns."""
    cols = list(df.columns)
    total_pos = cols.index("Total")
    id_cols = cols[:total_pos]
    qhr_cols = [c for c in cols if QHR_PATTERN.match(c)]
    band_cols = [c for c in cols[total_pos:] if c not in qhr_cols]
    return id_cols, band_cols, qhr_cols


# ---------------------------------------------------------------------------
# Checks for one sheet
# ---------------------------------------------------------------------------
def audit_sheet(df: pd.DataFrame, sheet: str) -> dict:
    id_cols, band_cols, qhr_cols = split_columns(df)
    value_cols = band_cols + qhr_cols
    result = {"sheet": sheet, "rows": len(df), "columns": df.shape[1]}

    # 1. Structure
    result["id_columns"] = id_cols
    result["band_columns"] = band_cols
    result["n_qhr"] = len(qhr_cols)
    result["qhr_first_last"] = (qhr_cols[0], qhr_cols[-1]) if qhr_cols else None

    # 2. Blanks
    blanks = df.isna().sum()
    result["blank_cells_total"] = int(blanks.sum())
    result["blank_by_column"] = {c: int(n) for c, n in blanks.items() if n > 0}

    # Rows that are not data: completely empty rows, and summary rows such as
    # a network "TOTAL" line (summing the sheet would then double count).
    result["empty_rows"] = int(df.isna().all(axis=1).sum())
    is_summary = df[id_cols].astype(str).apply(
        lambda col: col.str.strip().str.upper().eq("TOTAL")).any(axis=1)
    result["summary_rows"] = int(is_summary.sum())

    # 3. Duplicates
    result["duplicate_rows"] = int(df.duplicated().sum())
    key = ROW_ID.get(sheet)
    if key and all(k in df.columns for k in key):
        result["row_id"] = key
        result["duplicate_ids"] = int(df.duplicated(subset=key).sum())

    # 4. Types: every value column should be numeric
    non_numeric = {}
    for c in value_cols:
        converted = pd.to_numeric(df[c], errors="coerce")
        n_bad = int(converted.isna().sum() - df[c].isna().sum())
        if n_bad:
            non_numeric[c] = n_bad
    result["non_numeric_cells"] = non_numeric
    values = df[value_cols].apply(pd.to_numeric, errors="coerce")

    # 5. Impossible values: negative counts
    result["negative_cells"] = int((values < 0).sum().sum())
    result["rows_total_zero"] = int((values["Total"] == 0).sum())

    # 6. Consistency: 96 quarter-hours vs Total, and the 6 bands vs Total
    total = values["Total"]
    qhr_sum = values[qhr_cols].sum(axis=1)
    band_sum = values[[b for b in TIME_BANDS if b in values.columns]].sum(axis=1)
    result["qhr_vs_total_mismatch"] = int(((qhr_sum - total).abs() > SUM_TOLERANCE).sum())
    result["qhr_vs_total_max_diff"] = float((qhr_sum - total).abs().max())
    result["bands_vs_total_mismatch"] = int(((band_sum - total).abs() > SUM_TOLERANCE).sum())
    result["bands_vs_total_max_diff"] = float((band_sum - total).abs().max())

    # Basic description of the daily totals
    result["total_sum"] = float(total.sum())
    result["total_describe"] = total.describe().round(1).to_dict()
    return result


# ---------------------------------------------------------------------------
# Checks across sheets
# ---------------------------------------------------------------------------
def audit_cross_sheet(sheets: dict, definitions: dict | None) -> dict:
    out = {}

    # Entries vs exits for the whole network should be close (each journey
    # enters once and exits once), but not identical: some journeys start or
    # end on non-TfL services.
    ent = sheets["Station_Entries"]["Total"].sum()
    ext = sheets["Station_Exits"]["Total"].sum()
    out["entries_total"] = float(ent)
    out["exits_total"] = float(ext)
    out["exits_minus_entries_pct"] = float((ext - ent) / ent * 100)

    # Link loads and link frequencies should describe the same links.
    loads = set(sheets["Link_Loads"]["Link"])
    freqs = set(sheets["Link_Frequencies"]["Link"])
    out["links_only_in_loads"] = len(loads - freqs)
    out["links_only_in_frequencies"] = len(freqs - loads)

    # Links with passengers but no trains (would make passengers-per-train
    # impossible to compute), and links with trains but no passengers.
    ll = sheets["Link_Loads"].set_index("Link")["Total"]
    lf = sheets["Link_Frequencies"].set_index("Link")["Total"]
    both = ll.index.intersection(lf.index)
    out["links_load_but_no_trains"] = int(((ll[both] > 0) & (lf[both] == 0)).sum())
    out["links_trains_but_no_load"] = int(((ll[both] == 0) & (lf[both] > 0)).sum())

    if definitions is not None:
        # Station IDs: NUMBAT uses NLC codes. The Definitions file lists master
        # NLCs and also child NLCs that map to a master station.
        known_nlc = set(definitions["Stations"]["MasterNLC"]) | set(
            definitions["NLC-MNLC"]["ChildNLC"]
        )
        stations = set(sheets["Station_Entries"]["NLC"])
        missing = sorted(stations - known_nlc)
        out["stations_not_in_definitions"] = len(missing)
        out["stations_not_in_definitions_examples"] = missing[:10]

        # Link IDs: NUMBAT link codes end with "@LINE"; the Definitions file
        # stores the same code without that suffix.
        known_links = set(definitions["LinksRail"]["LinkCode"])
        numbat_links = {str(x).split("@")[0] for x in loads}
        missing_links = sorted(numbat_links - known_links)
        out["links_not_in_definitions"] = len(missing_links)
        out["links_not_in_definitions_examples"] = missing_links[:10]
    return out


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
def fmt(x) -> str:
    if isinstance(x, float):
        return f"{x:,.2f}"
    if isinstance(x, int):
        return f"{x:,}"
    return str(x)


def build_report(day: str, path: Path, sheet_results: list, cover: list, cross: dict) -> str:
    lines = [
        f"# NUMBAT 2025 audit: {day}",
        "",
        f"_Generated by `src/inspect_data.py` on {date.today().isoformat()} "
        f"from `{path.name}`. Raw data were read only, never modified._",
        "",
        "## Cover sheet",
        "",
    ]
    lines += [f"- {c}" for c in cover[:4]]

    lines += [
        "",
        "## Sheet overview",
        "",
        "| Sheet | Rows | Row ID | Duplicate rows | Duplicate IDs | Empty / TOTAL rows | "
        "Blank cells | Non-numeric cells | Negative cells | Rows with Total = 0 | "
        "15-min ≠ Total | Bands ≠ Total |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in sheet_results:
        lines.append(
            f"| {r['sheet']} | {fmt(r['rows'])} | {' + '.join(r.get('row_id', []))} | "
            f"{fmt(r['duplicate_rows'])} | {fmt(r.get('duplicate_ids', 'n/a'))} | "
            f"{r['empty_rows']} / {r['summary_rows']} | {fmt(r['blank_cells_total'])} | "
            f"{fmt(sum(r['non_numeric_cells'].values()))} | {fmt(r['negative_cells'])} | "
            f"{fmt(r['rows_total_zero'])} | {fmt(r['qhr_vs_total_mismatch'])} | "
            f"{fmt(r['bands_vs_total_mismatch'])} |"
        )

    lines += ["", "## Sheet details", ""]
    for r in sheet_results:
        d = r["total_describe"]
        lines += [
            f"### {r['sheet']}",
            "",
            f"- Identifier columns: {', '.join(r['id_columns'])}",
            f"- Time-band columns: {', '.join(r['band_columns'])}",
            f"- 15-minute columns: {r['n_qhr']} ({r['qhr_first_last'][0]} … {r['qhr_first_last'][1]})",
            f"- Blank cells: {fmt(r['blank_cells_total'])} in {len(r['blank_by_column'])} columns"
            + (" (all from empty rows)" if r['blank_cells_total'] == r['empty_rows'] * r['columns'] else ""),
            f"- Empty rows: {r['empty_rows']}; summary (TOTAL) rows: {r['summary_rows']}",
            f"- Largest |sum of 15-min − Total|: {fmt(r['qhr_vs_total_max_diff'])}; "
            f"largest |sum of bands − Total|: {fmt(r['bands_vs_total_max_diff'])}",
            f"- Daily Total: sum {fmt(r['total_sum'])}; median {fmt(d['50%'])}; "
            f"max {fmt(d['max'])}",
            "",
        ]

    lines += [
        "## Cross-sheet checks",
        "",
        f"- Network entries: {fmt(cross['entries_total'])}; exits: {fmt(cross['exits_total'])} "
        f"(exits − entries = {cross['exits_minus_entries_pct']:.2f}% of entries)",
        f"- Links only in Link_Loads: {cross['links_only_in_loads']}; "
        f"only in Link_Frequencies: {cross['links_only_in_frequencies']}",
        f"- Links with passengers but zero trains: {cross['links_load_but_no_trains']}",
        f"- Links with trains but zero passengers: {cross['links_trains_but_no_load']}",
    ]
    if "stations_not_in_definitions" in cross:
        lines += [
            f"- Station NLCs not found in Definitions file: {cross['stations_not_in_definitions']} "
            f"(examples: {cross['stations_not_in_definitions_examples'] or 'none'})",
            f"- Link codes not found in Definitions file: {cross['links_not_in_definitions']} "
            f"(examples: {cross['links_not_in_definitions_examples'] or 'none'})",
        ]
    else:
        lines.append("- Definitions file not found: ID linkage not checked.")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def audit_day(day: str, definitions: dict | None) -> str:
    path = RAW_DIR / f"NBT25{day}_Outputs.xlsx"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found. Download it (see docs/data_sources.md) "
            "and put it in data/raw/."
        )
    print(f"Reading {path.name} ...")
    cover_df = pd.read_excel(path, sheet_name="_Cover", header=None)
    cover = [str(v) for v in cover_df.values.flatten() if pd.notna(v)]

    sheets, results = {}, []
    for sheet in ROW_ID:
        df = read_numbat_sheet(path, sheet)
        sheets[sheet] = df
        results.append(audit_sheet(df, sheet))
        print(f"  checked {sheet}: {len(df):,} rows")

    cross = audit_cross_sheet(sheets, definitions)
    report = build_report(day, path, results, cover, cross)

    REPORT_DIR.mkdir(exist_ok=True)
    out_path = REPORT_DIR / f"audit_numbat_{day}.md"
    out_path.write_text(report, encoding="utf-8")
    print(f"Report written to {out_path.relative_to(REPO_ROOT)}\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit NUMBAT 2025 typical-day outputs.")
    parser.add_argument("--day", default="MON", choices=DAY_TYPES + ["all"],
                        help="Day type to audit (default: MON)")
    args = parser.parse_args()

    definitions = None
    if DEFINITIONS_FILE.exists():
        print("Reading Definitions file ...")
        definitions = pd.read_excel(
            DEFINITIONS_FILE, sheet_name=["Stations", "NLC-MNLC", "LinksRail"]
        )
    else:
        print("Definitions file not found: ID linkage checks will be skipped.")

    days = DAY_TYPES if args.day == "all" else [args.day]
    for day in days:
        report = audit_day(day, definitions)
        if len(days) == 1:
            print(report)


if __name__ == "__main__":
    main()
