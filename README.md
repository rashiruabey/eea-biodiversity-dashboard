# Europe's Biodiversity in Crisis
### EEA Article 17 — Conservation Status Dashboard (2013–2018)

An interactive Streamlit dashboard analysing the conservation status of species and habitats across 28 EU Member States, built for the University of Westminster 5DATA004C Data Science Project Lifecycle module.

---

## Live App

[View on Streamlit Cloud](#) ← link to be added after deployment

---

## Dataset

**Source:** European Environment Agency (EEA)
**Dataset:** Article 17, Habitats Directive 92/43/EEC — 2013–2018 Reporting Period
**URL:** https://www.eea.europa.eu/en/datahub/datahubitem-view/d8b47719-9213-485a-845b-db1bfe93598d

| File | Rows | Description |
|---|---|---|
| `data_species_regions.csv` | 8,097 | Species assessments per country and biogeographic region |
| `data_habitats_regions.csv` | 3,295 | Habitat assessments per country and biogeographic region |
| `data_pressures_threats.csv` | 114,261 | Reported pressures and threats per species/habitat |

---

## Dashboard Features

Eight interactive sections telling a data story from overview to detail:

- **Act I** — Overall status distribution (donut charts, species + habitats)
- **Act II** — Country ranking by % unfavourable (stacked horizontal bar, 28 countries)
- **Act III** — Status breakdown by taxonomic group (stacked bar + % unfavourable)
- **Act IV** — Trend comparison: 2007–2012 vs 2013–2018 (grouped bar with delta annotations)
- **Act V** — Biogeographic region breakdown (stacked bar + % unfavourable)
- **Act VI** — Top pressures and threats driving decline (horizontal bar, slider-controlled)
- **Act VII** — Population vs range trend explorer (bubble chart)
- **Act VIII** — Filterable data table with CSV download

**Sidebar filters:** Country, Species Group, Biogeographic Region, Assessment Status, Pressure ranking and type — all filters apply globally across every chart.

---

## Project Structure

```
├── app.py              # Streamlit dashboard (UI layer)
├── data_utils.py       # Data loading, filtering, transforms (pure Python)
├── test_app.py         # Pytest test suite — 5 test cases, 31 assertions
├── requirements.txt    # Python dependencies
└── eea_t_art17_p_2013-2018_v01_r00/
    ├── Article17_2020_dataset_csv/       # Main CSV data files
    └── Article17_2020_ref_codelists_csv/ # Reference/lookup tables
```

---

## Running Locally

**1. Clone the repository**
```bash
git clone https://github.com/rashiruabey/eea-biodiversity-dashboard.git
cd eea-biodiversity-dashboard
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python -m streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Running Tests

```bash
python -m pytest test_app.py -v
```

Expected output: **31 passed**

| Test Class | Test Case | What It Verifies |
|---|---|---|
| `TestTC1_DataLoading` | TC1 | All CSVs load with correct row counts and schema |
| `TestTC2_SpeciesGroupJoin` | TC2 | 100% species group join — zero null groups |
| `TestTC3_FilterFunctions` | TC3 | Country, group, status, pressure filters return correct subsets |
| `TestTC4_StatusDistribution` | TC4 | Status counts always sum to total rows |
| `TestTC5_PressuresReferenceJoin` | TC5 | Pressure codes correctly joined to human-readable labels |

---

## Tech Stack

| Library | Version | Purpose |
|---|---|---|
| Streamlit | ≥ 1.32 | Web app framework |
| Pandas | ≥ 2.0 | Data loading and transformation |
| Plotly | ≥ 5.18 | Interactive charts |
| Pytest | ≥ 7.4 | Test framework |

---

## Key Findings

- Over **54%** of species assessments and **72%** of habitat assessments are unfavourable
- The number of species in the worst category (U2 — Bad) increased between reporting periods
- **Grassland abandonment** and **natural succession** are the most frequently reported pressures
- Habitats are in significantly worse condition than species across all biogeographic regions

---

*University of Westminster — 5DATA004C Data Science Project Lifecycle, April 2026*
