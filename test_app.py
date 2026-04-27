"""
test_app.py - Test suite for EEA Article 17 Biodiversity Dashboard
University of Westminster 5DATA004C

Run with:  pytest test_app.py -v

Five test classes map 1-to-1 to the five documented test cases (TC1–TC5).
All tests use the real CSV data (integration tests) - no mocks.
Fixtures are module-scoped so data loads once per session.
"""
import pytest
import pandas as pd

from data_utils import (
    load_species_raw,
    load_habitats_raw,
    load_pressures_raw,
    filter_species,
    filter_habitats,
    filter_pressures,
    status_dist,
    STATUS_ORDER,
    STATUS_LABELS,
)


# ── SHARED FIXTURES ───────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def species_df():
    """Load and return the processed species dataset once per test session."""
    return load_species_raw()


@pytest.fixture(scope="module")
def habitats_df():
    """Load and return the processed habitats dataset once per test session."""
    return load_habitats_raw()


@pytest.fixture(scope="module")
def pressures_df():
    """Load and return the processed pressures/threats dataset once per test session."""
    return load_pressures_raw()


# ── TC1: DATA LOADING & STRUCTURE ─────────────────────────────────────────────

class TestTC1_DataLoading:
    """
    TC1 - Data Loading and Structure Validation

    Description:
        Verify that all three primary CSV files load correctly, contain more
        than 100 usable rows (satisfying the coursework minimum), and expose
        the expected column schema required by the dashboard.

    Dependencies:
        CSV files present in eea_t_art17_p_2013-2018_v01_r00/Article17_2020_dataset_csv/

    Expected result:
        - species_df: >= 7,000 rows, required columns present, no raw un-filtered rows
        - habitats_df: >= 3,000 rows, required columns present
        - pressures_df: >= 100,000 rows, required columns present
    """

    def test_species_row_count(self, species_df):
        assert len(species_df) >= 7000, (
            f"Expected >= 7,000 species rows after filtering, got {len(species_df)}"
        )

    def test_species_required_columns(self, species_df):
        required = {
            "country", "region", "speciescode", "speciesname",
            "conclusion_assessment", "conclusion_assessment_prev",
            "conclusion_assessment_trend", "population_trend", "range_trend",
            "group", "country_name", "use_for_statistics",
        }
        missing = required - set(species_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_habitats_row_count(self, habitats_df):
        assert len(habitats_df) >= 3000, (
            f"Expected >= 3,000 habitat rows, got {len(habitats_df)}"
        )

    def test_habitats_required_columns(self, habitats_df):
        required = {
            "country", "region", "habitatcode",
            "conclusion_assessment", "conclusion_assessment_prev",
            "coverage_trend",
        }
        missing = required - set(habitats_df.columns)
        assert not missing, f"Missing columns: {missing}"

    def test_pressures_row_count(self, pressures_df):
        assert len(pressures_df) >= 100_000, (
            f"Expected >= 100,000 pressure rows, got {len(pressures_df)}"
        )

    def test_only_usable_rows_loaded(self, species_df):
        assert (species_df["use_for_statistics"] == "Yes").all(), (
            "Loader should only return use_for_statistics == 'Yes' rows"
        )


# ── TC2: SPECIES GROUP JOIN COMPLETENESS ──────────────────────────────────────

class TestTC2_SpeciesGroupJoin:
    """
    TC2 - Species Group Join Completeness

    Description:
        Verify that every species assessment row is enriched with a taxonomic
        group label via the join with Article17_2020_species_check_list.csv.
        A 100% join rate is expected because the checklist covers all species
        codes that appear in the main assessment table.

    Steps and input data:
        1. Load species dataset (load_species_raw())
        2. Inspect the 'group' column for null values
        3. Assert null count == 0
        4. Assert all expected taxonomic group names are present

    Dependencies:
        Article17_2020_species_check_list.csv must be present alongside main data.

    Expected result:
        - Zero null values in the 'group' column
        - All nine Habitats Directive taxonomic groups are represented
    """

    def test_no_null_groups(self, species_df):
        null_count = species_df["group"].isna().sum()
        assert null_count == 0, (
            f"Found {null_count} rows with missing 'group' - join failed for some species codes"
        )

    def test_expected_taxonomic_groups_present(self, species_df):
        expected = {
            "Mammals", "Reptiles", "Amphibians", "Fish",
            "Vascular plants", "Arthropods", "Molluscs",
            "Non-vascular plants", "Other invertebrates",
        }
        actual = set(species_df["group"].unique())
        missing = expected - actual
        assert not missing, f"These expected groups are absent: {missing}"

    def test_group_column_is_string(self, species_df):
        dtype_name = str(species_df["group"].dtype).lower()
        assert "str" in dtype_name or "object" in dtype_name, (
            f"'group' column should be a string dtype, got: {species_df['group'].dtype}"
        )

    def test_join_coverage_is_100_percent(self, species_df):
        pct = 100 * species_df["group"].notna().mean()
        assert pct == 100.0, f"Join coverage: {pct:.2f}% - expected 100%"


# ── TC3: FILTER FUNCTIONS ────────────────────────────────────────────────────

class TestTC3_FilterFunctions:
    """
    TC3 - Interactive Filter Accuracy

    Description:
        Verify that the filter_species(), filter_habitats(), and filter_pressures()
        functions return exactly the correct subset of rows when a filter is applied,
        and return the full dataset when no filter is applied.
        This tests the core interactivity logic of the dashboard sidebar.

    Steps and input data:
        1. Apply single-country filter (country=['DE']) to species data
        2. Assert all returned rows have country == 'DE'
        3. Apply no filters - assert row count unchanged
        4. Apply multi-country filter and assert result set
        5. Apply species group filter and assert result set
        6. Apply status filter to habitats

    Dependencies:
        species_df and habitats_df fixtures.

    Expected result:
        - Single-country filter: all rows country == 'DE'
        - No filter: row count unchanged
        - Multi-country: only selected countries present
        - Group filter: only selected group present
        - Status filter: only selected status codes present
    """

    def test_single_country_filter(self, species_df):
        filtered = filter_species(species_df, countries=["DE"])
        assert (filtered["country"] == "DE").all(), "Expected only DE rows"

    def test_country_filter_reduces_rows(self, species_df):
        filtered = filter_species(species_df, countries=["DE"])
        assert len(filtered) < len(species_df)

    def test_no_filter_returns_all_rows(self, species_df):
        filtered = filter_species(species_df)
        assert len(filtered) == len(species_df)

    def test_multi_country_filter(self, species_df):
        filtered = filter_species(species_df, countries=["DE", "FR", "IT"])
        result_countries = set(filtered["country"].unique())
        assert result_countries.issubset({"DE", "FR", "IT"}), (
            f"Unexpected countries in result: {result_countries - {'DE','FR','IT'}}"
        )

    def test_species_group_filter(self, species_df):
        filtered = filter_species(species_df, groups=["Mammals"])
        assert (filtered["group"] == "Mammals").all()

    def test_status_filter_habitats(self, habitats_df):
        filtered = filter_habitats(habitats_df, statuses=["U2"])
        assert (filtered["conclusion_assessment"] == "U2").all()

    def test_pressure_feature_type_filter(self, pressures_df):
        sp_only = filter_pressures(pressures_df, feat_type="Species")
        assert (sp_only["featuretype"] == "species").all()

    def test_pressure_type_filter_threats_only(self, pressures_df):
        threats = filter_pressures(pressures_df, ptype="Threats")
        assert (threats["type"] == "t").all()


# ── TC4: STATUS DISTRIBUTION ──────────────────────────────────────────────────

class TestTC4_StatusDistribution:
    """
    TC4 - Status Distribution Calculation

    Description:
        Verify that the status_dist() function correctly computes the count of
        each assessment status (FV, U1, U2, XX), that counts sum to the total
        number of rows in the input DataFrame, and that the ecological finding
        (majority unfavourable) is confirmed by the data.

    Steps and input data:
        1. Call status_dist(species_df)
        2. Assert sum of counts == len(species_df)
        3. Assert all four STATUS_ORDER codes are present in output
        4. Assert FV + U1 + U2 + XX == total
        5. Assert U1 + U2 > 40% of total (expected ecological finding)

    Dependencies:
        species_df and habitats_df fixtures.

    Expected result:
        - Counts sum to total rows
        - All four status codes represented
        - More than 40% of species assessments are unfavourable
        - Habitats distribution also sums correctly
    """

    def test_species_counts_sum_to_total(self, species_df):
        dist = status_dist(species_df)
        assert dist["count"].sum() == len(species_df), (
            f"Status counts sum to {dist['count'].sum()}, expected {len(species_df)}"
        )

    def test_all_status_codes_in_output(self, species_df):
        dist = status_dist(species_df)
        assert list(dist["status"]) == STATUS_ORDER, (
            f"Expected {STATUS_ORDER}, got {list(dist['status'])}"
        )

    def test_status_labels_mapped_correctly(self, species_df):
        dist = status_dist(species_df)
        for _, row in dist.iterrows():
            assert row["label"] == STATUS_LABELS[row["status"]]

    def test_majority_unfavourable_species(self, species_df):
        dist = status_dist(species_df).set_index("status")
        unfav_total = dist.loc[["U1", "U2"], "count"].sum()
        total = dist["count"].sum()
        pct = unfav_total / total
        assert pct > 0.40, (
            f"Expected > 40% unfavourable, got {pct:.1%}. "
            "This may indicate a data filtering error."
        )

    def test_habitats_counts_sum_to_total(self, habitats_df):
        dist = status_dist(habitats_df)
        assert dist["count"].sum() == len(habitats_df)

    def test_habitats_majority_unfavourable(self, habitats_df):
        dist = status_dist(habitats_df).set_index("status")
        unfav = dist.loc[["U1", "U2"], "count"].sum()
        total = dist["count"].sum()
        assert unfav / total > 0.55, (
            "Habitats expected to be >55% unfavourable based on known dataset content"
        )

    def test_prev_period_dist_also_sums(self, species_df):
        dist = status_dist(species_df, col="conclusion_assessment_prev")
        assert dist["count"].sum() == len(species_df)


# ── TC5: PRESSURES REFERENCE JOIN ─────────────────────────────────────────────

class TestTC5_PressuresReferenceJoin:
    """
    TC5 - Pressures / Threats Reference Code Join

    Description:
        Verify that the join between data_pressures_threats.csv and
        ref_threatsPressures.csv correctly adds human-readable labels to at
        least 95% of pressure/threat records, and that specific known pressure
        codes resolve to their expected label text.

    Steps and input data:
        1. Load pressures dataset (load_pressures_raw())
        2. Inspect 'label' column for non-null values
        3. Assert >= 95% label coverage
        4. Assert pressure code 'A06' maps to a label containing 'grassland'
        5. Assert pressure code 'L02' maps to a label containing 'succession'
        6. Assert featuretype column contains both 'species' and 'habitats'

    Dependencies:
        Article17_2020_ref_threatsPressures.csv must be present in ref_codelists_csv/

    Expected result:
        - >= 95% of rows have a non-null label
        - Known pressure codes (A06, L02) resolve to correct human-readable text
        - Both species and habitat pressure records are present
        - Ranking column contains 'H', 'M', 'L' values
    """

    def test_label_join_coverage(self, pressures_df):
        pct = pressures_df["label"].notna().mean()
        assert pct >= 0.95, (
            f"Expected >= 95% label coverage, got {pct:.1%}. "
            "Possible mismatch between pressure codes and reference table."
        )

    def test_known_code_a06_label(self, pressures_df):
        a06 = pressures_df[pressures_df["pressurecode"] == "A06"]
        assert len(a06) > 0, "No rows found for pressure code A06"
        label = a06["label"].dropna().iloc[0].lower()
        assert "grassland" in label, (
            f"Expected 'grassland' in A06 label, got: {label}"
        )

    def test_known_code_l02_label(self, pressures_df):
        l02 = pressures_df[pressures_df["pressurecode"] == "L02"]
        assert len(l02) > 0, "No rows found for pressure code L02"
        label = l02["label"].dropna().iloc[0].lower()
        assert "succession" in label, (
            f"Expected 'succession' in L02 label, got: {label}"
        )

    def test_both_feature_types_present(self, pressures_df):
        types = set(pressures_df["featuretype"].dropna().unique())
        assert "species"  in types, "Expected 'species' in featuretype column"
        assert "habitats" in types, "Expected 'habitats' in featuretype column"

    def test_ranking_values_are_valid(self, pressures_df):
        valid_rankings = {"H", "M", "L"}
        actual = set(pressures_df["ranking"].dropna().unique())
        invalid = actual - valid_rankings
        assert not invalid, f"Unexpected ranking values: {invalid}"

    def test_high_ranking_records_present(self, pressures_df):
        h_count = (pressures_df["ranking"] == "H").sum()
        assert h_count > 10_000, (
            f"Expected > 10,000 high-ranking records, got {h_count}"
        )
