r"""
================================================================================
SAKAN | REPRODUCIBLE DATA CLEANING PIPELINE
================================================================================
Reproducible data cleaning, value standardization, and comprehensive data-quality
auditing for Greater Cairo rental listings. Original source files are never modified.

Can be executed directly from project root:
    python .\clean_data.py

Or imported by test suites and pipelines:
    from clean_data import clean_dataset, normalize_district, normalize_furnishing, parse_numeric_text
"""

from pathlib import Path
import json
import re

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
AUDIT_DIR = OUTPUT_DIR / "audit"
CLEAN_DIR = OUTPUT_DIR / "cleaned"

RENTALS_PATH = DATA_DIR / "cairo_rentals.csv"
DISTRICTS_PATH = DATA_DIR / "district_info.csv"

# Review thresholds only: these flags audit but do NOT remove records.
SUSPICIOUS_HIGH_RENT_EGP = 100_000
SUSPICIOUS_LARGE_SIZE_SQM = 500
SUSPICIOUS_RENT_CODES = {999_999.0, 1_000_000.0}

ESSENTIAL_COLUMNS = {"listing_id", "district", "size_sqm", "monthly_rent_egp"}

# ------------------------------------------------------------
# Helper Transformation Functions
# ------------------------------------------------------------

def normalize_district(value):
    if pd.isna(value):
        return np.nan

    normalized = re.sub(r"\s+", " ", str(value).strip().casefold())

    mapping = {
        "new cairo": "New Cairo",
        "nasr city": "Nasr City",
        "6 october": "6th of October",
        "6th of october": "6th of October",
        "sheikh zayed": "Sheikh Zayed",
        "el sheikh zayed": "Sheikh Zayed",
        "mohandessin": "Mohandeseen",
        "mohandeseen": "Mohandeseen",
        "madi": "Maadi",
        "maadi": "Maadi",
        "agouza": "Agouza",
        "dokki": "Dokki",
        "madinaty": "Madinaty",
        "rehab city": "Rehab City",
        "zamalek": "Zamalek",
        "mokattam": "Mokattam",
        "shoubra": "Shoubra",
        "downtown cairo": "Downtown Cairo",
        "faisal": "Faisal",
        "haram": "Haram",
        "obour city": "Obour City",
        "manial": "Manial",
        "shorouk city": "Shorouk City",
        "giza square": "Giza Square",
        "heliopolis": "Heliopolis",
        "helwan": "Helwan",
        "imbaba": "Imbaba",
        "sayeda zeinab": "Sayeda Zeinab",
        "el marg": "El Marg",
        "badr city": "Badr City",
    }

    return mapping.get(normalized, str(value).strip())


def normalize_furnishing(value):
    if pd.isna(value):
        return np.nan

    normalized = str(value).strip().casefold()

    mapping = {
        "unfurnished": "Unfurnished",
        "not furnished": "Unfurnished",
        "n": "Unfurnished",
        "no": "Unfurnished",
        "semi": "Semi-Furnished",
        "semi-furnished": "Semi-Furnished",
        "fully furnished": "Fully-Furnished",
        "fully-furnished": "Fully-Furnished",
        "furnished": "Furnished",
        "yes": "Furnished",
        "y": "Furnished",
        "f": "Furnished",
    }

    return mapping.get(normalized, np.nan)


def parse_numeric_text(value):
    if pd.isna(value):
        return np.nan

    if isinstance(value, (int, float, np.integer, np.floating)):
        return float(value)

    text = str(value).strip()

    # Remove common currency and area-unit labels.
    text = re.sub(r"(?i)\bEGP\b|\bsqm\b|\bm2\b", "", text)

    # Remove thousands separators and whitespace.
    text = text.replace(",", "")
    text = re.sub(r"\s+", "", text)

    # Accept only a valid numeric representation.
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        return np.nan

    try:
        return float(text)
    except ValueError:
        return np.nan


# ------------------------------------------------------------
# Core Modular Cleaning Function
# ------------------------------------------------------------

def clean_dataset(rentals_raw, district_raw, audit_dir=None, clean_dir=None, save_outputs=True):
    """
    Cleans raw rental listings, executes audits, flags anomalies, and produces core eligible datasets.
    """
    if audit_dir is None:
        audit_dir = AUDIT_DIR
    if clean_dir is None:
        clean_dir = CLEAN_DIR

    if save_outputs:
        audit_dir.mkdir(parents=True, exist_ok=True)
        clean_dir.mkdir(parents=True, exist_ok=True)

    original_rows = len(rentals_raw)

    # 1. Edge Case: Empty Dataset
    if rentals_raw.empty:
        empty_clean = pd.DataFrame(columns=list(rentals_raw.columns) + ["price_per_sqm", "listing_month"])
        empty_flags = pd.DataFrame()
        empty_summary = {
            "original_rows": 0,
            "rows_after_exact_duplicate_removal": 0,
            "exact_duplicate_rows_removed": 0,
            "core_eligible_rows": 0
        }
        return {
            "rentals_clean": empty_clean,
            "core_eligible": empty_clean.copy(),
            "district_info": district_raw.copy(),
            "quality_flags": empty_flags,
            "summary": empty_summary
        }

    # 2. Edge Case: Missing Essential Schema Columns
    missing_cols = ESSENTIAL_COLUMNS - set(rentals_raw.columns)
    if missing_cols:
        raise ValueError(f"Missing essential columns in rental dataset: {sorted(missing_cols)}")

    rentals = rentals_raw.copy(deep=True)
    district_info = district_raw.copy(deep=True)

    # Preserve pre-conversion values so audit flags can distinguish genuinely
    # missing values from non-empty values that could not be parsed.
    raw_rent_values = rentals["monthly_rent_egp"].copy() if "monthly_rent_egp" in rentals.columns else None
    raw_size_values = rentals["size_sqm"].copy() if "size_sqm" in rentals.columns else None
    raw_furnishing_values = rentals["furnished"].copy() if "furnished" in rentals.columns else None
    raw_district_values = rentals["district"].copy() if "district" in rentals.columns else None

    # Standardize column names and text whitespace
    rentals.columns = rentals.columns.str.strip()
    district_info.columns = district_info.columns.str.strip()

    text_columns = rentals.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        rentals[column] = rentals[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    text_columns = district_info.select_dtypes(include=["object", "string"]).columns
    for column in text_columns:
        district_info[column] = district_info[column].map(
            lambda value: value.strip() if isinstance(value, str) else value
        )

    # Remove exact duplicate rows
    exact_duplicates_removed = int(rentals.duplicated().sum())
    rentals = rentals.drop_duplicates().copy()

    # Normalize district names
    if "district" in rentals.columns:
        rentals["district"] = rentals["district"].map(normalize_district)

    if "district" in district_info.columns:
        district_info["district"] = district_info["district"].map(normalize_district)

    # Normalize furnishing categories
    if "furnished" in rentals.columns:
        original_furnishing = rentals["furnished"].copy()
        rentals["furnished"] = rentals["furnished"].map(normalize_furnishing)

        unknown_furnishing = (
            original_furnishing.notna() & rentals["furnished"].isna()
        )

        unknown_furnishing_values = pd.DataFrame({
            "original_value": original_furnishing[unknown_furnishing].astype(str).values
        })

        if save_outputs:
            unknown_furnishing_values.to_csv(
                audit_dir / "unmapped_furnishing_values.csv",
                index=False
            )

    # Parse numeric fields
    for column in ["monthly_rent_egp", "size_sqm"]:
        if column in rentals.columns:
            rentals[column] = rentals[column].map(parse_numeric_text)

    if "rooms" in rentals.columns:
        rentals["rooms"] = pd.to_numeric(rentals["rooms"], errors="coerce")

    # Parse listing dates
    if "listing_date" in rentals.columns:
        original_dates = rentals["listing_date"].copy()

        rentals["listing_date"] = pd.to_datetime(
            rentals["listing_date"],
            errors="coerce",
            format="mixed",
            dayfirst=True
        )

        invalid_date_mask = (
            original_dates.notna() & rentals["listing_date"].isna()
        )

        invalid_dates = pd.DataFrame({
            "original_listing_date": original_dates[invalid_date_mask].astype(str).values
        })

        if save_outputs:
            invalid_dates.to_csv(
                audit_dir / "invalid_dates_after_cleaning.csv",
                index=False
            )

    # Identify repeated listing IDs
    duplicate_id_report = pd.DataFrame()
    if "listing_id" in rentals.columns:
        duplicate_id_mask = rentals["listing_id"].duplicated(keep=False)
        duplicate_id_report = rentals.loc[duplicate_id_mask].sort_values(
            "listing_id",
            na_position="last"
        ).copy()

        if save_outputs:
            duplicate_id_report.to_csv(
                audit_dir / "duplicate_listing_ids_after_exact_dedup.csv",
                index=False
            )

    # Flag impossible, missing, and suspicious values
    quality_flags = pd.DataFrame(index=rentals.index)

    if "monthly_rent_egp" in rentals.columns:
        rent = rentals["monthly_rent_egp"]
        quality_flags["invalid_rent"] = rent.notna() & (rent <= 0)
        quality_flags["rent_missing_or_unparseable"] = rent.isna()
        quality_flags["rent_original_missing"] = raw_rent_values.isna() if raw_rent_values is not None else False
        quality_flags["rent_unparseable_nonmissing"] = (
            raw_rent_values.notna() & rent.isna() if raw_rent_values is not None else False
        )
        quality_flags["suspicious_high_rent"] = rent.ge(SUSPICIOUS_HIGH_RENT_EGP).fillna(False)
        quality_flags["suspicious_rent_code"] = rent.isin(SUSPICIOUS_RENT_CODES)

    if "size_sqm" in rentals.columns:
        size = rentals["size_sqm"]
        quality_flags["invalid_size"] = size.notna() & (size <= 0)
        quality_flags["size_missing_or_unparseable"] = size.isna()
        quality_flags["size_original_missing"] = raw_size_values.isna() if raw_size_values is not None else False
        quality_flags["size_unparseable_nonmissing"] = (
            raw_size_values.notna() & size.isna() if raw_size_values is not None else False
        )
        quality_flags["suspicious_large_size"] = size.ge(SUSPICIOUS_LARGE_SIZE_SQM).fillna(False)

    if "district" in rentals.columns:
        quality_flags["missing_district"] = (
            rentals["district"].isna()
            | rentals["district"].astype("string").str.strip().eq("").fillna(False)
        )

    if "furnished" in rentals.columns:
        quality_flags["missing_or_unmapped_furnishing"] = rentals["furnished"].isna()
        quality_flags["furnishing_original_missing"] = raw_furnishing_values.isna() if raw_furnishing_values is not None else False
        quality_flags["furnishing_unmapped_nonmissing"] = (
            raw_furnishing_values.notna() & rentals["furnished"].isna() if raw_furnishing_values is not None else False
        )

    if "rooms" in rentals.columns:
        rooms = rentals["rooms"]
        quality_flags["invalid_rooms"] = (
            rooms.notna() & ((rooms <= 0) | (rooms % 1 != 0))
        )
        quality_flags["rooms_missing_or_unparseable"] = rooms.isna()

    if "latitude" in rentals.columns and "longitude" in rentals.columns:
        lat = pd.to_numeric(rentals["latitude"], errors="coerce")
        lon = pd.to_numeric(rentals["longitude"], errors="coerce")
        missing_coordinate = lat.isna() | lon.isna()
        out_of_range_coordinate = (
            lat.notna()
            & lon.notna()
            & (~lat.between(-90, 90) | ~lon.between(-180, 180))
        ).fillna(False)

        quality_flags["missing_coordinates"] = missing_coordinate
        quality_flags["out_of_range_coordinates"] = out_of_range_coordinate
        quality_flags["invalid_coordinates"] = (
            missing_coordinate | out_of_range_coordinate
        )

    quality_flags = quality_flags.fillna(False).astype(bool)

    if save_outputs:
        quality_flag_summary = pd.DataFrame({
            "quality_flag": quality_flags.columns,
            "affected_rows": [int(quality_flags[column].sum()) for column in quality_flags.columns],
            "affected_percentage": [
                round(float(quality_flags[column].mean() * 100), 2)
                if len(quality_flags) else 0.0
                for column in quality_flags.columns
            ],
        })
        quality_flag_summary.to_csv(
            audit_dir / "cleaning_quality_flag_summary.csv",
            index=False
        )

        flagged_records = rentals.join(quality_flags.add_prefix("flag_"))
        flagged_records.to_csv(
            audit_dir / "cleaning_quality_flags.csv",
            index=False
        )

    # Define core analytical eligibility
    valid_rent = (
        rentals["monthly_rent_egp"].notna()
        & (rentals["monthly_rent_egp"] > 0)
    )

    valid_size = (
        rentals["size_sqm"].notna()
        & (rentals["size_sqm"] > 0)
    )

    valid_district = (
        rentals["district"].notna()
        & rentals["district"].astype(str).str.strip().ne("")
    )

    valid_rooms = (
        rentals["rooms"].notna()
        & (rentals["rooms"] > 0)
        & (rentals["rooms"] % 1 == 0)
    ) if "rooms" in rentals.columns else pd.Series(True, index=rentals.index)

    core_eligible_mask = valid_rent & valid_size & valid_district & valid_rooms
    core_eligible = rentals.loc[core_eligible_mask].copy()
    rentals_clean = rentals.copy()

    # Validate district metadata before merging
    if "district" in district_info.columns:
        if district_info["district"].duplicated().any():
            raise ValueError(
                "District metadata contains duplicate district keys after "
                "normalization. Resolve them before merging."
            )

    # Create analysis features
    rentals_clean["price_per_sqm"] = np.where(
        rentals_clean["monthly_rent_egp"].gt(0)
        & rentals_clean["size_sqm"].gt(0),
        rentals_clean["monthly_rent_egp"] / rentals_clean["size_sqm"],
        np.nan
    )

    if "listing_date" in rentals_clean.columns:
        rentals_clean["listing_month"] = (
            rentals_clean["listing_date"].dt.to_period("M")
        )

    core_eligible["price_per_sqm"] = (
        core_eligible["monthly_rent_egp"] / core_eligible["size_sqm"]
    )

    if "listing_date" in core_eligible.columns:
        core_eligible["listing_month"] = (
            core_eligible["listing_date"].dt.to_period("M")
        )

    # Merge district metadata
    merged = rentals_clean.merge(
        district_info,
        on="district",
        how="left",
        validate="many_to_one" if not district_info.empty else None,
        indicator=True
    )

    if save_outputs:
        merge_report = (
            merged["_merge"]
            .value_counts(dropna=False)
            .rename_axis("merge_status")
            .reset_index(name="row_count")
        )
        merge_report.to_csv(audit_dir / "district_merge_report.csv", index=False)

        unmatched_districts = (
            merged.loc[merged["_merge"] == "left_only", "district"]
            .dropna()
            .value_counts()
            .rename_axis("district")
            .reset_index(name="listing_count")
        )
        unmatched_districts.to_csv(audit_dir / "unmatched_districts.csv", index=False)

        merged.drop(columns=["_merge"]).to_csv(
            clean_dir / "cairo_rentals_cleaned.csv",
            index=False
        )

        core_eligible.to_csv(
            clean_dir / "cairo_rentals_core_eligible.csv",
            index=False
        )

        district_info.to_csv(
            clean_dir / "district_info_cleaned.csv",
            index=False
        )

    summary = {
        "original_rows": int(original_rows),
        "rows_after_exact_duplicate_removal": int(len(rentals)),
        "exact_duplicate_rows_removed": int(exact_duplicates_removed),
        "rows_with_valid_positive_rent": int(valid_rent.sum()),
        "rows_with_valid_positive_size": int(valid_size.sum()),
        "rows_with_valid_district": int(valid_district.sum()),
        "rows_with_valid_rooms": int(valid_rooms.sum()) if "rooms" in rentals.columns else 0,
        "core_eligible_rows": int(core_eligible_mask.sum()),
        "rows_excluded_from_core_analysis": int((~core_eligible_mask).sum()),
        "missing_dates_after_parsing": int(rentals["listing_date"].isna().sum()) if "listing_date" in rentals.columns else 0,
        "unmatched_merged_rows": int((merged["_merge"] == "left_only").sum()),
        "repeated_listing_id_rows_after_exact_dedup": int(duplicate_id_report.shape[0]),
        "furnishing_categories_after_normalization": sorted(
            rentals["furnished"].dropna().unique().tolist()
        ) if "furnished" in rentals.columns else [],
        "suspicious_high_rent_rows": int(quality_flags.get("suspicious_high_rent", pd.Series(False, index=rentals.index)).sum()),
        "suspicious_rent_code_rows": int(quality_flags.get("suspicious_rent_code", pd.Series(False, index=rentals.index)).sum()),
        "suspicious_large_size_rows": int(quality_flags.get("suspicious_large_size", pd.Series(False, index=rentals.index)).sum()),
        "missing_or_unmapped_furnishing_rows": int(quality_flags.get("missing_or_unmapped_furnishing", pd.Series(False, index=rentals.index)).sum()),
        "missing_coordinate_rows": int(quality_flags.get("missing_coordinates", pd.Series(False, index=rentals.index)).sum()),
        "out_of_range_coordinate_rows": int(quality_flags.get("out_of_range_coordinates", pd.Series(False, index=rentals.index)).sum()),
    }

    if save_outputs:
        with open(audit_dir / "cleaning_summary.json", "w", encoding="utf-8") as file:
            json.dump(summary, file, ensure_ascii=False, indent=4, default=str)

    return {
        "rentals_clean": merged.drop(columns=["_merge"]),
        "core_eligible": core_eligible,
        "district_info": district_info,
        "quality_flags": quality_flags,
        "summary": summary
    }


def main():
    print("=" * 70)
    print("SAKAN DATA CLEANING PIPELINE")
    print("=" * 70)
    rentals_raw = pd.read_csv(RENTALS_PATH)
    district_raw = pd.read_csv(DISTRICTS_PATH)
    print(f"Original rental records: {len(rentals_raw):,}")
    print(f"District metadata records: {len(district_raw):,}")

    result = clean_dataset(rentals_raw, district_raw, AUDIT_DIR, CLEAN_DIR, save_outputs=True)
    summary = result["summary"]

    print("\n[1] Exact duplicate rows removed:", summary["exact_duplicate_rows_removed"])
    print("[2] District names normalized.")
    print("[3] Furnishing categories normalized.")
    print("[4] Numeric fields converted.")
    print("[5] Listing dates parsed.")
    print("[6] Repeated listing IDs inspected.")
    print("[7] Quality flags generated.")

    print("\n" + "=" * 70)
    print("CLEANING PIPELINE COMPLETED")
    print("=" * 70)
    for key, value in summary.items():
        print(f"{key}: {value}")

    print("\nCleaned datasets saved to:", CLEAN_DIR)
    print("Audit reports saved to:", AUDIT_DIR)
    print("\nOriginal source files were not modified.")


if __name__ == "__main__":
    main()
