from pathlib import Path
import pandas as pd
import numpy as np

# SAKAN - Revised data-quality and multi-scenario sensitivity review.
# Investigative thresholds do not automatically imply invalid records.
ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
OUT = ROOT / "outputs" / "audit"
OUT.mkdir(parents=True, exist_ok=True)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)
required = {"listing_id", "district", "monthly_rent_egp", "size_sqm"}
missing = required - set(df.columns)
if missing:
    raise ValueError(f"Missing required columns: {sorted(missing)}")

for col in ["monthly_rent_egp", "size_sqm", "rooms", "latitude", "longitude"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["price_per_sqm"] = np.where(
    df["monthly_rent_egp"].gt(0) & df["size_sqm"].gt(0),
    df["monthly_rent_egp"] / df["size_sqm"], np.nan
)

df["flag_rent_nonpositive"] = df["monthly_rent_egp"].le(0)
df["flag_size_nonpositive"] = df["size_sqm"].le(0)
df["flag_rent_ge_100k"] = df["monthly_rent_egp"].ge(100_000)
df["flag_size_ge_500sqm"] = df["size_sqm"].ge(500)
df["flag_suspicious_rent_code"] = df["monthly_rent_egp"].isin([999_999, 1_000_000])
df["flag_size_ge_1000sqm"] = df["size_sqm"].ge(1_000)

print("=" * 72)
print("SAKAN - REVISED QUALITY CHECK & SENSITIVITY ANALYSIS")
print("=" * 72)
print(f"Input records: {len(df):,}")

for col in ["monthly_rent_egp", "size_sqm", "price_per_sqm"]:
    valid = df[col].dropna()
    if valid.empty:
        continue
    q1, q3 = valid.quantile([0.25, 0.75])
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    df[f"flag_{col}_iqr"] = df[col].lt(lo) | df[col].gt(hi)
    print(f"{col}: Q1={q1:,.2f}, median={valid.median():,.2f}, Q3={q3:,.2f}, IQR bounds={lo:,.2f}..{hi:,.2f}")
    print(f"  Below: {int(valid.lt(lo).sum()):,}; above: {int(valid.gt(hi).sum()):,}")

flag_cols = [c for c in df.columns if c.startswith("flag_")]
any_flag = df[flag_cols].fillna(False).astype(bool).any(axis=1)
review_cols = [c for c in [
    "listing_id", "district", "latitude", "longitude", "monthly_rent_egp",
    "size_sqm", "price_per_sqm", "rooms", "furnished", "listing_date"
] if c in df.columns]
df.loc[any_flag, review_cols + flag_cols].to_csv(OUT / "district_quality_review.csv", index=False)

base = df.loc[
    df["district"].notna() & df["monthly_rent_egp"].gt(0) & df["size_sqm"].gt(0)
].copy()

scenarios = {
    "base_valid_positive": base,
    "exclude_rent_ge_100k": base.loc[base["monthly_rent_egp"].lt(100_000)].copy(),
    "exclude_size_ge_500sqm": base.loc[base["size_sqm"].lt(500)].copy(),
    "exclude_both_ge_100k_or_500sqm": base.loc[
        base["monthly_rent_egp"].lt(100_000) & base["size_sqm"].lt(500)
    ].copy(),
    "exclude_suspicious_rent_codes": base.loc[
        ~base["monthly_rent_egp"].isin([999_999, 1_000_000])
    ].copy(),
    "exclude_size_ge_1000sqm": base.loc[base["size_sqm"].lt(1_000)].copy(),
}

def summarize(data, scenario):
    result = data.groupby("district").agg(
        listing_count=("listing_id", "count"),
        median_rent=("monthly_rent_egp", "median"),
        mean_rent=("monthly_rent_egp", "mean"),
        median_price_per_sqm=("price_per_sqm", "median"),
        mean_price_per_sqm=("price_per_sqm", "mean"),
        median_size_sqm=("size_sqm", "median"),
    ).reset_index()
    result.insert(0, "scenario", scenario)
    return result

details, totals = [], []
for name, data in scenarios.items():
    details.append(summarize(data, name))
    totals.append({
        "scenario": name,
        "listing_count": len(data),
        "district_count": data["district"].nunique(),
        "overall_median_rent": data["monthly_rent_egp"].median(),
        "overall_mean_rent": data["monthly_rent_egp"].mean(),
        "overall_median_price_per_sqm": data["price_per_sqm"].median(),
        "overall_mean_price_per_sqm": data["price_per_sqm"].mean(),
    })

detail_df = pd.concat(details, ignore_index=True)
totals_df = pd.DataFrame(totals)
detail_df.to_csv(OUT / "district_sensitivity_scenarios.csv", index=False, float_format="%.2f")
totals_df.to_csv(OUT / "sensitivity_scenario_summary.csv", index=False, float_format="%.2f")

base_summary = detail_df.loc[detail_df["scenario"].eq("base_valid_positive")].drop(columns="scenario")
comparisons = []
for name in list(scenarios.keys())[1:]:
    other = detail_df.loc[detail_df["scenario"].eq(name)].drop(columns="scenario")
    merged = base_summary.merge(other, on="district", how="outer", suffixes=("_base", "_scenario"))
    merged.insert(0, "scenario", name)
    for metric in ["listing_count", "median_rent", "median_price_per_sqm", "mean_rent", "mean_price_per_sqm", "median_size_sqm"]:
        b, s = f"{metric}_base", f"{metric}_scenario"
        merged[f"{metric}_absolute_change"] = merged[s] - merged[b]
        merged[f"{metric}_percent_change"] = np.where(
            merged[b].notna() & merged[b].ne(0),
            (merged[s] - merged[b]) / merged[b] * 100, np.nan
        )
    comparisons.append(merged)
pd.concat(comparisons, ignore_index=True).to_csv(
    OUT / "district_sensitivity_detailed_comparison.csv", index=False, float_format="%.2f"
)

integrity = pd.DataFrame([
    ("Input analytical records", len(df), "Rows in core eligible input"),
    ("Nonpositive rent", int(df["flag_rent_nonpositive"].sum()), "Invalid for rent-based analysis"),
    ("Nonpositive size", int(df["flag_size_nonpositive"].sum()), "Invalid for size and price-per-sqm analysis"),
    ("Rent >= 100,000 EGP", int(df["flag_rent_ge_100k"].sum()), "Review threshold, not automatic invalidity"),
    ("Rent exactly 999,999 or 1,000,000", int(df["flag_suspicious_rent_code"].sum()), "Potential sentinel/test values; verify source"),
    ("Size >= 500 sqm", int(df["flag_size_ge_500sqm"].sum()), "Review threshold; could include non-apartment properties"),
    ("Size >= 1,000 sqm", int(df["flag_size_ge_1000sqm"].sum()), "Extreme size threshold; manual review"),
    ("Records flagged by any rule", int(any_flag.sum()), "Flags overlap; not a unique issue count per rule"),
], columns=["check", "count", "interpretation"])
integrity.to_csv(OUT / "data_integrity_summary.csv", index=False)

print("\nScenario totals:")
print(totals_df.to_string(index=False))
print("\nReports saved:")
for name in ["district_quality_review.csv", "district_sensitivity_scenarios.csv",
             "sensitivity_scenario_summary.csv", "district_sensitivity_detailed_comparison.csv",
             "data_integrity_summary.csv"]:
    print(OUT / name)
print("\nNo source or cleaned records were deleted or modified.")
