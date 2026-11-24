# Data folder

Data files are not stored in the repository. Each team member keeps a local copy.

```
data/
├── raw/                 original downloads, never edited (not in the repository)
├── processed/           tables made by the scripts in src/ (not in the repository)
├── events_calendar.csv  events near the Park, compiled by the team (in the repository)
└── station_locations.csv  coordinates of the five study stations (in the repository)
```

## Getting started

1. Download the raw files listed in [`docs/data.md`](../docs/data.md) (section 2) into `data/raw/`. Keep the original file names, and do not open and save them in Excel (this can change dates and number formats).
2. Create a virtual environment **outside any iCloud-synced folder** (first time only), activate it and install the packages:
   ```
   python3 -m venv ~/venvs/urban-mobility
   source ~/venvs/urban-mobility/bin/activate
   python -m pip install -r requirements.txt
   ```
   Next time, only the `source` line is needed.
3. Run the six scripts in order from the repository root:
   ```
   python src/1_clean_numbat.py
   python src/2_clean_entry_exit.py
   python src/3_clean_footfall.py
   python src/4_make_tables.py
   python src/5_make_figures.py
   python src/6_make_map.py
   ```
   Step 6 needs internet the first time, to download the background map.

## Adding a new dataset

1. Download it into `data/raw/` and record the page URL, download date, publisher and licence in `docs/data.md`.
2. Write a script in `src/` that reads it from `data/raw/` and writes a table to `data/processed/`, with a simple check that nothing was lost.
3. Commit the script and the documentation, never the data files.

## Sharing data with the team

Share only the part tables (`part*.csv`), not the large cleaned tables.
