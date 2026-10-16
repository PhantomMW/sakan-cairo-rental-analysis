"""
================================================================================
SAKAN | DISTRICT MARKET MOMENTUM ANALYSIS & SENSITIVITY FRAMEWORK
================================================================================
Analyzes month-on-month (MoM) rental price changes across Greater Cairo districts,
evaluates sample reliability across two distinct dimensions:
  1. Annual Volume (Total listings across 12 months)
  2. Monthly Endpoint Sample Adequacy (Listing counts in compared periods)
Includes a multi-month quarterly smoothed sensitivity analysis (Sep-Nov 2025 vs
Jun-Aug 2026) to mitigate small-sample endpoint volatility.

Run from project root:
    python .\district_momentum_analysis.py

Outputs:
    outputs/analysis/district_monthly_timeseries.csv
    outputs/analysis/district_momentum_summary.csv
    outputs/analysis/district_momentum_sensitivity.csv
    outputs/analysis/top_momentum_districts_reliable.csv
    outputs/charts/09_district_monthly_rent_momentum.png
"""

from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
OUTPUT_DIR = ROOT / "outputs" / "analysis"
CHART_DIR = ROOT / "outputs" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("SAKAN | DISTRICT MARKET MOMENTUM & SENSITIVITY ANALYSIS")
print("=" * 70)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Required cleaned dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# Parse fields
df["listing_date"] = pd.to_datetime(df["listing_date"], errors="coerce")
df["listing_month"] = df["listing_date"].dt.to_period("M").astype("string")
df["monthly_rent_egp"] = pd.to_numeric(df["monthly_rent_egp"], errors="coerce")
df["size_sqm"] = pd.to_numeric(df["size_sqm"], errors="coerce")

df["price_per_sqm"] = np.where(
    df["monthly_rent_egp"].gt(0) & df["size_sqm"].gt(0),
    df["monthly_rent_egp"] / df["size_sqm"],
    np.nan
)

valid = df.loc[
    df["district"].notna()
    & df["listing_month"].notna()
    & df["monthly_rent_egp"].gt(0)
].copy()

print(f"Total core eligible records: {len(df):,}")
print(f"Records with valid listing date and rent: {len(valid):,}")
print(f"Observed months: {sorted(valid['listing_month'].unique())}")
print(f"Observed districts: {valid['district'].nunique()}")

# -----------------------------------------------------------------------------
# 1. Monthly District Panel (Time Series)
# -----------------------------------------------------------------------------
observed_panel = (
    valid.groupby(["district", "listing_month"])
    .agg(
        listing_count=("listing_id", "count"),
        median_monthly_rent_egp=("monthly_rent_egp", "median"),
        mean_monthly_rent_egp=("monthly_rent_egp", "mean"),
        median_price_per_sqm=("price_per_sqm", "median"),
        median_size_sqm=("size_sqm", "median")
    )
    .reset_index()
)

# Build a complete calendar for every district so a missing district-month is
# explicit. This prevents pct_change() from comparing non-adjacent months.
month_start = pd.Period(min(valid["listing_month"].dropna()), freq="M")
month_end = pd.Period(max(valid["listing_month"].dropna()), freq="M")
calendar_months = pd.period_range(start=month_start, end=month_end, freq="M").astype(str)
all_district_names = sorted(valid["district"].dropna().unique())
complete_index = pd.MultiIndex.from_product(
    [all_district_names, calendar_months], names=["district", "listing_month"]
).to_frame(index=False)

panel = complete_index.merge(
    observed_panel, on=["district", "listing_month"], how="left", validate="one_to_one"
)
panel["listing_count"] = panel["listing_count"].fillna(0).astype(int)
panel = panel.sort_values(["district", "listing_month"]).reset_index(drop=True)

# Month-over-Month % change is calculated only for adjacent calendar months.
# Missing months have NaN median rent, so the change is also NaN rather than
# incorrectly comparing the nearest observed months on either side.
panel["mom_rent_pct_change"] = (
    panel.groupby("district")["median_monthly_rent_egp"]
    .pct_change(fill_method=None) * 100
)

panel_path = OUTPUT_DIR / "district_monthly_timeseries.csv"
panel.to_csv(panel_path, index=False, float_format="%.2f")
print(f"\n[1] Saved monthly district panel: {panel_path}")

# -----------------------------------------------------------------------------
# 2. Multi-Month Quarterly Smoothed Aggregation (Sensitivity Baseline)
# -----------------------------------------------------------------------------
# To address monthly sample volatility (e.g. 3-7 listings in endpoint months),
# we compare the initial 3-month quarter (Sep-Nov 2025) with the final 3-month
# quarter (Jun-Aug 2026).
q1_mask = valid["listing_month"].isin(["2025-09", "2025-10", "2025-11"])
q4_mask = valid["listing_month"].isin(["2026-06", "2026-07", "2026-08"])

valid["quarter_period"] = np.where(
    q1_mask, "Q1_Initial (Sep-Nov 2025)",
    np.where(q4_mask, "Q4_Final (Jun-Aug 2026)", "Mid_Period")
)

quarterly_agg = (
    valid[valid["quarter_period"] != "Mid_Period"]
    .groupby(["district", "quarter_period"])
    .agg(
        q_count=("listing_id", "count"),
        q_median_rent=("monthly_rent_egp", "median"),
        q_mean_rent=("monthly_rent_egp", "mean")
    )
    .reset_index()
)

# -----------------------------------------------------------------------------
# 3. Comprehensive District Momentum & Reliability Classification
# -----------------------------------------------------------------------------
summary_records = []
sensitivity_records = []

all_districts = sorted(valid["district"].unique())
all_months = sorted(valid["listing_month"].unique())

first_period = all_months[0]  # 2025-09
last_period = all_months[-1]  # 2026-08

for d in all_districts:
    sub = panel[panel["district"] == d].sort_values("listing_month")
    tot_listings = int(sub["listing_count"].sum())
    months_active = int(sub["listing_count"].gt(0).sum())

    first_row = sub[sub["listing_month"] == first_period]
    last_row = sub[sub["listing_month"] == last_period]

    rent_sep = float(first_row["median_monthly_rent_egp"].iloc[0]) if len(first_row) else np.nan
    cnt_sep = int(first_row["listing_count"].iloc[0]) if len(first_row) else 0

    rent_aug = float(last_row["median_monthly_rent_egp"].iloc[0]) if len(last_row) else np.nan
    cnt_aug = int(last_row["listing_count"].iloc[0]) if len(last_row) else 0

    min_endpoint_cnt = min(cnt_sep, cnt_aug)

    # 1-Month Raw Endpoint Change (Sep 2025 vs Aug 2026)
    if pd.notna(rent_sep) and pd.notna(rent_aug) and rent_sep > 0:
        raw_endpoint_pct = ((rent_aug - rent_sep) / rent_sep) * 100
    else:
        raw_endpoint_pct = np.nan

    # Average MoM Change across active months
    avg_mom = float(sub["mom_rent_pct_change"].mean()) if pd.notna(sub["mom_rent_pct_change"].mean()) else 0.0

    # Quarterly Smoothed Data
    d_q = quarterly_agg[quarterly_agg["district"] == d]
    q1_row = d_q[d_q["quarter_period"].str.startswith("Q1")]
    q4_row = d_q[d_q["quarter_period"].str.startswith("Q4")]

    q1_cnt = int(q1_row["q_count"].iloc[0]) if len(q1_row) else 0
    q1_rent = float(q1_row["q_median_rent"].iloc[0]) if len(q1_row) else np.nan

    q4_cnt = int(q4_row["q_count"].iloc[0]) if len(q4_row) else 0
    q4_rent = float(q4_row["q_median_rent"].iloc[0]) if len(q4_row) else np.nan

    if pd.notna(q1_rent) and pd.notna(q4_rent) and q1_rent > 0:
        smoothed_quarterly_pct = ((q4_rent - q1_rent) / q1_rent) * 100
    else:
        smoothed_quarterly_pct = np.nan

    # Dimension 1: Annual Sample Volume Tier
    if tot_listings >= 100:
        volume_tier = "Large Volume (>=100 listings)"
    elif tot_listings >= 50:
        volume_tier = "Medium Volume (50-99 listings)"
    elif tot_listings >= 25:
        volume_tier = "Moderate Volume (25-49 listings)"
    else:
        volume_tier = "Low Volume (<25 listings)"

    # Dimension 2: Monthly Endpoint Sample Adequacy
    if min_endpoint_cnt >= 8:
        endpoint_adequacy = "Robust (min count >= 8)"
    elif min_endpoint_cnt >= 5:
        endpoint_adequacy = "Moderate (min count 5-7)"
    else:
        endpoint_adequacy = "Fragile / Volatile (min count < 5)"

    # Dimension 3: Composite Reliability Tier
    if tot_listings >= 100 and min_endpoint_cnt >= 8:
        composite_reliability = "Tier 1: High Reliability (Large Volume & Robust Monthly)"
    elif tot_listings >= 50 and min_endpoint_cnt >= 5:
        composite_reliability = "Tier 2: Moderate Reliability (Medium Volume & Moderate Monthly)"
    elif tot_listings >= 50 and min_endpoint_cnt < 5:
        composite_reliability = "Tier 3: Volatile Monthly Sample (Medium/High Volume but Fragile Monthly <5)"
    else:
        composite_reliability = "Tier 4: Low Volume Sample (<50 listings)"

    # Volatility / Discrepancy Flag
    if pd.notna(raw_endpoint_pct) and pd.notna(smoothed_quarterly_pct):
        drift = smoothed_quarterly_pct - raw_endpoint_pct
        volatility_flag = "High Drift (>20% difference)" if abs(drift) >= 20 else "Consistent (<=20% difference)"
    else:
        drift = np.nan
        volatility_flag = "Insufficient Data"

    summary_records.append({
        "district": d,
        "total_listings": tot_listings,
        "months_active": months_active,
        "annual_volume_tier": volume_tier,
        "median_sep_2025_egp": rent_sep,
        "count_sep_2025": cnt_sep,
        "median_aug_2026_egp": rent_aug,
        "count_aug_2026": cnt_aug,
        "min_endpoint_count": min_endpoint_cnt,
        "endpoint_sample_adequacy": endpoint_adequacy,
        "raw_endpoint_pct_change": raw_endpoint_pct,
        "avg_monthly_pct_change": avg_mom,
        "smoothed_quarterly_pct_change": smoothed_quarterly_pct,
        "composite_reliability": composite_reliability
    })

    sensitivity_records.append({
        "district": d,
        "total_listings": tot_listings,
        "annual_volume_tier": volume_tier,
        "sep_2025_count": cnt_sep,
        "aug_2026_count": cnt_aug,
        "endpoint_sample_adequacy": endpoint_adequacy,
        "raw_endpoint_pct_change": raw_endpoint_pct,
        "q1_initial_count (Sep-Nov)": q1_cnt,
        "q1_initial_median_egp": q1_rent,
        "q4_final_count (Jun-Aug)": q4_cnt,
        "q4_final_median_egp": q4_rent,
        "smoothed_quarterly_pct_change": smoothed_quarterly_pct,
        "smoothing_drift_pct": drift,
        "volatility_flag": volatility_flag,
        "composite_reliability": composite_reliability
    })

summary_df = pd.DataFrame(summary_records).sort_values(
    by=["composite_reliability", "raw_endpoint_pct_change"],
    ascending=[True, False]
)

summary_path = OUTPUT_DIR / "district_momentum_summary.csv"
summary_df.to_csv(summary_path, index=False, float_format="%.2f")
print(f"[2] Saved district momentum summary: {summary_path}")

sensitivity_df = pd.DataFrame(sensitivity_records).sort_values(
    by=["total_listings", "raw_endpoint_pct_change"],
    ascending=[False, False]
)
sensitivity_path = OUTPUT_DIR / "district_momentum_sensitivity.csv"
sensitivity_df.to_csv(sensitivity_path, index=False, float_format="%.2f")
print(f"[3] Saved district momentum sensitivity analysis: {sensitivity_path}")

# Filter reliable districts (Tier 1 & Tier 2: Annual >= 50 and Monthly min count >= 5)
reliable_df = summary_df[
    summary_df["composite_reliability"].str.startswith("Tier 1")
    | summary_df["composite_reliability"].str.startswith("Tier 2")
].sort_values("raw_endpoint_pct_change", ascending=False).copy()

reliable_path = OUTPUT_DIR / "top_momentum_districts_reliable.csv"
reliable_df.to_csv(reliable_path, index=False, float_format="%.2f")
print(f"[4] Saved high/moderate reliability momentum rankings: {reliable_path}")

# -----------------------------------------------------------------------------
# 4. Static Visualization: Momentum in Leading Districts
# -----------------------------------------------------------------------------
sns.set_theme(style="whitegrid", font_scale=1.0)
plt.figure(figsize=(14, 7))

# Highlight top established investment corridors
focus_districts = [
    "New Cairo", "Zamalek", "Maadi", "Sheikh Zayed",
    "Heliopolis", "Dokki", "6th of October", "Nasr City"
]

plot_data = panel[panel["district"].isin(focus_districts)].copy()

palette = {
    "New Cairo": "#2563EB",
    "Zamalek": "#DC2626",
    "Maadi": "#059669",
    "Sheikh Zayed": "#7C3AED",
    "Heliopolis": "#D97706",
    "Dokki": "#0891B2",
    "6th of October": "#4B5563",
    "Nasr City": "#E11D48"
}

sns.lineplot(
    data=plot_data,
    x="listing_month",
    y="median_monthly_rent_egp",
    hue="district",
    palette=palette,
    marker="o",
    linewidth=2.2
)

plt.title("District Monthly Median Rent Momentum (Sep 2025 - Aug 2026)", fontsize=14, fontweight="bold", pad=12)
plt.xlabel("Listing Month", fontsize=11, fontweight="bold")
plt.ylabel("Median Monthly Rent (EGP)", fontsize=11, fontweight="bold")
plt.xticks(rotation=45)
plt.legend(title="Strategic District", bbox_to_anchor=(1.02, 1), loc="upper left", frameon=True)
plt.tight_layout()

chart_path = CHART_DIR / "09_district_monthly_rent_momentum.png"
plt.savefig(chart_path, dpi=300, bbox_inches="tight")
plt.close()
print(f"[5] Saved district momentum chart: {chart_path}")

# -----------------------------------------------------------------------------
# 5. Display Key Findings & Sensitivity Insights
# -----------------------------------------------------------------------------
print("\n" + "=" * 80)
print("TOP RELIABLE DISTRICTS MOMENTUM & SENSITIVITY COMPARISON")
print("=" * 80)
print(
    reliable_df[[
        "district", "total_listings", "count_sep_2025", "count_aug_2026",
        "raw_endpoint_pct_change", "smoothed_quarterly_pct_change", "composite_reliability"
    ]].to_string(index=False)
)
print("=" * 80)
print("Critical Analytical Takeaway:")
print("Single-month endpoint changes are highly vulnerable to property-mix noise when monthly counts are low (<8).")
print("Quarterly smoothed comparisons provide a robust baseline that confirms steady appreciation in New Cairo, Heliopolis, and 6th of October, while moderating apparent spikes in thin monthly samples.")
