from pathlib import Path

import numpy as np
import pandas as pd

# ============================================================
# SAKAN - OUTLIER INVESTIGATION
# This script flags suspicious values for review.
# It does not delete or modify any dataset.
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
CLEAN_DIR = ROOT / "outputs" / "cleaned"
AUDIT_DIR = ROOT / "outputs" / "audit"

AUDIT_DIR.mkdir(parents=True, exist_ok=True)

raw = pd.read_csv(DATA_DIR / "cairo_rentals.csv")

clean = pd.read_csv(
    CLEAN_DIR / "cairo_rentals_cleaned.csv"
)

# ------------------------------------------------------------
# 1. Define reusable outlier investigation function
# ------------------------------------------------------------

def investigate_outliers(df, column):
    values = pd.to_numeric(df[column], errors="coerce")

    valid_mask = values.notna() & np.isfinite(values)
    valid_values = values.loc[valid_mask]

    q1 = valid_values.quantile(0.25)
    median = valid_values.median()
    q3 = valid_values.quantile(0.75)
    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    low_mask = valid_mask & (values < lower_bound)
    high_mask = valid_mask & (values > upper_bound)

    summary = {
        "column": column,
        "valid_numeric_count": int(valid_mask.sum()),
        "q1": float(q1),
        "median": float(median),
        "q3": float(q3),
        "iqr": float(iqr),
        "lower_iqr_bound": float(lower_bound),
        "upper_iqr_bound": float(upper_bound),
        "below_lower_bound": int(low_mask.sum()),
        "above_upper_bound": int(high_mask.sum()),
        "minimum": float(valid_values.min()),
        "maximum": float(valid_values.max()),
        "mean": float(valid_values.mean()),
        "std": float(valid_values.std()),
    }

    flagged = df.loc[low_mask | high_mask].copy()
    flagged["audited_column"] = column
    flagged["audited_value"] = values.loc[flagged.index]
    flagged["outlier_direction"] = np.where(
        values.loc[flagged.index] > upper_bound,
        "Above upper IQR bound",
        "Below lower IQR bound"
    )

    return summary, flagged


# ------------------------------------------------------------
# 2. Investigate rental prices and property sizes
# ------------------------------------------------------------

all_summaries = []
all_flags = []

for column in ["monthly_rent_egp", "size_sqm"]:
    summary, flagged = investigate_outliers(clean, column)

    all_summaries.append(summary)
    all_flags.append(flagged)

    print("\n" + "=" * 70)
    print(f"OUTLIER INVESTIGATION: {column}")
    print("=" * 70)

    for key, value in summary.items():
        print(f"{key}: {value}")

summary_df = pd.DataFrame(all_summaries)

summary_df.to_csv(
    AUDIT_DIR / "outlier_statistics.csv",
    index=False
)

combined_flags = pd.concat(
    all_flags,
    ignore_index=True
)

combined_flags.to_csv(
    AUDIT_DIR / "potential_outliers_for_review.csv",
    index=False
)

# ------------------------------------------------------------
# 3. Inspect extreme rental values
# ------------------------------------------------------------

rent = pd.to_numeric(
    clean["monthly_rent_egp"],
    errors="coerce"
)

extreme_rent_mask = rent.ge(100000)

extreme_rents = clean.loc[
    extreme_rent_mask
].copy()

extreme_rents.to_csv(
    AUDIT_DIR / "extreme_rental_prices_for_review.csv",
    index=False
)

print("\n" + "=" * 70)
print("RENTAL PRICES AT OR ABOVE 100,000 EGP")
print("=" * 70)

print("Count:", len(extreme_rents))

if not extreme_rents.empty:
    columns_to_show = [
        c for c in [
            "listing_id",
            "district",
            "monthly_rent_egp",
            "size_sqm",
            "rooms",
            "furnished",
            "listing_date"
        ]
        if c in extreme_rents.columns
    ]

    print(
        extreme_rents[columns_to_show]
        .sort_values("monthly_rent_egp", ascending=False)
        .head(20)
        .to_string(index=False)
    )

# ------------------------------------------------------------
# 4. Inspect extreme property sizes
# ------------------------------------------------------------

size = pd.to_numeric(
    clean["size_sqm"],
    errors="coerce"
)

extreme_size_mask = size.ge(500)

extreme_sizes = clean.loc[
    extreme_size_mask
].copy()

extreme_sizes.to_csv(
    AUDIT_DIR / "extreme_property_sizes_for_review.csv",
    index=False
)

print("\n" + "=" * 70)
print("PROPERTY SIZES AT OR ABOVE 500 SQM")
print("=" * 70)

print("Count:", len(extreme_sizes))

if not extreme_sizes.empty:
    columns_to_show = [
        c for c in [
            "listing_id",
            "district",
            "monthly_rent_egp",
            "size_sqm",
            "rooms",
            "furnished",
            "listing_date"
        ]
        if c in extreme_sizes.columns
    ]

    print(
        extreme_sizes[columns_to_show]
        .sort_values("size_sqm", ascending=False)
        .head(20)
        .to_string(index=False)
    )

# ------------------------------------------------------------
# 5. Compare raw and cleaned descriptive statistics
# ------------------------------------------------------------

comparison_rows = []

for column in ["monthly_rent_egp", "size_sqm"]:
    raw_values = raw[column].map(
        lambda x: (
            float(str(x).replace(",", "").replace("EGP", "").replace("sqm", "").replace("m2", "").strip())
            if pd.notna(x)
            and str(x).replace(",", "").replace("EGP", "").replace("sqm", "").replace("m2", "").strip().replace(".", "", 1).replace("-", "", 1).isdigit()
            else np.nan
        )
    )

    cleaned_values = pd.to_numeric(
        clean[column],
        errors="coerce"
    )

    for stage, values in [
        ("Raw parseable values", raw_values),
        ("Cleaned numeric values", cleaned_values)
    ]:
        valid = values[
            values.notna()
            & np.isfinite(values)
            & (values > 0)
        ]

        comparison_rows.append({
            "column": column,
            "stage": stage,
            "count": int(valid.count()),
            "mean": float(valid.mean()) if not valid.empty else np.nan,
            "median": float(valid.median()) if not valid.empty else np.nan,
            "minimum": float(valid.min()) if not valid.empty else np.nan,
            "maximum": float(valid.max()) if not valid.empty else np.nan
        })

comparison = pd.DataFrame(comparison_rows)

comparison.to_csv(
    AUDIT_DIR / "raw_vs_cleaned_statistics.csv",
    index=False
)

print("\n" + "=" * 70)
print("RAW VS CLEANED STATISTICS")
print("=" * 70)
print(comparison.to_string(index=False))

print("\nInvestigation completed.")
print("No records were deleted or modified.")
print("Reports saved to:", AUDIT_DIR)
