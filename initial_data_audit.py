from pathlib import Path
import json
import pandas as pd
import numpy as np

# ============================================================
# SAKAN PROJECT - INITIAL DATA QUALITY AUDIT
# This script inspects the original datasets without modifying
# or deleting any source records.
# ============================================================

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
OUTPUT_DIR = PROJECT_DIR / "outputs"
AUDIT_DIR = OUTPUT_DIR / "audit"

RENTALS_PATH = DATA_DIR / "cairo_rentals.csv"
DISTRICTS_PATH = DATA_DIR / "district_info.csv"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SAKAN CAIRO RENTAL MARKET ANALYSIS")
print("INITIAL DATA QUALITY AUDIT")
print("=" * 70)

# ------------------------------------------------------------
# 1. Verify source files
# ------------------------------------------------------------

for path in [RENTALS_PATH, DISTRICTS_PATH]:
    if not path.exists():
        raise FileNotFoundError(
            f"Required dataset not found: {path}\n"
            "Check that the original CSV files are inside the data folder."
        )

print("\n[1] Source files verified successfully.")

# ------------------------------------------------------------
# 2. Load original datasets
# ------------------------------------------------------------

rentals_raw = pd.read_csv(RENTALS_PATH)
district_info_raw = pd.read_csv(DISTRICTS_PATH)

print("\n[2] DATASET DIMENSIONS")
print("-" * 70)

print(f"Rental listings: {rentals_raw.shape[0]:,} rows, "
      f"{rentals_raw.shape[1]} columns")

print(f"District metadata: {district_info_raw.shape[0]:,} rows, "
      f"{district_info_raw.shape[1]} columns")

# ------------------------------------------------------------
# 3. Inspect column names and data types
# ------------------------------------------------------------

print("\n[3] RENTAL DATASET COLUMNS")
print("-" * 70)

for column in rentals_raw.columns:
    print(f"{column:<30} {rentals_raw[column].dtype}")

print("\n[4] DISTRICT METADATA COLUMNS")
print("-" * 70)

for column in district_info_raw.columns:
    print(f"{column:<30} {district_info_raw[column].dtype}")

# ------------------------------------------------------------
# 4. Missing-value analysis
# ------------------------------------------------------------

def build_missing_report(df, dataset_name):
    return pd.DataFrame({
        "dataset": dataset_name,
        "column": df.columns,
        "data_type": [str(df[c].dtype) for c in df.columns],
        "missing_count": [int(df[c].isna().sum()) for c in df.columns],
        "missing_percentage": [
            round(float(df[c].isna().mean() * 100), 2)
            for c in df.columns
        ],
        "unique_values": [
            int(df[c].nunique(dropna=True))
            for c in df.columns
        ]
    })

missing_report = pd.concat(
    [
        build_missing_report(rentals_raw, "rental_listings"),
        build_missing_report(district_info_raw, "district_metadata")
    ],
    ignore_index=True
)

missing_report.to_csv(
    AUDIT_DIR / "missing_values_report.csv",
    index=False
)

print("\n[5] MISSING VALUES")
print("-" * 70)

print(
    missing_report[
        ["dataset", "column", "missing_count", "missing_percentage"]
    ].to_string(index=False)
)

# ------------------------------------------------------------
# 5. Duplicate analysis
# ------------------------------------------------------------

duplicate_summary = {
    "rental_rows_original": int(len(rentals_raw)),
    "exact_duplicate_rows": int(rentals_raw.duplicated().sum()),
    "district_rows_original": int(len(district_info_raw)),
    "district_exact_duplicate_rows": int(
        district_info_raw.duplicated().sum()
    )
}

if "listing_id" in rentals_raw.columns:
    duplicate_summary["listing_id_duplicate_rows"] = int(
        rentals_raw["listing_id"].duplicated(keep=False).sum()
    )
    duplicate_summary["listing_id_duplicate_excess"] = int(
        rentals_raw["listing_id"].duplicated().sum()
    )
    duplicate_summary["listing_id_distinct_nonmissing"] = int(
        rentals_raw["listing_id"].nunique(dropna=True)
    )

if "district" in district_info_raw.columns:
    duplicate_summary["district_name_duplicate_rows"] = int(
        district_info_raw["district"].duplicated(keep=False).sum()
    )
    duplicate_summary["district_name_duplicate_excess"] = int(
        district_info_raw["district"].duplicated().sum()
    )

print("\n[6] DUPLICATE ANALYSIS")
print("-" * 70)

for key, value in duplicate_summary.items():
    print(f"{key}: {value}")

# Save potentially repeated listing IDs for manual inspection.
if "listing_id" in rentals_raw.columns:
    repeated_ids = rentals_raw[
        rentals_raw["listing_id"].duplicated(keep=False)
    ].sort_values("listing_id", na_position="last")

    repeated_ids.to_csv(
        AUDIT_DIR / "repeated_listing_ids.csv",
        index=False
    )

# ------------------------------------------------------------
# 6. Numeric-column inspection
# ------------------------------------------------------------

numeric_summary = rentals_raw.describe(
    include="all"
).transpose()

numeric_summary.to_csv(
    AUDIT_DIR / "rental_descriptive_statistics.csv"
)

print("\n[7] NUMERIC AND DESCRIPTIVE STATISTICS")
print("-" * 70)

for column in ["monthly_rent_egp", "size_sqm", "rooms"]:
    if column in rentals_raw.columns:
        numeric_values = pd.to_numeric(
            rentals_raw[column],
            errors="coerce"
        )

        print(f"\nColumn: {column}")
        print(f"Valid numeric values: {numeric_values.notna().sum()}")
        print(f"Unconvertible nonmissing values: "
              f"{(rentals_raw[column].notna() & numeric_values.isna()).sum()}")

        if numeric_values.notna().any():
            print(f"Minimum: {numeric_values.min()}")
            print(f"Median: {numeric_values.median()}")
            print(f"Maximum: {numeric_values.max()}")

# ------------------------------------------------------------
# 7. Inspect suspicious rental prices
# ------------------------------------------------------------

if "monthly_rent_egp" in rentals_raw.columns:
    rent = pd.to_numeric(
        rentals_raw["monthly_rent_egp"],
        errors="coerce"
    )

    invalid_rent_mask = rent.notna() & (rent <= 0)

    q1 = rent.quantile(0.25)
    q3 = rent.quantile(0.75)
    iqr = q3 - q1

    upper_iqr_bound = (
        q3 + 1.5 * iqr
        if pd.notna(iqr)
        else np.nan
    )

    extreme_rent_mask = (
        rent.notna()
        & (rent > upper_iqr_bound)
        if pd.notna(upper_iqr_bound)
        else pd.Series(False, index=rent.index)
    )

    rent_audit = rentals_raw.loc[
        invalid_rent_mask | extreme_rent_mask
    ].copy()

    rent_audit["audit_reason"] = [
        "Non-positive rental price" if invalid_rent_mask.loc[idx]
        else "Above exploratory IQR upper bound"
        for idx in rent_audit.index
    ]

    rent_audit.to_csv(
        AUDIT_DIR / "potential_rent_anomalies.csv",
        index=False
    )

    print("\n[8] RENT PRICE ANOMALIES")
    print("-" * 70)
    print(f"Non-positive rental prices: {int(invalid_rent_mask.sum())}")
    print(f"Above exploratory IQR upper bound: "
          f"{int(extreme_rent_mask.sum())}")
    print("Potential anomalies saved for review.")

# ------------------------------------------------------------
# 8. Inspect suspicious property sizes
# ------------------------------------------------------------

if "size_sqm" in rentals_raw.columns:
    size = pd.to_numeric(
        rentals_raw["size_sqm"],
        errors="coerce"
    )

    invalid_size_mask = size.notna() & (size <= 0)

    q1 = size.quantile(0.25)
    q3 = size.quantile(0.75)
    iqr = q3 - q1

    upper_iqr_bound = (
        q3 + 1.5 * iqr
        if pd.notna(iqr)
        else np.nan
    )

    extreme_size_mask = (
        size.notna()
        & (size > upper_iqr_bound)
        if pd.notna(upper_iqr_bound)
        else pd.Series(False, index=size.index)
    )

    size_audit = rentals_raw.loc[
        invalid_size_mask | extreme_size_mask
    ].copy()

    size_audit["audit_reason"] = [
        "Non-positive property size" if invalid_size_mask.loc[idx]
        else "Above exploratory IQR upper bound"
        for idx in size_audit.index
    ]

    size_audit.to_csv(
        AUDIT_DIR / "potential_size_anomalies.csv",
        index=False
    )

    print("\n[9] PROPERTY SIZE ANOMALIES")
    print("-" * 70)
    print(f"Non-positive property sizes: {int(invalid_size_mask.sum())}")
    print(f"Above exploratory IQR upper bound: "
          f"{int(extreme_size_mask.sum())}")
    print("Potential anomalies saved for review.")

# ------------------------------------------------------------
# 9. Inspect category consistency
# ------------------------------------------------------------

category_columns = [
    column for column in ["district", "furnished"]
    if column in rentals_raw.columns
]

category_report = {}

for column in category_columns:
    values = (
        rentals_raw[column]
        .dropna()
        .astype(str)
        .str.strip()
    )

    category_report[column] = {
        str(value): int(count)
        for value, count in values.value_counts().items()
    }

    print(f"\n[10] DISTINCT VALUES IN {column.upper()}")
    print("-" * 70)

    print(values.value_counts(dropna=False).to_string())

with open(
    AUDIT_DIR / "category_values_report.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        category_report,
        file,
        ensure_ascii=False,
        indent=4
    )

# ------------------------------------------------------------
# 10. Inspect listing dates
# ------------------------------------------------------------

if "listing_date" in rentals_raw.columns:
    parsed_dates = pd.to_datetime(
        rentals_raw["listing_date"],
        errors="coerce"
    )

    invalid_date_mask = (
        rentals_raw["listing_date"].notna()
        & parsed_dates.isna()
    )

    print("\n[11] LISTING DATE AUDIT")
    print("-" * 70)
    print(f"Missing dates: {int(rentals_raw['listing_date'].isna().sum())}")
    print(f"Invalid nonmissing dates: {int(invalid_date_mask.sum())}")
    print(f"Valid parsed dates: {int(parsed_dates.notna().sum())}")

    valid_dates = parsed_dates.dropna()

    if not valid_dates.empty:
        print(f"Earliest listing date: {valid_dates.min()}")
        print(f"Latest listing date: {valid_dates.max()}")

    date_audit = rentals_raw.loc[invalid_date_mask].copy()

    date_audit.to_csv(
        AUDIT_DIR / "invalid_listing_dates.csv",
        index=False
    )

# ------------------------------------------------------------
# 11. Compare district names across datasets
# ------------------------------------------------------------

if (
    "district" in rentals_raw.columns
    and "district" in district_info_raw.columns
):
    rental_districts = set(
        rentals_raw["district"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    metadata_districts = set(
        district_info_raw["district"]
        .dropna()
        .astype(str)
        .str.strip()
        .str.casefold()
    )

    unmatched_rental_districts = sorted(
        rental_districts - metadata_districts
    )

    metadata_only_districts = sorted(
        metadata_districts - rental_districts
    )

    district_matching_report = {
        "rental_districts_not_in_metadata": unmatched_rental_districts,
        "metadata_districts_without_listings": metadata_only_districts
    }

    with open(
        AUDIT_DIR / "district_matching_report.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            district_matching_report,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n[12] DISTRICT MATCHING")
    print("-" * 70)
    print("Rental district names not matched in metadata:")
    print(unmatched_rental_districts)

    print("\nMetadata district names without matching listings:")
    print(metadata_only_districts)

# ------------------------------------------------------------
# 12. Save the audit summary
# ------------------------------------------------------------

summary = {
    "rental_rows": int(len(rentals_raw)),
    "rental_columns": int(len(rentals_raw.columns)),
    "district_metadata_rows": int(len(district_info_raw)),
    "district_metadata_columns": int(len(district_info_raw.columns)),
    "rental_exact_duplicates": int(rentals_raw.duplicated().sum()),
    "district_exact_duplicates": int(district_info_raw.duplicated().sum()),
    "rental_missing_cells": int(rentals_raw.isna().sum().sum()),
    "district_missing_cells": int(district_info_raw.isna().sum().sum()),
    "rental_missing_values_by_column": {
        str(column): int(count)
        for column, count in rentals_raw.isna().sum().items()
    }
}

if "listing_id" in rentals_raw.columns:
    summary["duplicate_listing_id_excess"] = int(
        rentals_raw["listing_id"].duplicated().sum()
    )

with open(
    AUDIT_DIR / "initial_audit_summary.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(
        summary,
        file,
        ensure_ascii=False,
        indent=4
    )

print("\n" + "=" * 70)
print("INITIAL DATA QUALITY AUDIT COMPLETED SUCCESSFULLY")
print("=" * 70)
print(f"Audit reports saved in: {AUDIT_DIR}")
print("\nOriginal CSV files were not modified.")
