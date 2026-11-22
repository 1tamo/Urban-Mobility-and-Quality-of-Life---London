# Research Design

**Project:** When Does Concentration Become Pressure? Urban Mobility and Quality of Life in London

**Status:** Main case selected (Stratford); analysis in progress
**Version:** 0.3
**Draft Date:** 22 November 2026
**Initial Document Author:** 1tamo

---

## 1. Main Research Question

Transport accessibility and urban development attract people, but are the benefits of growing activity limited by infrastructure capacity?

When local pressures rise, how do flows redistribute, and do urban management measures alleviate pressure or transfer it to surrounding areas?

## 2. Background and Proposed Conceptual Model

New facilities, transport connections, and employment or commercial opportunities may attract people to an area.

Increased activity may then support further business and service development, reinforcing its attractiveness. However, when demand outgrows the capacity of infrastructure and public space, crowding, delays and travel difficulties may reduce these benefits and encourage some people to adjust their journeys.

### Proposed Conceptual Framework

**Improved access and opportunities → Concentration of people → Rising capacity pressure → Worsening travel experience → Redistribution across times, routes or destinations**

This framework is a hypothesis to be tested, not an assumed explanation.

## 3. Research Hypotheses

### H1 — Concentration

Improved transport accessibility or new facilities are associated with increased local flows.

### H2 — A Pressure Turning Point

The relationship between flows and travel experience may be nonlinear. Once seats are full, each additional passenger adds standing density, and the perceived cost of travel rises more sharply.

How we treat H2: we do not test the turning point ourselves. Yap, Wong & Cats (2023) found, using observed route choices on the London Underground, that crowding costs start once seats are full and then rise roughly linearly with standing density. Our contribution is to show where Stratford stands relative to that point: in the morning peak, Central line and Elizabeth line trains leaving Stratford are past it; off-peak trains and the Jubilee line are not. Part 3's figure applies the published formula, so it illustrates the turning point rather than proving it.

### H3 — Redistribution

When a hub is under pressure (for example on event days), some demand may shift to nearby alternative stations.

### H4 — Management Spillovers

Crowd-management measures at a hub (for example queuing, holding passengers or closing an entrance) may relieve that hub while increasing pressure at surrounding stations.

## 4. Research Scope

### 4.1 Main Case: Stratford and the Queen Elizabeth Olympic Park area

Selected on 22 November 2026 after team discussion. Stratford allows all four hypotheses to be examined in one place:

| Hypothesis | How it appears at Stratford |
|---|---|
| H1 | Long-term growth in station use alongside new transport links and facilities (2009–2016) |
| H2 | Peak-hour trains leaving Stratford run with all seats taken and many passengers standing |
| H3 | On event days at London Stadium, demand rises at smaller stations around the Park |
| H4 | Event-day crowd management at Stratford station may push passengers towards those smaller stations |

**Study stations**

| Station | Main mode(s) | Notes |
|---|---|---|
| Stratford | LU (Central, Jubilee), Elizabeth line, LO, DLR, National Rail | Hub |
| Stratford International | DLR, HS1 (Southeastern) | |
| Stratford High Street | DLR | |
| Pudding Mill Lane | DLR | Closest DLR station to London Stadium |
| Hackney Wick | LO | |

Coverage of each station in each dataset must be confirmed before analysis (see section 8).

**Timeline of access and opportunity changes** (to be verified against primary sources before use in figures)

| Year | Change | Type |
|---|---|---|
| 2009 | Domestic high-speed (HS1) services start calling at Stratford International | Access |
| 2011 | Westfield Stratford City opens; Stratford City bus station opens | Opportunity / Access |
| 2012 | London Olympic and Paralympic Games | Opportunity |
| 2016 | London Stadium becomes West Ham United's home ground | Opportunity |

### 4.2 Case considered and set aside: Camden High Street pedestrianisation

Camden High Street was proposed on 17 November 2026 as a case for H4. The trial began on 3 May 2025 and the scheme was made permanent on 27 October 2026 (Camden Council).

It is no longer the main case, for these reasons:

- The intervention affects street footfall, but our data measure station demand. Station demand is not street footfall.
- Only one before (NUMBAT 2024) and one after (NUMBAT 2025) typical-day observation are available.
- It does not connect to the Stratford story.

If time allows, a short before-and-after comparison of Camden Town against nearby stations may be reported in an appendix. A result that does not support H4 would still be reported.

## 5. Data and Methods

The analysis is organised as a four-part story. Each part answers one question with one main figure.

| Part | Question | Data | Main figure | Hypothesis |
|---|---|---|---|---|
| 0. London overview | Where in London has demand grown, and how has it changed? Why Stratford? | Entry/exit counts 2007–2017 (all Underground stations); NUMBAT 2018–2025 (all stations) | Top 10 growth stations; demand by fare zone vs 2019 | Context |
| 1. Concentration | Why Stratford? How did use grow? | LU station entry/exit counts 2007–2017 (Stratford only) | Line chart by day type, annotated with the timeline in 4.1 | H1 |
| 2. Everyday pressure | Is pressure rising across the five stations? | NUMBAT typical-day outputs 2018–2025 | Heatmap: station × year, one panel each for weekday, Saturday and Sunday | H1, H2 |
| 3. Travel experience | What does that pressure feel like on board? | NUMBAT 2025 link loads and frequencies; TfL rolling stock data; crowding valuation (Yap, Wong & Cats, 2023) | Peak vs off-peak perceived journey time by line | H2 |
| 4. Redistribution | On event days, where does the pressure go? | TfL Network Demand station footfall (daily); event calendar | Daily demand relative to each station's median, event days marked | H3, H4 |

### 5.1 Pressure index (Part 4)

Physical station capacity is not published in a usable form, so pressure is measured relative to each station's own normal level:

> pressure index = daily entries and exits ÷ median daily entries and exits for the same station and the same day of the week, over the same year

Working thresholds: an index of 1.5 or more is **elevated**, and 2.0 or more is **extreme**. These are analytical choices, not safety limits. Results will be checked with other thresholds.

Both the relative increase (index) and the absolute increase (extra passengers) are reported. A hub can show a small relative increase while still handling the largest number of extra people.

### 5.2 Perceived journey time (Part 3)

> perceived time = in-vehicle time × (1 + 0.42 × standing passengers per m²)

Standing density = (average passengers per train − seats) ÷ standing area, set to zero when seats are not full. Passengers per train are calculated per hour, because 15-minute values jump with the timing of trains (see `docs/data.md`, section 3). The 0.42 coefficient comes from Yap, Wong & Cats (2023), estimated from 20,970 observed route choices on the Central and Victoria lines in June 2022 (t = 2.21). Observed standing densities in that study did not exceed 3 per m², so the Elizabeth line value (3.24) is a slight extrapolation. As a sensitivity check, Part 3 also reports results with 0.22 (the average of pre-2020 studies quoted in the same paper) and with the approximate 95% interval of 0.42 (0.05–0.79).

### 5.3 Optional scenario

If time allows, a simple, clearly labelled scenario: if one station's event-day excess demand were redistributed to the others in proportion to their normal share, which stations would pass the thresholds in 5.1? This is a what-if calculation, not a forecast.

## 6. Quality of Life and Responsible Data Analysis

- **Observed flows are not direct measures of well-being.** Passenger counts cannot establish subjective experience, crowd density at a given moment, or safety risk.
- **NUMBAT is modelled, not observed.** It describes a typical day and averages across all trains in each period. Individual trains and areas near doors are more crowded.
- **Statistical thresholds are not physical capacity limits.**
- **Association does not establish causation.** The timeline in 4.1 shows coincidence in time, not cause.
- **2020 and 2021 show much lower demand than other years**; trends are compared with 2019.
- Evidence on residents' wider quality of life is mostly qualitative or not specific to Stratford, and is used as supporting context only.

## 7. Expected Outcomes

The project aims to evaluate how far the evidence at Stratford supports the concentration–pressure–redistribution framework. An absence of clear patterns, or evidence against a hypothesis, will also be reported as a finding.

## 8. Open Decisions

Done (22 November 2026):
- All five study stations appear in NUMBAT 2018–2025 and in the station footfall files.
- The Part 2 heatmap uses whole-day totals, compared with 2019. Tables by time band are also available.
- NUMBAT 2016–2017 are not used: 2018–2025 already cover the years before and after 2020–2021.

Still open:
- Build and verify the event calendar (date, venue, event type, attendance), so the busiest days in Part 4 can be matched to events.
- Find out why Pudding Mill Lane demand jumps from 2022 in NUMBAT (real change, or a change in how TfL models the station?).
- Verify the Elizabeth line standing area, currently estimated from published standing capacity.

## 9. Revision History

Substantive changes are also recorded in the Git history.

| Version | Date | Description |
|---|---|---|
| 0.1 | 2026-11-02 | Initial draft |
| 0.1 (GitHub) | 2026-11-16 | Added to the repository |
| 0.2 | 2026-11-17 | Added candidate case: Camden High Street pedestrianisation |
| 0.3 | 2026-11-22 | Stratford selected as main case; Camden set aside; analysis organised as a four-part story; pressure index and perceived time defined; first results for all four parts |

---

**Keywords:** Urban mobility; Transport accessibility; Capacity pressure; Quality of life; Flow redistribution; Spatial spillover effects.
