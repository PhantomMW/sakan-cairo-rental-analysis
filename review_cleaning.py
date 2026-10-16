from pathlib import Path
import json
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CLEAN_DIR = ROOT / "outputs" / "cleaned"
AUDIT_DIR = ROOT / "outputs" / "audit"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# 1. Load original and cleaned datasets
# ============================================================

raw = pd.read_csv(DATA_DIR / "cairo_rentals.csv")

clean = pd.read_csv(
    CLEAN_DIR / "cairo_rentals_cleaned.csv"
)

core = pd.read_csv(
    CLEAN_DIR / "cairo_rentals_core_eligible.csv"
)

print("=" * 70)
print("POST-CLEANING QUALITY REVIEW")
print("=" * 70)

print("\nDataset dimensions")
print("-" * 70)

print("Original:", raw.shape)
print("Cleaned:", clean.shape)
print("Core eligible:", core.shape)

# ============================================================
# 2. Audit original and cleaned dates
# ============================================================

print("\nDATE QUALITY")
print("-" * 70)

raw_dates = pd.to_datetime(
    raw["listing_date"],
    errors="coerce",
    format="mixed",
    dayfirst=True
)

clean_dates = pd.to_datetime(
    clean["listing_date"],
    errors="coerce",
    format="mixed",
    dayfirst=True
)

date_report = {
    "original_rows": int(len(raw)),
    "original_missing_dates": int(
        raw["listing_date"].isna().sum()
    ),
    "original_unparseable_nonmissing_dates": int(
        (
            raw["listing_date"].notna()
            & raw_dates.isna()
        ).sum()
    ),
    "cleaned_rows": int(len(clean)),
    "cleaned_missing_dates": int(
        clean["listing_date"].isna().sum()
    ),
    "cleaned_parseable_dates": int(
        clean_dates.notna().sum()
    ),
}

for key, value in date_report.items():
    print(f"{key}: {value}")

# Save invalid original date examples.
bad_original_dates = raw.loc[
    raw["listing_date"].notna() & raw_dates.isna()
].copy()

bad_original_dates.to_csv(
    AUDIT_DIR / "date_review_original_invalid.csv",
    index=False
)

# ============================================================
# 3. Inspect district matching
# ============================================================

print("\nDISTRICT MATCHING")
print("-" * 70)

district_report_path = (
    AUDIT_DIR / "unmatched_districts.csv"
)

if district_report_path.exists():
    unmatched = pd.read_csv(district_report_path)

    if unmatched.empty:
        print("No unmatched named districts.")
    else:
        print(unmatched.to_string(index=False))
else:
    print("Unmatched district report was not found.")

print(
    "\nMissing district values in cleaned data:",
    int(clean["district"].isna().sum())
)

# ============================================================
# 4. Review core eligibility
# ============================================================

print("\nCORE ELIGIBILITY")
print("-" * 70)

rent = pd.to_numeric(
    clean["monthly_rent_egp"],
    errors="coerce"
)

size = pd.to_numeric(
    clean["size_sqm"],
    errors="coerce"
)

rooms = pd.to_numeric(
    clean["rooms"],
    errors="coerce"
)

conditions = {
    "missing_or_invalid_rent": (
        rent.isna() | (rent <= 0)
    ),
    "missing_or_invalid_size": (
        size.isna() | (size <= 0)
    ),
    "missing_district": clean["district"].isna(),
    "missing_or_invalid_rooms": (
        rooms.isna()
        | (rooms <= 0)
        | (rooms % 1 != 0)
    ),
}

eligibility_report = pd.DataFrame({
    "condition": list(conditions.keys()),
    "affected_rows": [
        int(mask.sum())
        for mask in conditions.values()
    ]
})

print(eligibility_report.to_string(index=False))

eligibility_report.to_csv(
    AUDIT_DIR / "core_eligibility_review.csv",
    index=False
)

# Multiple conditions can affect the same row.
# Therefore, these counts must not be added to estimate unique exclusions.

# ============================================================
# 5. Review furnishing categories
# ============================================================

print("\nFURNISHING CATEGORIES")
print("-" * 70)

print(
    clean["furnished"]
    .value_counts(dropna=False)
    .to_string()
)

# ============================================================
# 6. Review positive numeric distributions
# ============================================================

print("\nNUMERIC DISTRIBUTIONS")
print("-" * 70)

for column in ["monthly_rent_egp", "size_sqm", "price_per_sqm"]:
    if column in clean.columns:
        values = pd.to_numeric(
            clean[column],
            errors="coerce"
        )

        valid = values[
            np.isfinite(values)
            & (values > 0)
        ]

        print(f"\n{column}")
        print("Valid positive values:", len(valid))

        if not valid.empty:
            print(valid.describe(
                percentiles=[0.25, 0.5, 0.75, 0.95, 0.99]
            ).to_string())

# ============================================================
# 7. Check merge-related columns
# ============================================================

print("\nMERGED METADATA COLUMNS")
print("-" * 70)

for column in [
    "population_density",
    "avg_income_index",
    "metro_access"
]:
    if column in clean.columns:
        print(
            column,
            "| Missing:",
            int(clean[column].isna().sum())
        )

# ============================================================
# 8. Save summary
# ============================================================

summary = {
    "date_review": date_report,
    "cleaned_rows": int(len(clean)),
    "core_eligible_rows": int(len(core)),
    "furnishing_categories": sorted(
        clean["furnished"].dropna().unique().tolist()
    ),
    "eligibility_conditions": {
        key: int(mask.sum())
        for key, mask in conditions.items()
    }
}

with open(
    AUDIT_DIR / "post_cleaning_review.json",
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
print("POST-CLEANING REVIEW COMPLETED")
print("=" * 70)
print("Reports saved to:", AUDIT_DIR)
