from pathlib import Path
import json
import re

import numpy as np
import pandas as pd

# ============================================================
# SAKAN - DATA CLEANING PIPELINE
# Reproducible data cleaning with audit reports.
# Original source CSV files are never modified.
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
AUDIT_DIR = OUTPUT_DIR / "audit"
CLEAN_DIR = OUTPUT_DIR / "cleaned"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)

RENTALS_PATH = DATA_DIR / "cairo_rentals.csv"
DISTRICTS_PATH = DATA_DIR / "district_info.csv"

# Review thresholds only: these flags do NOT remove records.
SUSPICIOUS_HIGH_RENT_EGP = 100_000
SUSPICIOUS_LARGE_SIZE_SQM = 500
SUSPICIOUS_RENT_CODES = {999_999.0, 1_000_000.0}

# ------------------------------------------------------------
# 1. Load raw datasets
# ------------------------------------------------------------

rentals_raw = pd.read_csv(RENTALS_PATH)
district_raw = pd.read_csv(DISTRICTS_PATH)

original_rows = len(rentals_raw)

print("=" * 70)
print("SAKAN DATA CLEANING PIPELINE")
print("=" * 70)
print(f"Original rental records: {original_rows:,}")
print(f"District metadata records: {len(district_raw):,}")

rentals = rentals_raw.copy(deep=True)
district_info = district_raw.copy(deep=True)

# Preserve pre-conversion values so audit flags can distinguish genuinely
# missing values from non-empty values that could not be parsed.
raw_rent_values = rentals["monthly_rent_egp"].copy() if "monthly_rent_egp" in rentals.columns else None
raw_size_values = rentals["size_sqm"].copy() if "size_sqm" in rentals.columns else None
raw_furnishing_values = rentals["furnished"].copy() if "furnished" in rentals.columns else None
raw_district_values = rentals["district"].copy() if "district" in rentals.columns else None

# ------------------------------------------------------------
# 2. Standardize column names and text whitespace
# ------------------------------------------------------------

rentals.columns = rentals.columns.str.strip()
district_info.columns = district_info.columns.str.strip()

text_columns = rentals.select_dtypes(
    include=["object", "string"]
).columns

for column in text_columns:
    rentals[column] = rentals[column].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

text_columns = district_info.select_dtypes(
    include=["object", "string"]
).columns

for column in text_columns:
    district_info[column] = district_info[column].map(
        lambda value: value.strip() if isinstance(value, str) else value
    )

# ------------------------------------------------------------
# 3. Remove exact duplicate rows
# ------------------------------------------------------------

exact_duplicates_removed = int(rentals.duplicated().sum())
rentals = rentals.drop_duplicates().copy()

print("\n[1] Exact duplicate rows removed:", exact_duplicates_removed)

# ------------------------------------------------------------
# 4. Normalize district names
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


if "district" in rentals.columns:
    rentals["district"] = rentals["district"].map(normalize_district)

if "district" in district_info.columns:
    district_info["district"] = district_info["district"].map(normalize_district)

print("\n[2] District names normalized.")

# ------------------------------------------------------------
# 5. Normalize furnishing categories
# ------------------------------------------------------------

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


if "furnished" in rentals.columns:
    original_furnishing = rentals["furnished"].copy()
    rentals["furnished"] = rentals["furnished"].map(normalize_furnishing)

    unknown_furnishing = (
        original_furnishing.notna() & rentals["furnished"].isna()
    )

    unknown_furnishing_values = pd.DataFrame({
        "original_value": original_furnishing[unknown_furnishing].astype(str).values
    })

    unknown_furnishing_values.to_csv(
        AUDIT_DIR / "unmapped_furnishing_values.csv",
        index=False
    )

print("\n[3] Furnishing categories normalized.")

# ------------------------------------------------------------
# 6. Parse numeric fields
# ------------------------------------------------------------

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

    # Accept only a numeric representation.
    if not re.fullmatch(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)", text):
        return np.nan

    try:
        return float(text)
    except ValueError:
        return np.nan


for column in ["monthly_rent_egp", "size_sqm"]:
    if column in rentals.columns:
        rentals[column] = rentals[column].map(parse_numeric_text)

if "rooms" in rentals.columns:
    rentals["rooms"] = pd.to_numeric(rentals["rooms"], errors="coerce")

print("\n[4] Numeric fields converted.")

# ------------------------------------------------------------
# 7. Parse listing dates
# ------------------------------------------------------------

if "listing_date" in rentals.columns:
    original_dates = rentals["listing_date"].copy()

    # IMPORTANT:
    # format="mixed" allows ISO dates and slash-separated dates to coexist.
    # dayfirst=True interprets dates such as 30/01/2026 correctly.
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

    invalid_dates.to_csv(
        AUDIT_DIR / "invalid_dates_after_cleaning.csv",
        index=False
    )

print("\n[5] Listing dates parsed.")

# ------------------------------------------------------------
# 8. Identify repeated listing IDs
# ------------------------------------------------------------

duplicate_id_report = pd.DataFrame()

if "listing_id" in rentals.columns:
    duplicate_id_mask = rentals["listing_id"].duplicated(keep=False)

    duplicate_id_report = rentals.loc[duplicate_id_mask].sort_values(
        "listing_id",
        na_position="last"
    ).copy()

    duplicate_id_report.to_csv(
        AUDIT_DIR / "duplicate_listing_ids_after_exact_dedup.csv",
        index=False
    )

print("\n[6] Repeated listing IDs inspected.")

# Do not automatically discard conflicting records that share
# a listing_id. They are retained for further investigation.

# ------------------------------------------------------------
# 9. Flag impossible, missing, and suspicious values
# ------------------------------------------------------------

quality_flags = pd.DataFrame(index=rentals.index)

if "monthly_rent_egp" in rentals.columns:
    rent = rentals["monthly_rent_egp"]
    raw_rent_text = raw_rent_values.astype("string").str.strip()
    quality_flags["invalid_rent"] = rent.notna() & (rent <= 0)
    quality_flags["rent_missing_or_unparseable"] = rent.isna()
    quality_flags["rent_original_missing"] = raw_rent_values.isna()
    quality_flags["rent_unparseable_nonmissing"] = (
        raw_rent_values.notna() & rent.isna()
    )
    quality_flags["suspicious_high_rent"] = rent.ge(SUSPICIOUS_HIGH_RENT_EGP).fillna(False)
    quality_flags["suspicious_rent_code"] = rent.isin(SUSPICIOUS_RENT_CODES)

if "size_sqm" in rentals.columns:
    size = rentals["size_sqm"]
    quality_flags["invalid_size"] = size.notna() & (size <= 0)
    quality_flags["size_missing_or_unparseable"] = size.isna()
    quality_flags["size_original_missing"] = raw_size_values.isna()
    quality_flags["size_unparseable_nonmissing"] = (
        raw_size_values.notna() & size.isna()
    )
    quality_flags["suspicious_large_size"] = size.ge(SUSPICIOUS_LARGE_SIZE_SQM).fillna(False)

if "district" in rentals.columns:
    quality_flags["missing_district"] = (
        rentals["district"].isna()
        | rentals["district"].astype("string").str.strip().eq("").fillna(False)
    )

if "furnished" in rentals.columns:
    quality_flags["missing_or_unmapped_furnishing"] = rentals["furnished"].isna()
    quality_flags["furnishing_original_missing"] = raw_furnishing_values.isna()
    quality_flags["furnishing_unmapped_nonmissing"] = (
        raw_furnishing_values.notna() & rentals["furnished"].isna()
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

# A compact audit summary makes the quality flags easy to review.
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
    AUDIT_DIR / "cleaning_quality_flag_summary.csv",
    index=False
)

# Preserve all quality flags alongside cleaned listing information.
flagged_records = rentals.join(quality_flags.add_prefix("flag_"))
flagged_records.to_csv(
    AUDIT_DIR / "cleaning_quality_flags.csv",
    index=False
)

print("\n[7] Quality flags generated.")
print(quality_flag_summary.to_string(index=False))

# ------------------------------------------------------------
# 10. Define core analytical eligibility
# ------------------------------------------------------------

# We do not use IQR alone as a deletion rule.
# Statistically unusual but plausible properties are preserved
# for further review.

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
)

# Keep records with valid core fields for the main rental analysis.
core_eligible_mask = (
    valid_rent & valid_size & valid_district & valid_rooms
)

core_eligible = rentals.loc[core_eligible_mask].copy()

# The cleaned general dataset preserves records that may still be
# useful for analyses not requiring every core field.
rentals_clean = rentals.copy()

# ------------------------------------------------------------
# 11. Validate district metadata before merging
# ------------------------------------------------------------

metadata_duplicate_names = district_info[
    district_info["district"].duplicated(keep=False)
].copy()

metadata_duplicate_names.to_csv(
    AUDIT_DIR / "duplicate_district_metadata_names.csv",
    index=False
)

if district_info["district"].duplicated().any():
    raise ValueError(
        "District metadata contains duplicate district keys after "
        "normalization. Resolve them before merging."
    )

# ------------------------------------------------------------
# 12. Create analysis features
# ------------------------------------------------------------

rentals_clean["price_per_sqm"] = np.where(
    rentals_clean["monthly_rent_egp"].gt(0)
    & rentals_clean["size_sqm"].gt(0),
    rentals_clean["monthly_rent_egp"] / rentals_clean["size_sqm"],
    np.nan
)

rentals_clean["listing_month"] = (
    rentals_clean["listing_date"].dt.to_period("M")
)

core_eligible["price_per_sqm"] = (
    core_eligible["monthly_rent_egp"] / core_eligible["size_sqm"]
)

core_eligible["listing_month"] = (
    core_eligible["listing_date"].dt.to_period("M")
)

# ------------------------------------------------------------
# 13. Merge district metadata
# ------------------------------------------------------------

merged = rentals_clean.merge(
    district_info,
    on="district",
    how="left",
    validate="many_to_one",
    indicator=True
)

merge_report = (
    merged["_merge"]
    .value_counts(dropna=False)
    .rename_axis("merge_status")
    .reset_index(name="row_count")
)

merge_report.to_csv(
    AUDIT_DIR / "district_merge_report.csv",
    index=False
)

unmatched_districts = (
    merged.loc[merged["_merge"] == "left_only", "district"]
    .dropna()
    .value_counts()
    .rename_axis("district")
    .reset_index(name="listing_count")
)

unmatched_districts.to_csv(
    AUDIT_DIR / "unmatched_districts.csv",
    index=False
)

merged.drop(columns=["_merge"]).to_csv(
    CLEAN_DIR / "cairo_rentals_cleaned.csv",
    index=False
)

core_eligible.to_csv(
    CLEAN_DIR / "cairo_rentals_core_eligible.csv",
    index=False
)

district_info.to_csv(
    CLEAN_DIR / "district_info_cleaned.csv",
    index=False
)

# ------------------------------------------------------------
# 14. Generate cleaning summary
# ------------------------------------------------------------

summary = {
    "original_rows": int(original_rows),
    "rows_after_exact_duplicate_removal": int(len(rentals)),
    "exact_duplicate_rows_removed": int(exact_duplicates_removed),
    "rows_with_valid_positive_rent": int(valid_rent.sum()),
    "rows_with_valid_positive_size": int(valid_size.sum()),
    "rows_with_valid_district": int(valid_district.sum()),
    "rows_with_valid_rooms": int(valid_rooms.sum()),
    "core_eligible_rows": int(core_eligible_mask.sum()),
    "rows_excluded_from_core_analysis": int((~core_eligible_mask).sum()),
    "missing_dates_after_parsing": int(rentals["listing_date"].isna().sum()),
    "unparseable_nonmissing_dates": int(
        (rentals_raw["listing_date"].notna()
         & pd.to_datetime(
             rentals_raw["listing_date"],
             errors="coerce",
             format="mixed",
             dayfirst=True
         ).isna()).sum()
    ),
    "unmatched_merged_rows": int((merged["_merge"] == "left_only").sum()),
    "repeated_listing_id_rows_after_exact_dedup": int(
        duplicate_id_report.shape[0]
    ),
    "furnishing_categories_after_normalization": sorted(
        rentals["furnished"].dropna().unique().tolist()
    ),
    "suspicious_high_rent_rows": int(quality_flags.get("suspicious_high_rent", pd.Series(False, index=rentals.index)).sum()),
    "suspicious_rent_code_rows": int(quality_flags.get("suspicious_rent_code", pd.Series(False, index=rentals.index)).sum()),
    "suspicious_large_size_rows": int(quality_flags.get("suspicious_large_size", pd.Series(False, index=rentals.index)).sum()),
    "missing_or_unmapped_furnishing_rows": int(quality_flags.get("missing_or_unmapped_furnishing", pd.Series(False, index=rentals.index)).sum()),
    "missing_coordinate_rows": int(quality_flags.get("missing_coordinates", pd.Series(False, index=rentals.index)).sum()),
    "out_of_range_coordinate_rows": int(quality_flags.get("out_of_range_coordinates", pd.Series(False, index=rentals.index)).sum()),
}

with open(
    AUDIT_DIR / "cleaning_summary.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        summary,
        file,
        ensure_ascii=False,
        indent=4,
        default=str
    )

print("\n" + "=" * 70)
print("CLEANING PIPELINE COMPLETED")
print("=" * 70)

for key, value in summary.items():
    print(f"{key}: {value}")

print("\nCleaned datasets saved to:", CLEAN_DIR)
print("Audit reports saved to:", AUDIT_DIR)
print("\nOriginal source files were not modified.")
