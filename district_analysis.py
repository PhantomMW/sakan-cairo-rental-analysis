from pathlib import Path
import pandas as pd

# ============================================================
# SAKAN - DISTRICT RENTAL ANALYSIS
# ============================================================
# Purpose:
# 1. Summarize rental prices and listing characteristics by district.
# 2. Identify affordable districts using a minimum sample size.
# 3. Test whether district rankings change when suspiciously high
#    rents and very large properties are excluded analytically.
#
# Important:
# - This script does NOT modify the source or cleaned datasets.
# - Sensitivity exclusions apply only to the sensitivity analysis.
# - Statistical outliers are not automatically deleted from the
#   primary district summary.
# ============================================================

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
OUTPUT_DIR = ROOT / "outputs" / "analysis"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

MIN_LISTINGS_PER_DISTRICT = 10
SUSPICIOUS_RENT_THRESHOLD = 100_000
SUSPICIOUS_SIZE_THRESHOLD = 500

print("=" * 75)
print("SAKAN - DISTRICT RENTAL ANALYSIS")
print("=" * 75)

# 1. Load cleaned core-eligible dataset
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Required input file was not found:\n{DATA_PATH}\n"
        "Run the cleaning/pipeline stages first."
    )

df = pd.read_csv(DATA_PATH)

print(f"\nLoaded records: {len(df):,}")
print(f"Number of columns: {len(df.columns)}")

# 2. Validate required columns
required_columns = [
    "listing_id",
    "district",
    "monthly_rent_egp",
    "size_sqm",
    "rooms",
    "furnished",
]
missing_columns = [column for column in required_columns if column not in df.columns]

if missing_columns:
    raise ValueError(f"Required columns are missing: {missing_columns}")

# 3. Convert numeric fields safely
for column in ["monthly_rent_egp", "size_sqm", "rooms"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 4. Apply analytical validity checks
# Keep suspicious but positive rent/size values in the primary analysis.
district_text = df["district"].astype("string").str.strip()
valid_mask = (
    district_text.notna()
    & district_text.ne("")
    & df["monthly_rent_egp"].gt(0)
    & df["size_sqm"].gt(0)
    & df["rooms"].gt(0)
    & (df["rooms"] % 1 == 0)
)

analysis_df = df.loc[valid_mask].copy()
analysis_df["district"] = analysis_df["district"].astype(str).str.strip()
analysis_df["price_per_sqm"] = (
    analysis_df["monthly_rent_egp"] / analysis_df["size_sqm"]
)

print(f"Valid records for district analysis: {len(analysis_df):,}")
print(f"Excluded by basic validity checks: {len(df) - len(analysis_df):,}")
print(f"Minimum listings for affordability rankings: {MIN_LISTINGS_PER_DISTRICT}")

# 5. Helper function for district-level statistics
def build_district_summary(data: pd.DataFrame) -> pd.DataFrame:
    """Create one row of rental metrics per district."""
    if data.empty:
        return pd.DataFrame(
            columns=[
                "district",
                "listing_count",
                "mean_monthly_rent_egp",
                "median_monthly_rent_egp",
                "min_monthly_rent_egp",
                "max_monthly_rent_egp",
                "mean_size_sqm",
                "median_size_sqm",
                "mean_price_per_sqm",
                "median_price_per_sqm",
                "median_rooms",
            ]
        )

    return (
        data.groupby("district", dropna=False)
        .agg(
            listing_count=("listing_id", "count"),
            mean_monthly_rent_egp=("monthly_rent_egp", "mean"),
            median_monthly_rent_egp=("monthly_rent_egp", "median"),
            min_monthly_rent_egp=("monthly_rent_egp", "min"),
            max_monthly_rent_egp=("monthly_rent_egp", "max"),
            mean_size_sqm=("size_sqm", "mean"),
            median_size_sqm=("size_sqm", "median"),
            mean_price_per_sqm=("price_per_sqm", "mean"),
            median_price_per_sqm=("price_per_sqm", "median"),
            median_rooms=("rooms", "median"),
        )
        .reset_index()
    )

# 6. Save complete primary district summary
district_summary = build_district_summary(analysis_df)
district_summary = district_summary.sort_values(
    ["median_monthly_rent_egp", "district"],
    ascending=[True, True],
).reset_index(drop=True)

summary_path = OUTPUT_DIR / "district_rental_summary.csv"
district_summary.to_csv(summary_path, index=False, float_format="%.2f")

# 7. Affordability rankings, using the same minimum sample size
reliable_districts = district_summary.loc[
    district_summary["listing_count"] >= MIN_LISTINGS_PER_DISTRICT
].copy()

affordable_by_rent = reliable_districts.sort_values(
    ["median_monthly_rent_egp", "district"],
    ascending=[True, True],
).head(10).copy()

affordable_rent_path = OUTPUT_DIR / "top_10_affordable_districts_by_rent.csv"
affordable_by_rent.to_csv(
    affordable_rent_path, index=False, float_format="%.2f"
)

affordable_by_sqm = reliable_districts.sort_values(
    ["median_price_per_sqm", "district"],
    ascending=[True, True],
).head(10).copy()

affordable_sqm_path = OUTPUT_DIR / "top_10_affordable_districts_by_sqm.csv"
affordable_by_sqm.to_csv(
    affordable_sqm_path, index=False, float_format="%.2f"
)

# 8. Save district listing counts
district_counts = (
    analysis_df["district"]
    .value_counts()
    .rename_axis("district")
    .reset_index(name="listing_count")
    .sort_values(["listing_count", "district"], ascending=[False, True])
)
district_counts.to_csv(OUTPUT_DIR / "district_listing_counts.csv", index=False)

# 9. Sensitivity analysis:
# Exclude records with rent >= threshold OR size >= threshold.
# These are analytical scenarios only; no source records are deleted.
suspicious_rent_mask = analysis_df["monthly_rent_egp"].ge(
    SUSPICIOUS_RENT_THRESHOLD
)
suspicious_size_mask = analysis_df["size_sqm"].ge(
    SUSPICIOUS_SIZE_THRESHOLD
)
sensitivity_exclusion_mask = suspicious_rent_mask | suspicious_size_mask

sensitivity_df = analysis_df.loc[~sensitivity_exclusion_mask].copy()
sensitivity_summary = build_district_summary(sensitivity_df)

# Keep districts with at least MIN_LISTINGS_PER_DISTRICT in each scenario
# before comparing rankings, so small groups do not create misleading ranks.
base_rankable = reliable_districts.copy()
sensitivity_rankable = sensitivity_summary.loc[
    sensitivity_summary["listing_count"] >= MIN_LISTINGS_PER_DISTRICT
].copy()

base_rankable["base_rent_rank"] = base_rankable[
    "median_monthly_rent_egp"
].rank(method="min", ascending=True).astype(int)
base_rankable["base_price_per_sqm_rank"] = base_rankable[
    "median_price_per_sqm"
].rank(method="min", ascending=True).astype(int)

sensitivity_rankable["sensitivity_rent_rank"] = sensitivity_rankable[
    "median_monthly_rent_egp"
].rank(method="min", ascending=True).astype(int)
sensitivity_rankable["sensitivity_price_per_sqm_rank"] = sensitivity_rankable[
    "median_price_per_sqm"
].rank(method="min", ascending=True).astype(int)

rank_comparison = base_rankable[
    [
        "district",
        "listing_count",
        "median_monthly_rent_egp",
        "median_price_per_sqm",
        "base_rent_rank",
        "base_price_per_sqm_rank",
    ]
].merge(
    sensitivity_rankable[
        [
            "district",
            "listing_count",
            "median_monthly_rent_egp",
            "median_price_per_sqm",
            "sensitivity_rent_rank",
            "sensitivity_price_per_sqm_rank",
        ]
    ],
    on="district",
    how="outer",
    suffixes=("_base", "_sensitivity"),
    indicator=True,
)

rank_comparison = rank_comparison.rename(
    columns={
        "listing_count_base": "base_listing_count",
        "median_monthly_rent_egp_base": "base_median_monthly_rent_egp",
        "median_price_per_sqm_base": "base_median_price_per_sqm",
        "listing_count_sensitivity": "sensitivity_listing_count",
        "median_monthly_rent_egp_sensitivity": "sensitivity_median_monthly_rent_egp",
        "median_price_per_sqm_sensitivity": "sensitivity_median_price_per_sqm",
    }
)

rank_comparison["rent_rank_change"] = (
    rank_comparison["sensitivity_rent_rank"] - rank_comparison["base_rent_rank"]
)
rank_comparison["price_per_sqm_rank_change"] = (
    rank_comparison["sensitivity_price_per_sqm_rank"]
    - rank_comparison["base_price_per_sqm_rank"]
)
rank_comparison["comparison_status"] = rank_comparison["_merge"].map(
    {
        "both": "Ranked in both scenarios",
        "left_only": "Meets minimum sample only in base scenario",
        "right_only": "Meets minimum sample only in sensitivity scenario",
    }
)

# Classify rank stability only after both rank-change columns are calculated.
def classify_rank_stability(change):
    """Describe how much a district's rank changed between scenarios."""
    if pd.isna(change):
        return "Not comparable"

    magnitude = abs(float(change))
    if magnitude == 0:
        return "Stable"
    if magnitude <= 2:
        return "Minor change"
    return "Major change"


rank_comparison["rent_rank_stability"] = (
    rank_comparison["rent_rank_change"].apply(classify_rank_stability)
)
rank_comparison["price_per_sqm_rank_stability"] = (
    rank_comparison["price_per_sqm_rank_change"].apply(classify_rank_stability)
)
rank_comparison = rank_comparison.drop(columns=["_merge"]).sort_values(
    ["base_rent_rank", "district"],
    na_position="last",
)

rank_comparison_path = OUTPUT_DIR / "district_ranking_sensitivity_comparison.csv"
rank_comparison.to_csv(
    rank_comparison_path, index=False, float_format="%.2f"
)

# Save the sensitivity district summary too, for transparent review.
sensitivity_summary_path = OUTPUT_DIR / "district_rental_summary_sensitivity.csv"
sensitivity_summary.sort_values(
    ["median_monthly_rent_egp", "district"],
    ascending=[True, True],
).to_csv(sensitivity_summary_path, index=False, float_format="%.2f")

# 10. Display results with accurate headings
print("\n" + "=" * 75)
print("10 MOST AFFORDABLE DISTRICTS BY MEDIAN MONTHLY RENT")
print(f"(At least {MIN_LISTINGS_PER_DISTRICT} listings per district)")
print("=" * 75)

if affordable_by_rent.empty:
    print("No districts meet the minimum listing threshold.")
else:
    print(
        affordable_by_rent[
            [
                "district",
                "listing_count",
                "median_monthly_rent_egp",
                "median_price_per_sqm",
            ]
        ].to_string(index=False)
    )

print("\n" + "=" * 75)
print("10 MOST AFFORDABLE DISTRICTS BY MEDIAN PRICE PER SQM")
print(f"(At least {MIN_LISTINGS_PER_DISTRICT} listings per district)")
print("=" * 75)

if affordable_by_sqm.empty:
    print("No districts meet the minimum listing threshold.")
else:
    print(
        affordable_by_sqm[
            [
                "district",
                "listing_count",
                "median_monthly_rent_egp",
                "median_price_per_sqm",
            ]
        ].to_string(index=False)
    )

print("\n" + "=" * 75)
print("SENSITIVITY ANALYSIS")
print("=" * 75)
print(f"Base analytical records: {len(analysis_df):,}")
print(f"Records excluded in sensitivity scenario: {int(sensitivity_exclusion_mask.sum()):,}")
print(f"Records retained in sensitivity scenario: {len(sensitivity_df):,}")
print(
    "Rent threshold: monthly_rent_egp >= "
    f"{SUSPICIOUS_RENT_THRESHOLD:,} EGP"
)
print(f"Size threshold: size_sqm >= {SUSPICIOUS_SIZE_THRESHOLD:,} sqm")
print("Rule: exclude a record if either threshold is met.")
print(
    "Note: sensitivity exclusions are for comparison only; "
    "the primary summary and source data remain unchanged."
)

print("\n" + "=" * 75)
print("DISTRICT ANALYSIS COMPLETED")
print("=" * 75)
print(f"\nFull district summary: {summary_path}")
print(f"Affordable by rent: {affordable_rent_path}")
print(f"Affordable by price per sqm: {affordable_sqm_path}")
print(f"Sensitivity summary: {sensitivity_summary_path}")
print(f"Ranking comparison: {rank_comparison_path}")
print(f"All analysis outputs saved to: {OUTPUT_DIR}")
