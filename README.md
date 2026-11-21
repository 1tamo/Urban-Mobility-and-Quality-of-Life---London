# When Does Concentration Become Pressure?
### Urban Mobility and Quality of Life in London: the case of Stratford

## The question

New transport links and new destinations attract people. But when demand grows faster than stations and trains can handle, travel gets worse, and the pressure may move to nearby places.

We test this idea at **Stratford** in east London, where new rail links, Westfield, the 2012 Olympics and London Stadium have brought large numbers of people to one area.

## The story in four parts

| Part | Question | Hypothesis | Status |
|---|---|---|---|
| 1. Concentration | How did use of Stratford grow, and when? | H1 | In progress |
| 2. Everyday pressure | Is demand rising across Stratford and four nearby stations? | H1, H2 | In progress |
| 3. Travel experience | What does peak-hour crowding feel like on board? | H2 | Preliminary result |
| 4. Redistribution | On event days, does pressure move to smaller stations? | H3, H4 | Data being collected |

**Preliminary result (Part 3):** On a typical 2025 weekday between 08:00 and 09:00, trains leaving Stratford for central London ran with all seats taken. Using a published London crowding valuation, a 10-minute ride felt like about 16 minutes on the Central line and about 24 minutes on the Elizabeth line, compared with about 10–11.5 minutes off-peak. These figures are being re-checked.

_Figures will be added here as each part is completed._

## Hypotheses

- **H1 — Concentration:** Improved access or new facilities are associated with increased local flows.
- **H2 — Pressure turning point:** Once seats are full, crowding makes travel feel sharply worse.
- **H3 — Redistribution:** When the hub is under pressure, demand shifts to nearby stations.
- **H4 — Management spillovers:** Crowd management at the hub may relieve it while increasing pressure elsewhere.

## Repository guide

| Folder / file | What it contains |
|---|---|
| [`docs/research_design.md`](docs/research_design.md) | Research question, case selection, methods and limitations |
| [`docs/analysis_tables.md`](docs/analysis_tables.md) | The small tables behind each figure, column by column |
| [`docs/data_sources.md`](docs/data_sources.md) | Where each dataset comes from, and its licence |
| [`docs/data_audit.md`](docs/data_audit.md) | Data quality checks and cleaning decisions |
| [`data/README.md`](data/README.md) | How to download the data and run the scripts |
| `src/` | Data audit and cleaning scripts |
| `reports/` | Audit reports and cleaning logs produced by the scripts |

## Responsible data analysis

- Passenger counts are not direct measures of well-being, crowd density or safety.
- NUMBAT data are modelled typical days, averaged across all trains in each period.
- Thresholds used in the analysis are analytical choices, not safety limits.
- Patterns in time are associations, not proof of cause.

## Data attribution

Powered by TfL Open Data. Contains public sector information licensed under the Open Government Licence v2.0.
