# Data folder

Raw and processed data files are **not** stored in this repository (`data/raw/` and `data/processed/` are git-ignored). Each person keeps a local copy. This page explains where the data come from and how to add new data.

```
data/
├── README.md        ← this file (tracked by Git)
├── raw/             ← original downloads, never edited (local only)
└── processed/       ← outputs of the cleaning scripts (local only)
```

## Getting the existing data

1. Download each file listed in `docs/data_sources.md` (section 3.2) from its official URL into `data/raw/`. Keep the original file names.
2. With the virtual environment activated, run the cleaning scripts from the repository root:

```
python src/clean_numbat.py
python src/clean_entry_exit.py
python src/build_master.py
```

## SOP: adding a new dataset

Follow these steps in order. Do not skip the record-keeping steps (1, 3, 6): they make the work reproducible and the licence position clear.

### 1. Record the source before or while downloading

Write down:
- the official page URL and the direct file URL;
- the download date;
- the publisher;
- the licence shown on the page;
- whether you filtered, renamed or edited the file in any way.

Prefer official sources (TfL, London Datastore, GLA, council websites). If a file was produced by filtering a larger official file (e.g. one station from a network-wide file), keep the original file too if possible, or record exactly how it was filtered.

### 2. Put the file in `data/raw/`

- Keep the original file name and content.
- **Never open and save raw files in Excel**: saving can silently change dates, number formats and encodings.
- If a team member sends a file, put it in `data/raw/` unchanged and record who provided it.

### 3. Register it in `docs/data_sources.md`

Add a row to the candidate datasets table (section 3) and a short entry under section 3.2 with:
- URL and download date;
- licence and attribution text;
- file name;
- SHA-256 checksum (optional). On Mac: `shasum -a 256 data/raw/<file>`.

Mark the licence as **Verified** only when an official page states it.

### 4. Audit it (look, don't change)

Write or extend an audit script in `src/` (e.g. `inspect_<name>.py`) that reads the raw file and writes `reports/audit_<name>.md`. It should check:
- what one row represents;
- blanks, duplicates, numbers stored as text and impossible values;
- consistency with totals;
- whether IDs (e.g. station NLC) match the existing tables;
- unusual values (closures, strikes, restrictions).

Look up the cause of unusual values where possible and record the source.

### 5. Decide how to handle each issue

Write the findings and decisions in `docs/data_audit.md`:
- a findings section;
- a decisions table with reasons;
- new numbered lines at the end of the Decision log (section 9).

Default rule: **flag, don't delete**.

### 6. Clean it with a script

Write `src/clean_<name>.py`. It reads `data/raw/` and writes `data/processed/<name>.csv`. Include automatic checks, such as row counts or totals before and after.

If the data are station-level, use the master-table columns (`source`, `measurement`, `temporal_resolution`, `year`, `day_type`, `nlc`, `station`, `time_slot`, `measure`, `value`, `in_scope`, `scope_note`, …). Then add the new file to `SOURCES` in `src/build_master.py` and re-run it.

### 7. Commit code and documents, not data

In GitHub Desktop, check the list of changed files before committing:
- ✅ `src/*.py`, `docs/*.md`, `reports/*.md`
- ❌ anything in `data/raw/` or `data/processed/`, `.venv/`, `.DS_Store`

If data files appear in the list, stop and check `.gitignore`. Write a clear commit summary, then **Commit to main** → **Push origin**.

### 8. Share processed data with the team

- Zip only the data files from `data/processed/` and give the archive a version number (e.g. `cleaned_data_v3.zip`).
- Upload it to the team's OneDrive / Teams folder, shared with team members only, together with an updated data note.
- Tell the team what changed since the previous version.

## Attribution for public outputs

- TfL Open Data (NUMBAT, TfL footfall data): "Powered by TfL Open Data".
- London Datastore files (OGL v2.0): "Contains public sector information licensed under the Open Government Licence v2.0".
