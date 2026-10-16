from pathlib import Path
import pandas as pd

# ============================================================
# SAKAN - RAW VALUE INSPECTION
# Inspect unparseable values before making cleaning decisions.
# Original datasets remain unchanged.
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs" / "audit"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

rentals = pd.read_csv(DATA_DIR / "cairo_rentals.csv")

# ------------------------------------------------------------
# 1. Inspect rental prices that cannot be converted to numbers
# ------------------------------------------------------------

rent_numeric = pd.to_numeric(
    rentals["monthly_rent_egp"],
    errors="coerce"
)

bad_rent_mask = (
    rentals["monthly_rent_egp"].notna()
    & rent_numeric.isna()
)

bad_rent_values = rentals.loc[
    bad_rent_mask,
    ["listing_id", "district", "monthly_rent_egp"]
].copy()

bad_rent_values.to_csv(
    OUTPUT_DIR / "unparseable_rent_values.csv",
    index=False
)

print("=" * 70)
print("UNPARSEABLE RENT VALUES")
print("=" * 70)

print(f"Count: {len(bad_rent_values)}")
print(
    bad_rent_values[
        "monthly_rent_egp"
    ].value_counts(dropna=False).head(40).to_string()
)

# ------------------------------------------------------------
# 2. Inspect property sizes that cannot be converted to numbers
# ------------------------------------------------------------

size_numeric = pd.to_numeric(
    rentals["size_sqm"],
    errors="coerce"
)

bad_size_mask = (
    rentals["size_sqm"].notna()
    & size_numeric.isna()
)

bad_size_values = rentals.loc[
    bad_size_mask,
    ["listing_id", "district", "size_sqm"]
].copy()

bad_size_values.to_csv(
    OUTPUT_DIR / "unparseable_size_values.csv",
    index=False
)

print("\n" + "=" * 70)
print("UNPARSEABLE PROPERTY SIZE VALUES")
print("=" * 70)

print(f"Count: {len(bad_size_values)}")
print(
    bad_size_values[
        "size_sqm"
    ].value_counts(dropna=False).head(40).to_string()
)

# ------------------------------------------------------------
# 3. Inspect invalid listing dates
# ------------------------------------------------------------

parsed_dates = pd.to_datetime(
    rentals["listing_date"],
    errors="coerce"
)

bad_date_mask = (
    rentals["listing_date"].notna()
    & parsed_dates.isna()
)

bad_date_values = rentals.loc[
    bad_date_mask,
    ["listing_id", "district", "listing_date"]
].copy()

bad_date_values.to_csv(
    OUTPUT_DIR / "unparseable_listing_dates.csv",
    index=False
)

print("\n" + "=" * 70)
print("UNPARSEABLE LISTING DATES")
print("=" * 70)

print(f"Count: {len(bad_date_values)}")
print(
    bad_date_values[
        "listing_date"
    ].value_counts(dropna=False).head(40).to_string()
)

# ------------------------------------------------------------
# 4. Inspect furnishing categories and district names
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("FURNISHING VALUES")
print("=" * 70)

print(
    rentals["furnished"]
    .value_counts(dropna=False)
    .to_string()
)

print("\n" + "=" * 70)
print("DISTRICT NAMES")
print("=" * 70)

print(
    rentals["district"]
    .value_counts(dropna=False)
    .to_string()
)

print("\nInspection completed.")
print(f"Reports saved to: {OUTPUT_DIR}")
