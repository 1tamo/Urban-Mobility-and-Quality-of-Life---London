Data Sources and Feasibility Assessment

Status: In Progress
Last Updated: 17 November 2026

1. Purpose

This document tracks the identification, assessment, and selection of datasets for the project.

The primary objective is to determine which datasets can support empirical investigation of the proposed concentration–pressure–redistribution framework.

2. Data Requirements by Hypothesis
Hypothesis	Required Data	Key Considerations
H1 — Concentration	Station or pedestrian flows, accessibility changes, facility openings	Temporal coverage and location matching
H2 — Pressure Turning Point	Flow counts, delays, crowding or capacity-related indicators	Comparable observations and sufficient variation
H3 — Redistribution	Flow counts across alternative times, routes or locations	Temporal and spatial resolution
H4 — Management Spillovers	Intervention records and flows in affected and surrounding areas	Before-and-after observations and comparison locations
3. Candidate Datasets

The following datasets have been identified for preliminary feasibility assessment. Their inclusion does not imply that they have been approved for the final analysis.

Dataset	Provider	Available Files / Access	Potential Relevance	Licence Status
NUMBAT 2025 Typical Day Outputs	Transport for London (TfL)	Five Excel files covering different typical day types	H1, H2, H3	Verified — TfL Transport Data Service licence (see 3.2)
Multi-year Station Entry and Exit Figures	TfL / London Datastore	Historical station entry and exit data (.xls)	H1, H3	Verified — OGL v2.0 (see 3.2)
London Underground Performance Data	TfL / London Datastore	Historical performance data (.xlsx, two files)	H2	Verified — OGL v2.0 (see 3.2)
NUMBAT 2016–2024 Typical Day Outputs	TfL	Yearly folders on the TfL crowding data portal (not yet downloaded)	H1	Same portal and licence as NUMBAT 2025; not yet assessed
TfL Network Demand data (dashboard and Station footfall files)	TfL	Interactive Power BI report; yearly CSV files 2019–2022 and a weekly-refreshed file from 2023	H1, H3, H4	Not yet verified
3.1 Preliminary Observations

NUMBAT 2025

The available files represent five typical day types: Monday, Tuesday–Thursday, Friday, Saturday, and Sunday.
They contain station-level passenger demand and network-level information, including link loads and service frequencies.
These data may support the exploration of demand concentration and potential pressure-related proxy measures. However, typical day estimates should not be treated as observations of individual calendar dates.
NUMBAT excludes days affected by major disruptions, events and closures, and assumes the full train service operates as scheduled. It therefore describes normal conditions and cannot on its own measure the effect of disruptions or interventions.

Historical Station Entry and Exit Data

Historical station-level counts may help examine longer-term changes in passenger demand.
Temporal resolution and compatibility with other datasets require further assessment.

London Underground Performance Data

Performance indicators may provide measures of service reliability and passenger travel burden.
Their suitability depends on whether they can be meaningfully matched with mobility data.

TfL Network Demand data

The dashboard and the Station footfall files may provide station demand observations for specific calendar dates. NUMBAT provides typical days only.
Temporal granularity, field definitions and licensing conditions remain to be confirmed.
3.2 Data Source Verification (Phase 1.1)

Last checked: 17 November 2026. Data files downloaded: 16 November 2026. NUMBAT documentation downloaded: 17 November 2026. Checked by: 1tamo (with AI-assisted web research). Verified means that an official page states the licence and clearly covers the file.

The project uses two different licences:

the TfL Transport Data Service licence for NUMBAT;
the standard Open Government Licence v2.0 for the London Datastore files.

Attribution is recorded separately for each.

NUMBAT 2025
Folder: https://crowding.data.tfl.gov.uk/#!NUMBAT%2FNUMBAT%202025%2F
Licence statement: the portal (https://crowding.data.tfl.gov.uk/) directs users to the TfL transport data terms and conditions: https://tfl.gov.uk/corporate/terms-and-conditions/transport-data-service.
These terms are based on Open Government Licence v2.0 with TfL-specific amendments.
This is not the standard OGL v3.0.
What the licence permits: copying, publishing, distributing, adapting, and commercial or non-commercial use, including combining with other data.
Conditions relevant to this project:
Attribution: "Powered by TfL Open Data".
Registration with TfL's open data service. The licence applies "from the date of registration". A team member registered on 17 November 2026.
No implication of TfL endorsement. Follow TfL branding guidelines if TfL marks or logos are used.
TfL may revise the licence without notice. Record the date the terms were checked (above).
Personal data is excluded. NUMBAT is aggregated and contains no personal data.
File-level metadata (from the _Cover sheet):
Publisher: TfL – Public Transport Service Planning.
Contact: SMBRailDemandQueries@tfl.gov.uk.
Cover date 2026-07-01; version note "v05 23-04-26".
The file itself contains no licence statement.

Data files. Downloaded 16 Nov 2026. The portal timestamp for every file is 10 Aug 2026, and the local file sizes match the portal listing.

File	Download URL	SHA-256
NBT25MON_Outputs.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202025/NBT25MON_Outputs.xlsx	89ebca13a5f611e255c3cc31eb34917a7262c642135e943ee6714df17a108b05
NBT25TWT_Outputs.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202025/NBT25TWT_Outputs.xlsx	a10e5f767750538ecac99cf0d2131243672574df88b9c933f03b9357c5f67db2
NBT25FRI_Outputs.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202025/NBT25FRI_Outputs.xlsx	22eeb8fe2fd5ee2c974aaff81c7f3e114c53e39f46cd03c273c072974f5d9b5c
NBT25SAT_Outputs.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202025/NBT25SAT_Outputs.xlsx	64cdfa78f312332740f9a562f81f5dac12114bb439d4a219bcf095ee28ad3821
NBT25SUN_Outputs.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202025/NBT25SUN_Outputs.xlsx	c064331e50cf92edd022ef9f1f7efb9c21ca38edabb963a7bf5758682d60bc8c

Supporting documentation. Downloaded 17 Nov 2026; same portal and licence.

File	Download URL	SHA-256
Intro_to_NUMBAT.pdf	https://crowding.data.tfl.gov.uk/NUMBAT/Intro_to_NUMBAT.pdf	b62b95112b545723da59c64118a7ba182d8230cfbc688b50b5e485fa7e025458
PTSP Oasis for NUMBAT definitions.xlsx	https://crowding.data.tfl.gov.uk/NUMBAT/NUMBAT%202024/PTSP%20Oasis%20for%20NUMBAT%20definitions.xlsx	4b2bf85aa082a7452d8e6d1ea63d5b48498771c267a71c258a445c6c1a23940c
Intro_to_NUMBAT.pdf (2020) defines each output:
Link Load: the number of passengers travelling along a link between two stations per 15 minutes.
Service Frequency: the number of trains passing through a line section per 15 minutes.
NUMBAT assumes a perfect train schedule is operated.
Definitions workbook. This is the "Definitions file" referenced on the _Cover sheet. It sits in the 2024 folder; no 2025 version was found.
Contents: reference tables for stations (NLC/ASC, NaPTAN and National Rail CRS codes, alternative names), lines, directions, nodes (with x/y coordinates), rail links (including DistanceM) and within-station links.
Coverage caveat: the station-scope table only has flags up to NBT2023. The 2025 _Cover sheet also records link changes made in April 2026 (Elizabeth line branch codes; Metropolitan line fast/semi-fast links). The data audit must check that every 2025 station and link ID matches this workbook.
Also available, not downloaded: NUMBAT/NBT16-25_AnnualisedBoarders_Outputs.xlsx (annualised boarders, 2016–2025).
London Datastore files
Record: "London Underground Performance Reports", https://data.london.gov.uk/dataset/london-underground-performance-reports-em8qy.
Author: Transport for London.
Maintainer: Opinion Research and General Statistics (GLA).
Last updated: 28 April 2020.
Licence shown on the record: Open Government Licence v2.0, https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/.
Attribution: "Contains public sector information licensed under the Open Government Licence v2.0."
Downloaded: 16 November 2026.
File	Coverage label on record	SHA-256
tfl-tube-performance.xlsx	May 2011 – Mar 2020	a54f561ea2cbfaf3a70c55716bcf69f570274080c58f14e8cb5c26e49888daaf
multi-year-station-entry-and-exit-figures.xls ("Entry and exit figures by station")	May 2011 – Mar 2017	3b8cf828567f22a3d46b199cf79a0aa1175d976d4fc709261960d484b288bb6d
lu-performance-data.xlsx ("LU-Performance data almanac")	May 2011 – Apr 2019	6a38aed882639a74b9b0836b2b0d3f8360a78923f57a46b25bf49cbecf65141d
Copyright notice: the station entry/exit file carries "(C) Copyright, London Underground Limited, 2018". This does not conflict with the OGL: the copyright holder keeps copyright and licenses use under the OGL.
Coverage labels: the labels on the record do not match the file contents. For example, the entry/exit file contains sheets for 2007–2017. The data audit uses the actual file contents.
Repository policy for raw data

Raw data files are kept out of the public repository (data/raw/ is git-ignored), even though both licences permit redistribution with attribution:

Reproducibility: the official download URL, download date and SHA-256 checksum of each file are recorded above, so others can obtain identical copies from the publisher.
Size: the five NUMBAT 2025 files are about 60 MB in total.

Derived outputs (for example aggregated tables or figures) may be published with the attribution required by the relevant licence.

4. Dataset Assessment Criteria

Each dataset will be evaluated according to:

Data availability and licensing
Temporal coverage and resolution
Geographic coverage and resolution
Available variables and identifiers
Missing data and measurement limitations
Compatibility with other datasets
Relevance to the research hypotheses
5. Dataset Selection Decisions

The rationale for accepting or rejecting candidate datasets will be documented here.

6. Outstanding Questions
Which datasets provide sufficiently detailed mobility observations?
Can flow counts be linked to pressure-related indicators?
Are intervention dates and surrounding-area observations available?
Which hypotheses remain feasible after data assessment?
Are NUMBAT outputs comparable across years (2016–2025), given changes in day-type definitions (e.g. MTT in 2016 versus MON/TWT/FRI in 2025) and network changes?
What is the temporal granularity and licence of the TfL Network Demand Station footfall files?
