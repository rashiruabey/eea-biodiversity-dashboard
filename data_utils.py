"""
data_utils.py
Pure data-loading and transformation functions - no Streamlit dependency.
Imported by app.py (which wraps loaders with @st.cache_data) and by test_app.py.
"""
import os
import pandas as pd

# ── PATHS ─────────────────────────────────────────────────────────────────────
_BASE    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(_BASE, "eea_t_art17_p_2013-2018_v01_r00",
                         "Article17_2020_dataset_csv")
REF_DIR  = os.path.join(_BASE, "eea_t_art17_p_2013-2018_v01_r00",
                         "Article17_2020_ref_codelists_csv")

# ── CONSTANTS ──────────────────────────────────────
# ───────────────────────────
STATUS_ORDER  = ["FV", "U1", "U2", "XX"]
STATUS_COLORS = {
    "FV": "#27ae60",
    "U1": "#f39c12",
    "U2": "#e74c3c",
    "XX": "#7f8c8d",
}
STATUS_LABELS = {
    "FV": "Favourable",
    "U1": "Unfavourable - Inadequate",
    "U2": "Unfavourable - Bad",
    "XX": "Unknown",
}
TREND_LABELS = {
    "I":   "Improving",
    "S":   "Stable",
    "D":   "Declining",
    "Unk": "Unknown",
    "U":   "Uncertain",
}
COUNTRY_NAMES = {
    "AT": "Austria",        "BE": "Belgium",        "BG": "Bulgaria",
    "CY": "Cyprus",         "CZ": "Czech Republic", "DE": "Germany",
    "DK": "Denmark",        "EE": "Estonia",         "ES": "Spain",
    "FI": "Finland",        "FR": "France",          "GR": "Greece",
    "HR": "Croatia",        "HU": "Hungary",         "IE": "Ireland",
    "IT": "Italy",          "LT": "Lithuania",       "LU": "Luxembourg",
    "LV": "Latvia",         "MT": "Malta",           "NL": "Netherlands",
    "PL": "Poland",         "PT": "Portugal",        "RO": "Romania",
    "SE": "Sweden",         "SI": "Slovenia",        "SK": "Slovakia",
    "UK": "United Kingdom",
}
PRESSURE_CAT_COLORS = {
    "A": "#e67e22",  # Agriculture
    "B": "#27ae60",  # Forestry
    "C": "#8e44ad",  # Mining / quarrying
    "D": "#2980b9",  # Infrastructure / transport
    "E": "#c0392b",  # Urbanisation
    "F": "#16a085",  # Human intrusion / disturbance
    "G": "#d35400",  # Pollution
    "H": "#7f8c8d",  # Natural abiotic processes
    "I": "#e74c3c",  # Invasive / problematic species
    "J": "#2c3e50",  # Modified ecosystem functioning
    "K": "#3498db",  # Climate change / hydrological change
    "L": "#1abc9c",  # Geological events
    "M": "#9b59b6",  # Other
    "N": "#e74c3c",  # Climate-related
    "X": "#95a5a6",  # Unknown
}


# ── LOADERS ───────────────────────────────────────────────────────────────────

def load_species_raw() -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(DATA_DIR, "Article17_2020_data_species_regions.csv"),
        encoding="utf-8-sig", low_memory=False,
    )
    checklist = pd.read_csv(
        os.path.join(DATA_DIR, "Article17_2020_species_check_list.csv"),
        encoding="utf-8-sig",
    )
    group_map = checklist.drop_duplicates("speciescode")[["speciescode", "group"]]
    df = df.merge(group_map, on="speciescode", how="left")
    df = df[df["use_for_statistics"] == "Yes"].copy()
    for col in ["conclusion_assessment", "conclusion_assessment_prev"]:
        df[col] = df[col].fillna("XX").replace("", "XX")
    df["conclusion_assessment_trend"] = (
        df["conclusion_assessment_trend"].fillna("Unk").replace("", "Unk")
    )
    df["population_trend"] = df["population_trend"].fillna("Unk").replace("", "Unk")
    df["range_trend"]      = df["range_trend"].fillna("Unk").replace("", "Unk")
    df["country_name"]     = df["country"].map(COUNTRY_NAMES)
    return df


def load_habitats_raw() -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(DATA_DIR, "Article17_2020_data_habitats_regions.csv"),
        encoding="utf-8-sig", low_memory=False,
    )
    df = df[df["use_for_statistics"] == "Yes"].copy()
    for col in ["conclusion_assessment", "conclusion_assessment_prev"]:
        df[col] = df[col].fillna("XX").replace("", "XX")
    df["conclusion_assessment_trend"] = (
        df["conclusion_assessment_trend"].fillna("Unk").replace("", "Unk")
    )
    df["coverage_trend"] = df["coverage_trend"].fillna("Unk").replace("", "Unk")
    df["country_name"]   = df["country"].map(COUNTRY_NAMES)
    return df


def load_pressures_raw() -> pd.DataFrame:
    df = pd.read_csv(
        os.path.join(DATA_DIR, "Article17_2020_data_pressures_threats.csv"),
        encoding="utf-8-sig", low_memory=False,
    )
    ref = pd.read_csv(
        os.path.join(REF_DIR, "Article17_2020_ref_threatsPressures.csv"),
        encoding="utf-8-sig",
    )
    df = df.merge(ref, left_on="pressurecode", right_on="code", how="left")
    df = df[df["use_for_statistics"] == "Yes"].copy()
    df["country_name"] = df["country"].map(COUNTRY_NAMES)
    return df


def load_bio_regions() -> dict:
    ref = pd.read_csv(
        os.path.join(REF_DIR, "Article17_2020_ref_bioGeoReg.csv"),
        encoding="utf-8-sig",
    )
    return dict(zip(ref["code"], ref["label"]))


# ── FILTER HELPERS ────────────────────────────────────────────────────────────

def filter_species(
    df: pd.DataFrame,
    countries=None,
    groups=None,
    regions=None,
    statuses=None,
) -> pd.DataFrame:
    if countries: df = df[df["country"].isin(countries)]
    if groups:    df = df[df["group"].isin(groups)]
    if regions:   df = df[df["region"].isin(regions)]
    if statuses:  df = df[df["conclusion_assessment"].isin(statuses)]
    return df


def filter_habitats(
    df: pd.DataFrame,
    countries=None,
    regions=None,
    statuses=None,
) -> pd.DataFrame:
    if countries: df = df[df["country"].isin(countries)]
    if regions:   df = df[df["region"].isin(regions)]
    if statuses:  df = df[df["conclusion_assessment"].isin(statuses)]
    return df


def filter_pressures(
    df: pd.DataFrame,
    countries=None,
    regions=None,
    feat_type: str = "Both",
    ranking_sel=None,
    ptype: str = "Both",
) -> pd.DataFrame:
    if countries:  df = df[df["country"].isin(countries)]
    if regions:    df = df[df["region"].isin(regions)]
    if feat_type != "Both":
        df = df[df["featuretype"] == feat_type.lower()]
    if ranking_sel:
        df = df[df["ranking"].isin(ranking_sel)]
    if ptype != "Both":
        df = df[df["type"] == ("p" if ptype == "Pressures" else "t")]
    return df


# ── TRANSFORM HELPERS ─────────────────────────────────────────────────────────

def status_dist(df: pd.DataFrame, col: str = "conclusion_assessment") -> pd.DataFrame:
    counts = df[col].value_counts().reindex(STATUS_ORDER, fill_value=0)
    out = pd.DataFrame({"status": counts.index, "count": counts.values})
    out["label"] = out["status"].map(STATUS_LABELS)
    out["color"] = out["status"].map(STATUS_COLORS)
    return out


def pressure_bar_color(code: str) -> str:
    return PRESSURE_CAT_COLORS.get(code[0].upper() if code else "X", "#95a5a6")
