from pathlib import Path
import pandas as pd

# ============================================================
# SAKAN - ROOM COUNT SENSITIVITY ANALYSIS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_PATH = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
OUTPUT_DIR = ROOT / "outputs" / "analysis"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

DETAIL_OUTPUT = OUTPUT_DIR / "room_sensitivity_detailed.csv"
COMPARISON_OUTPUT = OUTPUT_DIR / "room_sensitivity_comparison.csv"

print("=" * 76)
print("SAKAN - ROOM COUNT SENSITIVITY ANALYSIS")
print("=" * 76)

# 1. Load data
if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

required_columns = [
    "listing_id",
    "rooms",
    "monthly_rent_egp",
    "size_sqm",
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(f"Missing required columns: {missing_columns}")

# 2. Convert numeric fields
for column in ["rooms", "monthly_rent_egp", "size_sqm"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 3. Apply the same core analytical eligibility checks
valid_mask = (
    df["rooms"].notna()
    & df["rooms"].gt(0)
    & (df["rooms"] % 1 == 0)
    & df["monthly_rent_egp"].notna()
    & df["monthly_rent_egp"].gt(0)
    & df["size_sqm"].notna()
    & df["size_sqm"].gt(0)
)

base = df.loc[valid_mask].copy()

if base.empty:
    raise ValueError("No valid records available for analysis.")

# 4. Define comparison scenarios
scenarios = {
    "Base - all eligible": base,

    "Exclude rent >= 100k": base.loc[
        base["monthly_rent_egp"] < 100_000
    ].copy(),

    "Exclude size >= 500 sqm": base.loc[
        base["size_sqm"] < 500
    ].copy(),

    "Exclude rent >= 100k or size >= 500 sqm": base.loc[
        (base["monthly_rent_egp"] < 100_000)
        & (base["size_sqm"] < 500)
    ].copy(),

    "Exclude suspicious rent codes": base.loc[
        ~base["monthly_rent_egp"].isin([999_999, 1_000_000])
    ].copy(),
}

# 5. Summarize each scenario by room count
all_results = []

for scenario_name, scenario_df in scenarios.items():

    if scenario_df.empty:
        print(f"\nWARNING: Scenario has no records: {scenario_name}")
        continue

    scenario_df = scenario_df.copy()

    scenario_df["price_per_sqm"] = (
        scenario_df["monthly_rent_egp"] / scenario_df["size_sqm"]
    )

    summary = (
        scenario_df.groupby("rooms")
        .agg(
            listing_count=("listing_id", "count"),
            median_monthly_rent_egp=("monthly_rent_egp", "median"),
            mean_monthly_rent_egp=("monthly_rent_egp", "mean"),
            median_size_sqm=("size_sqm", "median"),
            median_price_per_sqm=("price_per_sqm", "median"),
        )
        .reset_index()
    )

    summary["rooms"] = summary["rooms"].astype(int)
    summary["scenario"] = scenario_name
    summary["scenario_total_records"] = len(scenario_df)

    all_results.append(summary)

if not all_results:
    raise ValueError("No scenario results were generated.")

detailed = pd.concat(all_results, ignore_index=True)

column_order = [
    "scenario",
    "scenario_total_records",
    "rooms",
    "listing_count",
    "median_monthly_rent_egp",
    "mean_monthly_rent_egp",
    "median_size_sqm",
    "median_price_per_sqm",
]

detailed = detailed[column_order].sort_values(
    ["rooms", "scenario"]
)

# 6. Save detailed results
detailed.to_csv(
    DETAIL_OUTPUT,
    index=False,
    float_format="%.2f",
)

# 7. Create an easier comparison table
comparison = detailed.pivot(
    index="rooms",
    columns="scenario",
    values=[
        "listing_count",
        "median_monthly_rent_egp",
        "mean_monthly_rent_egp",
        "median_price_per_sqm",
    ],
)

comparison.columns = [
    f"{metric}__{scenario}"
    for metric, scenario in comparison.columns
]

comparison = comparison.reset_index()

comparison.to_csv(
    COMPARISON_OUTPUT,
    index=False,
    float_format="%.2f",
)

# 8. Print results
print(f"\nOriginal input records: {len(df):,}")
print(f"Core eligible records: {len(base):,}")

print("\nSCENARIO RECORD COUNTS")
print("-" * 76)

for scenario_name, scenario_df in scenarios.items():
    print(
        f"{scenario_name:<45} "
        f"{len(scenario_df):>6,} records"
    )

print("\nMEDIAN RENT BY ROOM COUNT AND SCENARIO")
print("-" * 76)

display_df = detailed.pivot(
    index="rooms",
    columns="scenario",
    values="median_monthly_rent_egp",
)

print(display_df.to_string(float_format=lambda x: f"{x:,.2f}"))

print("\nLISTING COUNTS BY ROOM COUNT AND SCENARIO")
print("-" * 76)

count_df = detailed.pivot(
    index="rooms",
    columns="scenario",
    values="listing_count",
)

print(count_df.to_string())

print("\n" + "=" * 76)
print("ROOM SENSITIVITY ANALYSIS COMPLETED")
print("=" * 76)

print(f"\nDetailed results: {DETAIL_OUTPUT}")
print(f"Comparison table: {COMPARISON_OUTPUT}")

print(
    "\nInterpretation: Sensitivity scenarios are analytical comparisons. "
    "They do not prove that excluded records are invalid."
)
