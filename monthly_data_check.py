from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT
    / "outputs"
    / "cleaned"
    / "cairo_rentals_core_eligible.csv"
)

OUTPUT_DIR = ROOT / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

df["listing_date"] = pd.to_datetime(
    df["listing_date"],
    errors="coerce"
)

df["monthly_rent_egp"] = pd.to_numeric(
    df["monthly_rent_egp"],
    errors="coerce"
)

df["listing_month"] = (
    df["listing_date"].dt.to_period("M").astype("string")
)

valid = df.loc[
    df["listing_month"].notna()
    & df["monthly_rent_egp"].gt(0)
].copy()

monthly_summary = (
    valid.groupby("listing_month")
    .agg(
        listing_count=("listing_id", "count"),
        median_monthly_rent_egp=("monthly_rent_egp", "median"),
        mean_monthly_rent_egp=("monthly_rent_egp", "mean"),
        minimum_rent_egp=("monthly_rent_egp", "min"),
        maximum_rent_egp=("monthly_rent_egp", "max")
    )
    .reset_index()
    .sort_values("listing_month")
)

monthly_summary.to_csv(
    OUTPUT_DIR / "monthly_rental_summary.csv",
    index=False
)

print("=" * 70)
print("MONTHLY RENTAL DATA CHECK")
print("=" * 70)

print(f"Eligible records: {len(df):,}")
print(f"Records with valid dates and positive rent: {len(valid):,}")
print(f"Records excluded from monthly analysis: {len(df) - len(valid):,}")

print("\nListings and rent statistics by month:")
print(monthly_summary.to_string(index=False))

print("\nSaved to:")
print(OUTPUT_DIR / "monthly_rental_summary.csv")
