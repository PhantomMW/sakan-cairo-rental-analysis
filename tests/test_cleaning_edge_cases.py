"""
================================================================================
SAKAN | UNIT & EDGE-CASE TEST SUITE
================================================================================
Comprehensive pytest test suite validating the 10 critical edge cases:
1. Empty dataset handling
2. Missing essential schema columns
3. Zero and negative rents and sizes
4. Extreme outlier rents (999,999 and 1,000,000 EGP)
5. Invalid or empty dates
6. Out-of-bounds geographic coordinates
7. Duplicate row detection and removal
8. Unmatched district in metadata
9. Missing or unrecognized furnishing values
10. Single-record dataset (N=1)
================================================================================
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
import sys
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from clean_data import (
    clean_dataset,
    normalize_district,
    normalize_furnishing,
    parse_numeric_text,
    SUSPICIOUS_HIGH_RENT_EGP,
    SUSPICIOUS_RENT_CODES
)

@pytest.fixture
def sample_district_metadata():
    return pd.DataFrame({
        "district": ["New Cairo", "Maadi", "Zamalek", "Nasr City", "Dokki"],
        "population_density": [3500, 12000, 14000, 18000, 22000],
        "income_index": [4.8, 4.5, 4.9, 3.8, 4.0],
        "metro_access": [0, 1, 0, 1, 1]
    })


@pytest.fixture
def base_valid_record():
    return {
        "listing_id": "SKN99001",
        "district": "New Cairo",
        "latitude": 30.0123,
        "longitude": 31.4567,
        "size_sqm": 150.0,
        "rooms": 3,
        "furnished": "Furnished",
        "monthly_rent_egp": 25000.0,
        "listing_date": "2026-03-15"
    }


# -----------------------------------------------------------------------------
# 1. Test Empty Dataset
# -----------------------------------------------------------------------------
def test_empty_dataframe(sample_district_metadata):
    empty_df = pd.DataFrame(columns=[
        "listing_id", "district", "latitude", "longitude",
        "size_sqm", "rooms", "furnished", "monthly_rent_egp", "listing_date"
    ])
    result = clean_dataset(empty_df, sample_district_metadata, save_outputs=False)

    assert result["rentals_clean"].empty
    assert result["core_eligible"].empty
    assert result["summary"]["original_rows"] == 0
    assert result["summary"]["core_eligible_rows"] == 0


# -----------------------------------------------------------------------------
# 2. Test Missing Essential Columns
# -----------------------------------------------------------------------------
def test_missing_essential_columns(sample_district_metadata, base_valid_record):
    df_missing_rent = pd.DataFrame([base_valid_record]).drop(columns=["monthly_rent_egp"])

    with pytest.raises(ValueError, match="Missing essential columns"):
        clean_dataset(df_missing_rent, sample_district_metadata, save_outputs=False)

    df_missing_district = pd.DataFrame([base_valid_record]).drop(columns=["district"])
    with pytest.raises(ValueError, match="Missing essential columns"):
        clean_dataset(df_missing_district, sample_district_metadata, save_outputs=False)


# -----------------------------------------------------------------------------
# 3. Test Zero and Negative Rents and Sizes
# -----------------------------------------------------------------------------
def test_zero_or_negative_rent_and_size(sample_district_metadata, base_valid_record):
    records = [
        # Valid record
        dict(base_valid_record, listing_id="SKN01", monthly_rent_egp=20000, size_sqm=100),
        # Zero rent
        dict(base_valid_record, listing_id="SKN02", monthly_rent_egp=0, size_sqm=100),
        # Negative rent
        dict(base_valid_record, listing_id="SKN03", monthly_rent_egp=-5000, size_sqm=100),
        # Zero size
        dict(base_valid_record, listing_id="SKN04", monthly_rent_egp=15000, size_sqm=0),
        # Negative size
        dict(base_valid_record, listing_id="SKN05", monthly_rent_egp=15000, size_sqm=-80),
    ]
    df = pd.DataFrame(records)
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    flags = result["quality_flags"]
    core = result["core_eligible"]

    # Verify flags
    assert flags.loc[1, "invalid_rent"] == True
    assert flags.loc[2, "invalid_rent"] == True
    assert flags.loc[3, "invalid_size"] == True
    assert flags.loc[4, "invalid_size"] == True

    # Core eligible must exclude all invalid values (only SKN01 qualifies)
    assert len(core) == 1
    assert core.iloc[0]["listing_id"] == "SKN01"
    assert (core["monthly_rent_egp"] > 0).all()
    assert (core["size_sqm"] > 0).all()


# -----------------------------------------------------------------------------
# 4. Test Extreme Outlier Rents (999,999 and 1,000,000 EGP)
# -----------------------------------------------------------------------------
def test_extreme_outlier_rents(sample_district_metadata, base_valid_record):
    records = [
        dict(base_valid_record, listing_id="SKN_NORM", monthly_rent_egp=30000),
        dict(base_valid_record, listing_id="SKN_999K", monthly_rent_egp=999999),
        dict(base_valid_record, listing_id="SKN_1MIL", monthly_rent_egp=1000000),
    ]
    df = pd.DataFrame(records)
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    flags = result["quality_flags"]
    core = result["core_eligible"]

    # Extreme codes must be explicitly flagged
    assert flags.loc[1, "suspicious_high_rent"] == True
    assert flags.loc[1, "suspicious_rent_code"] == True
    assert flags.loc[2, "suspicious_high_rent"] == True
    assert flags.loc[2, "suspicious_rent_code"] == True

    # Outliers must NOT be blindly dropped from core eligible dataset
    assert len(core) == 3
    assert set(core["listing_id"]) == {"SKN_NORM", "SKN_999K", "SKN_1MIL"}


# -----------------------------------------------------------------------------
# 5. Test Invalid or Empty Dates
# -----------------------------------------------------------------------------
def test_invalid_and_empty_dates(sample_district_metadata, base_valid_record):
    records = [
        dict(base_valid_record, listing_id="SKN_D1", listing_date="2026-02-15"),
        dict(base_valid_record, listing_id="SKN_D2", listing_date="invalid_date_string"),
        dict(base_valid_record, listing_id="SKN_D3", listing_date=""),
        dict(base_valid_record, listing_id="SKN_D4", listing_date=None),
    ]
    df = pd.DataFrame(records)
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    cleaned = result["rentals_clean"]
    assert pd.notna(cleaned.loc[0, "listing_date"])
    assert pd.isna(cleaned.loc[1, "listing_date"])
    assert pd.isna(cleaned.loc[2, "listing_date"])
    assert pd.isna(cleaned.loc[3, "listing_date"])


# -----------------------------------------------------------------------------
# 6. Test Out-of-Bounds Coordinates
# -----------------------------------------------------------------------------
def test_out_of_bounds_coordinates(sample_district_metadata, base_valid_record):
    records = [
        dict(base_valid_record, listing_id="SKN_OK", latitude=30.05, longitude=31.25),
        dict(base_valid_record, listing_id="SKN_BAD_LAT", latitude=120.50, longitude=31.25),
        dict(base_valid_record, listing_id="SKN_BAD_LON", latitude=30.05, longitude=-200.00),
        dict(base_valid_record, listing_id="SKN_NAN", latitude=np.nan, longitude=np.nan),
    ]
    df = pd.DataFrame(records)
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    flags = result["quality_flags"]
    assert flags.loc[0, "invalid_coordinates"] == False
    assert flags.loc[1, "out_of_range_coordinates"] == True
    assert flags.loc[2, "out_of_range_coordinates"] == True
    assert flags.loc[3, "missing_coordinates"] == True


# -----------------------------------------------------------------------------
# 7. Test Duplicate Rows
# -----------------------------------------------------------------------------
def test_duplicate_rows(sample_district_metadata, base_valid_record):
    # Repeat the identical record 3 times
    df = pd.DataFrame([base_valid_record, base_valid_record, base_valid_record])
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    assert result["summary"]["original_rows"] == 3
    assert result["summary"]["exact_duplicate_rows_removed"] == 2
    assert len(result["rentals_clean"]) == 1
    assert len(result["core_eligible"]) == 1


# -----------------------------------------------------------------------------
# 8. Test District Not Present in Metadata
# -----------------------------------------------------------------------------
def test_unmatched_district_in_metadata(sample_district_metadata, base_valid_record):
    record = dict(base_valid_record, district="NonExistentNeighborhood")
    df = pd.DataFrame([record])
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    cleaned = result["rentals_clean"]
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["district"] == "NonExistentNeighborhood"
    # Metadata fields should be NaN because the district is not in metadata
    assert pd.isna(cleaned.iloc[0]["population_density"])
    assert result["summary"]["unmatched_merged_rows"] == 1


# -----------------------------------------------------------------------------
# 9. Test Furnishing Normalization and Unknown Values
# -----------------------------------------------------------------------------
def test_furnishing_normalization_and_unknowns(sample_district_metadata, base_valid_record):
    records = [
        dict(base_valid_record, listing_id="SKN_F1", furnished="semi"),
        dict(base_valid_record, listing_id="SKN_F2", furnished="UNFURNISHED"),
        dict(base_valid_record, listing_id="SKN_F3", furnished="yes"),
        dict(base_valid_record, listing_id="SKN_F4", furnished="fully furnished"),
        dict(base_valid_record, listing_id="SKN_F5", furnished="f"),
        dict(base_valid_record, listing_id="SKN_F6", furnished="UnknownGarbageVal"),
        dict(base_valid_record, listing_id="SKN_F7", furnished=np.nan),
    ]
    df = pd.DataFrame(records)
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    cleaned = result["rentals_clean"]
    assert cleaned.loc[0, "furnished"] == "Semi-Furnished"
    assert cleaned.loc[1, "furnished"] == "Unfurnished"
    assert cleaned.loc[2, "furnished"] == "Furnished"
    assert cleaned.loc[3, "furnished"] == "Fully-Furnished"
    assert cleaned.loc[4, "furnished"] == "Furnished"
    assert pd.isna(cleaned.loc[5, "furnished"])
    assert pd.isna(cleaned.loc[6, "furnished"])


# -----------------------------------------------------------------------------
# 10. Test Single-Record Dataset (N=1)
# -----------------------------------------------------------------------------
def test_single_record_dataset(sample_district_metadata, base_valid_record):
    df = pd.DataFrame([base_valid_record])
    result = clean_dataset(df, sample_district_metadata, save_outputs=False)

    assert result["summary"]["original_rows"] == 1
    assert len(result["core_eligible"]) == 1
    # Check mathematical computation of price per sqm
    expected_sqm = base_valid_record["monthly_rent_egp"] / base_valid_record["size_sqm"]
    assert pytest.approx(result["core_eligible"].iloc[0]["price_per_sqm"], 0.01) == expected_sqm
