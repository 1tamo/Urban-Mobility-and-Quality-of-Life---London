# Data folder

Data files are not stored in the repository. Each team member keeps a local copy.

```
data/
├── raw/         original downloads, never edited
└── processed/   tables made by the scripts in src/
```

## Getting started

1. Download the raw files listed in [`docs/data.md`](../docs/data.md) (section 2) into `data/raw/`. Keep the original file names, and do not open and save them in Excel (this can change dates and number formats).
2. Activate the virtual environment and install the packages:
   ```
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```
3. Run the four scripts in order from the repository root:
   ```
   python src/1_clean_numbat.py
   python src/2_clean_entry_exit.py
   python src/3_make_tables.py
   python src/4_make_figures.py
   ```

## Adding a new dataset

1. Download it into `data/raw/` and record the page URL, download date, publisher and licence in `docs/data.md`.
2. Write a script in `src/` that reads it from `data/raw/` and writes a table to `data/processed/`, with a simple check that nothing was lost.
3. Commit the script and the documentation, never the data files.

## Sharing data with the team

Share only the part tables (`part*.csv`), not the large cleaned tables.
