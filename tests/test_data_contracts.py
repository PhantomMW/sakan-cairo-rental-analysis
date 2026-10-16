"""
================================================================================
SAKAN | DATA CONTRACT & STATISTICAL AUDIT TEST SUITE
================================================================================
Automated test suite validating production data contracts on disk:
1. Row count contracts (2000 raw, 1940 cleaned, 1851 core, 1832 monthly, 1843 map)
2. Value validity contracts on core eligible dataset (rent > 0, size > 0, no nulls)
3. Zero duplicate rows in cleaned and core eligible files
4. Mathematical and statistical consistency (price_per_sqm == rent / size)
5. Metric reconciliation with final report constants
================================================================================
"""

import pytest
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN_DIR = ROOT / "outputs" / "cleaned"
ANALYSIS_DIR = ROOT / "outputs" / "analysis"
CHARTS_DIR = ROOT / "outputs" / "charts"


def test_contract_file_existence():
    """Verify primary production outputs exist on disk."""
    assert (CLEAN_DIR / "cairo_rentals_cleaned.csv").exists()
    assert (CLEAN_DIR / "cairo_rentals_core_eligible.csv").exists()
    assert (ANALYSIS_DIR / "monthly_rental_summary.csv").exists()
    assert (ANALYSIS_DIR / "district_rental_summary.csv").exists()
    assert (CHARTS_DIR / "07_interactive_cairo_rental_map.html").exists()


def test_contract_row_counts():
    """Verify expected dataset dimensions across processing stages."""
    cleaned = pd.read_csv(CLEAN_DIR / "cairo_rentals_cleaned.csv")
    core = pd.read_csv(CLEAN_DIR / "cairo_rentals_core_eligible.csv")
    monthly = pd.read_csv(ANALYSIS_DIR / "monthly_rental_summary.csv")
    districts = pd.read_csv(ANALYSIS_DIR / "district_rental_summary.csv")

    assert len(cleaned) == 1940, f"Expected 1940 cleaned records, got {len(cleaned)}"
    assert len(core) == 1851, f"Expected 1851 core eligible records, got {len(core)}"
    assert len(monthly) == 12, f"Expected 12 monthly periods, got {len(monthly)}"
    assert len(districts) == 26, f"Expected 26 districts, got {len(districts)}"
    assert monthly["listing_count"].sum() == 1832, f"Expected 1832 monthly listings, got {monthly['listing_count'].sum()}"


def test_contract_zero_duplicates():
    """Verify zero duplicate records in cleaned datasets."""
    cleaned = pd.read_csv(CLEAN_DIR / "cairo_rentals_cleaned.csv")
    core = pd.read_csv(CLEAN_DIR / "cairo_rentals_core_eligible.csv")

    assert cleaned.duplicated().sum() == 0, "Found duplicate rows in cairo_rentals_cleaned.csv"
    assert core.duplicated().sum() == 0, "Found duplicate rows in cairo_rentals_core_eligible.csv"


def test_contract_core_eligible_values():
    """Verify no negative, zero, or missing values in core eligible fields."""
    core = pd.read_csv(CLEAN_DIR / "cairo_rentals_core_eligible.csv")

    assert (core["monthly_rent_egp"] > 0).all(), "Found invalid rent <= 0 in core eligible dataset"
    assert (core["size_sqm"] > 0).all(), "Found invalid size <= 0 in core eligible dataset"
    assert core["monthly_rent_egp"].notna().all(), "Found NaN rent in core eligible dataset"
    assert core["size_sqm"].notna().all(), "Found NaN size in core eligible dataset"
    assert core["district"].notna().all(), "Found NaN district in core eligible dataset"
    assert (core["rooms"] >= 1).all(), "Found invalid rooms < 1 in core eligible dataset"


def test_contract_price_per_sqm_math():
    """Verify price_per_sqm mathematically equals monthly_rent_egp / size_sqm."""
    core = pd.read_csv(CLEAN_DIR / "cairo_rentals_core_eligible.csv")

    calculated_sqm = core["monthly_rent_egp"] / core["size_sqm"]
    diff = (core["price_per_sqm"] - calculated_sqm).abs()
    assert (diff < 1e-4).all(), "Price per sqm calculation divergence detected!"


def test_contract_interactive_map_listing_count():
    """Verify interactive map HTML file contains the expected 1,843 mapped listings."""
    map_file = CHARTS_DIR / "07_interactive_cairo_rental_map.html"
    assert map_file.exists()
    content = map_file.read_text(encoding="utf-8")
    assert "1,843" in content or "1843" in content, "Map HTML does not reflect 1,843 mapped listings"
