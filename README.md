# Europe's Biodiversity in Crisis
### EEA Article 17 - Conservation Status Dashboard (2013-2018)

An interactive Streamlit dashboard exploring the conservation status of species and habitats across 28 EU Member States, built for the University of Westminster 5DATA004C module.

---

## Live App

[View on Streamlit Cloud](#) ← paste your URL here after deployment

---

## Overview

The dashboard tells a data story across eight sections - from a headline summary of how bad things are, down to individual species and country-level detail. Every chart responds to the sidebar filters in real time.

![Dashboard hero and KPI cards](screenshots/01_hero.png)

The four KPI cards at the top give the headline numbers straight away: total assessments, % unfavourable species, % unfavourable habitats, and number of reporting countries.

---

## What the Data Shows

- Over **54%** of species assessments are unfavourable
- Over **72%** of habitat assessments are unfavourable
- Grassland abandonment and natural succession are the most reported pressures
- Habitats are in worse condition than species across all regions

---

## Dataset

**Source:** European Environment Agency (EEA)
**Dataset:** Article 17, Habitats Directive 92/43/EEC - 2013-2018 Reporting Period

| File | Rows | Description |
|---|---|---|
| `data_species_regions.csv` | 8,097 | Species assessments per country and region |
| `data_habitats_regions.csv` | 3,295 | Habitat assessments per country and region |
| `data_pressures_threats.csv` | 114,261 | Reported pressures and threats |

---

## Dashboard Sections

**Act I - Overall Status**

Donut charts showing the split between Favourable, Unfavourable-Inadequate, Unfavourable-Bad and Unknown for both species and habitats.

![Act I status donuts](screenshots/02_act1_donuts.png)

**Act II - Country Ranking**

All 28 countries ranked by % unfavourable, plus an interactive Europe choropleth map showing the geographic spread.

![Act II country bar chart and map](screenshots/03_act2_map.png)

**Act III - Taxonomic Groups**

Which animal and plant groups are suffering most - stacked bar by group with a % unfavourable breakdown alongside.

**Act IV - Trend Over Time**

Side-by-side comparison of the 2007-2012 and 2013-2018 reporting periods with delta annotations showing whether things got better or worse.

![Act IV trend comparison](screenshots/04_act4_trends.png)

**Act V - Biogeographic Regions**

Conservation pressure by region, from the Arctic Boreal north to the Mediterranean south.

**Act VI - Pressures and Threats**

The top reported pressures driving decline, coloured by category (Agriculture, Forestry, Infrastructure, etc.). A slider controls how many to display.

![Act VI pressures chart](screenshots/05_act6_pressures.png)

**Act VII - Population vs Range**

Bubble chart showing species where both population and range are declining simultaneously - the most critical zone.

**Act VIII - Data Explorer**

Full filtered dataset as a scrollable table with a CSV download button.

---

## Sidebar Filters

All filters apply globally across every chart:

- Country (28 EU member states)
- Species group (Mammals, Reptiles, Fish, etc.)
- Biogeographic region (14 regions)
- Assessment status (FV, U1, U2, XX)
- Pressure ranking and type

---

## Project Structure

```
├── app.py              # Streamlit dashboard
├── data_utils.py       # Data loading, filtering, transforms
├── test_app.py         # Pytest test suite - 5 test cases, 31 assertions
├── requirements.txt    # Python dependencies
└── eea_t_art17_p_2013-2018_v01_r00/
    ├── Article17_2020_dataset_csv/
    └── Article17_2020_ref_codelists_csv/
```

---

## Running Locally

```bash
git clone https://github.com/rashiruabey/eea-biodiversity-dashboard.git
cd eea-biodiversity-dashboard
pip install -r requirements.txt
python -m streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Tests

```bash
python -m pytest test_app.py -v
```

Expected: **31 passed**

| Test | What it checks |
|---|---|
| TC1 | All CSVs load with correct row counts and columns |
| TC2 | 100% species group join, zero nulls |
| TC3 | Filters return correct subsets |
| TC4 | Status counts always sum to total rows |
| TC5 | Pressure codes joined to readable labels |

---

## Tech Stack

Streamlit, Pandas, Plotly, Pytest

---

*University of Westminster - 5DATA004C Data Science Project Lifecycle, April 2026*
