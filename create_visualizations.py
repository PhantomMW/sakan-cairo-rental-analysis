from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# SAKAN - RENTAL MARKET VISUALIZATIONS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_PATH = (
    ROOT
    / "outputs"
    / "cleaned"
    / "cairo_rentals_core_eligible.csv"
)

CHART_DIR = ROOT / "outputs" / "charts"
ANALYSIS_DIR = ROOT / "outputs" / "analysis"
CHART_DIR.mkdir(parents=True, exist_ok=True)
ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid", context="notebook")

# 1. Load data
df = pd.read_csv(DATA_PATH)

for column in ["monthly_rent_egp", "size_sqm", "rooms"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

df["listing_date"] = pd.to_datetime(
    df["listing_date"],
    errors="coerce",
    format="mixed",
    dayfirst=True
)

df["price_per_sqm"] = np.where(
    df["monthly_rent_egp"].gt(0) & df["size_sqm"].gt(0),
    df["monthly_rent_egp"] / df["size_sqm"],
    np.nan
)

# Main analytical subset
valid = df.loc[
    df["district"].notna()
    & df["monthly_rent_egp"].gt(0)
    & df["size_sqm"].gt(0)
].copy()

# Sensitivity subset:
# Apply broad limits to examine whether extreme values affect results.
# These limits are for sensitivity analysis, not a claim that all
# excluded records are erroneous. Source data remains unchanged.
sensitivity_mask = (
    (valid["monthly_rent_egp"] < 100_000)
    & (valid["size_sqm"] < 500)
)
sensitivity = valid.loc[sensitivity_mask].copy()

if sensitivity.empty:
    raise ValueError(
        "Sensitivity subset is empty. Check the filtering conditions."
    )

print("=" * 70)
print("SAKAN - CREATING VISUALIZATIONS")
print("=" * 70)
print(f"Records in main subset: {len(valid):,}")
print(f"Records in sensitivity subset: {len(sensitivity):,}")
print(f"Records excluded for sensitivity analysis: {len(valid) - len(sensitivity):,}")

# ------------------------------------------------------------
# Chart 1: Median monthly rent by district
# ------------------------------------------------------------

district_rent = (
    sensitivity.groupby("district")["monthly_rent_egp"]
    .median()
    .sort_values()
)

plt.figure(figsize=(12, 9))
sns.barplot(x=district_rent.values, y=district_rent.index, color="#2563eb")
plt.title("Median Monthly Rent by District")
plt.xlabel("Median Monthly Rent (EGP)")
plt.ylabel("District")
plt.tight_layout()
plt.savefig(CHART_DIR / "01_median_rent_by_district.png", dpi=300, bbox_inches="tight")
plt.close()

# ------------------------------------------------------------
# Chart 2: Median price per square meter by district
# ------------------------------------------------------------

district_sqm = (
    sensitivity.groupby("district")["price_per_sqm"]
    .median()
    .dropna()
    .sort_values()
)

plt.figure(figsize=(12, 9))
sns.barplot(x=district_sqm.values, y=district_sqm.index, color="#059669")
plt.title("Median Monthly Rent per Square Meter by District")
plt.xlabel("Median Rent per Square Meter (EGP/m²)")
plt.ylabel("District")
plt.tight_layout()
plt.savefig(CHART_DIR / "02_median_price_per_sqm_by_district.png", dpi=300, bbox_inches="tight")
plt.close()

# ------------------------------------------------------------
# Chart 3: Monthly rent distribution
# ------------------------------------------------------------

rent_values = sensitivity["monthly_rent_egp"].dropna()

plt.figure(figsize=(11, 6))
sns.histplot(rent_values, bins=35, kde=True, color="#2563eb")
plt.title("Distribution of Monthly Rental Prices")
plt.xlabel("Monthly Rent (EGP)")
plt.ylabel("Number of Listings")
plt.tight_layout()
plt.savefig(CHART_DIR / "03_monthly_rent_distribution.png", dpi=300, bbox_inches="tight")
plt.close()

# ------------------------------------------------------------
# Chart 4: Property size vs monthly rent
# ------------------------------------------------------------

scatter_data = sensitivity.loc[
    sensitivity["size_sqm"].between(1, 500)
    & sensitivity["monthly_rent_egp"].between(1, 100_000)
].copy()

plt.figure(figsize=(10, 7))
sns.scatterplot(
    data=scatter_data,
    x="size_sqm",
    y="monthly_rent_egp",
    hue="furnished",
    alpha=0.7
)
plt.title("Property Size vs Monthly Rent")
plt.xlabel("Property Size (m²)")
plt.ylabel("Monthly Rent (EGP)")

handles, labels = plt.gca().get_legend_handles_labels()
if handles:
    plt.legend(
        handles,
        labels,
        title="Furnishing Status",
        bbox_to_anchor=(1.02, 1),
        loc="upper left"
    )

plt.tight_layout()
plt.savefig(CHART_DIR / "04_size_vs_rent.png", dpi=300, bbox_inches="tight")
plt.close()

# ------------------------------------------------------------
# Chart 5: Rent by furnishing status
# ------------------------------------------------------------

if "furnished" in sensitivity.columns and sensitivity["furnished"].notna().any():
    furnishing_order = (
        sensitivity.groupby("furnished")["monthly_rent_egp"]
        .median()
        .sort_values()
        .index
    )

    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=sensitivity,
        x="furnished",
        y="monthly_rent_egp",
        order=furnishing_order,
        color="#3b82f6",
        showfliers=False
    )
    plt.title("Monthly Rent by Furnishing Status")
    plt.xlabel("Furnishing Status")
    plt.ylabel("Monthly Rent (EGP)")
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "05_rent_by_furnishing.png", dpi=300, bbox_inches="tight")
    plt.close()
else:
    print("WARNING: Furnishing data unavailable; chart 5 was not generated.")

# ------------------------------------------------------------
# Chart 6: Monthly median rent trend
# ------------------------------------------------------------

monthly_data = sensitivity.loc[sensitivity["listing_date"].notna()].copy()
monthly_data["listing_month"] = monthly_data["listing_date"].dt.to_period("M").astype(str)

monthly_summary = (
    monthly_data.groupby("listing_month")
    .agg(
        listing_count=("listing_id", "count"),
        median_rent=("monthly_rent_egp", "median"),
        mean_rent=("monthly_rent_egp", "mean")
    )
    .reset_index()
    .sort_values("listing_month")
)

monthly_summary.to_csv(
    ANALYSIS_DIR / "monthly_rental_summary_sensitivity.csv",
    index=False,
    float_format="%.2f"
)

if not monthly_summary.empty:
    plt.figure(figsize=(12, 6))
    sns.lineplot(
        data=monthly_summary,
        x="listing_month",
        y="median_rent",
        marker="o",
        color="#2563eb",
        linewidth=2.5
    )
    plt.title("Monthly Median Rent Trend")
    plt.xlabel("Listing Month")
    plt.ylabel("Median Monthly Rent (EGP)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(CHART_DIR / "06_monthly_median_rent_trend.png", dpi=300, bbox_inches="tight")
    plt.close()
else:
    print("WARNING: No dated records in the sensitivity subset; chart 6 was not generated.")

# ------------------------------------------------------------
# Save chart manifest
# ------------------------------------------------------------

chart_descriptions = {
    "01_median_rent_by_district.png": "Compare median monthly rents across districts.",
    "02_median_price_per_sqm_by_district.png": "Compare median monthly rent per square meter across districts.",
    "03_monthly_rent_distribution.png": "Inspect the distribution of monthly rental prices.",
    "04_size_vs_rent.png": "Explore the relationship between property size and monthly rent.",
    "05_rent_by_furnishing.png": "Compare monthly rents across furnishing categories.",
    "06_monthly_median_rent_trend.png": "Show monthly median rent over time in the sensitivity subset.",
    "07_interactive_cairo_rental_map.html": "Interactive Cairo rental map with listing locations and geographic exploration.",
    "08_median_rent_by_room_count.png": "Compare median monthly rent across room-count categories; labels include listing counts.",
    "09_district_monthly_rent_momentum.png": "Show monthly median rent momentum across strategic districts over time."
}

manifest_path = CHART_DIR / "visualization_manifest.csv"
existing_manifest = {}
if manifest_path.exists():
    try:
        old_df = pd.read_csv(manifest_path)
        for _, row in old_df.iterrows():
            if pd.notna(row.get("chart_file")) and pd.notna(row.get("description")):
                existing_manifest[row["chart_file"]] = row["description"]
    except Exception:
        pass

combined_descriptions = {**chart_descriptions, **existing_manifest}
generated_charts = [
    name for name in combined_descriptions
    if (CHART_DIR / name).exists()
]

manifest = pd.DataFrame({
    "chart_file": generated_charts,
    "description": [combined_descriptions[name] for name in generated_charts]
})

manifest.to_csv(manifest_path, index=False)

print("\n" + "=" * 70)
print("VISUALIZATIONS COMPLETED")
print("=" * 70)

for chart in generated_charts:
    print(CHART_DIR / chart)

print("\nMonthly sensitivity summary:")
print(ANALYSIS_DIR / "monthly_rental_summary_sensitivity.csv")
print("\nManifest:")
print(CHART_DIR / "visualization_manifest.csv")
print("\nReminder: these are sensitivity-analysis charts, not cleaned truth labels.")
