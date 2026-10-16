from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# SAKAN - ROOM COUNT RENTAL ANALYSIS
# ============================================================

ROOT = Path(__file__).resolve().parent

DATA_PATH = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
OUTPUT_DIR = ROOT / "outputs" / "analysis"
CHART_DIR = ROOT / "outputs" / "charts"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)

SUMMARY_PATH = OUTPUT_DIR / "room_rental_summary.csv"
CHART_PATH = CHART_DIR / "08_median_rent_by_room_count.png"

print("=" * 70)
print("SAKAN - ROOM COUNT RENTAL ANALYSIS")
print("=" * 70)

# 1. Load data
if not DATA_PATH.exists():
    raise FileNotFoundError(
        f"Required dataset was not found: {DATA_PATH}"
    )

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
    raise ValueError(
        f"Required columns are missing: {missing_columns}"
    )

# 2. Convert required fields to numeric
for column in ["rooms", "monthly_rent_egp", "size_sqm"]:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# 3. Apply analytical validity checks
valid_mask = (
    df["rooms"].notna()
    & df["rooms"].gt(0)
    & (df["rooms"] % 1 == 0)
    & df["monthly_rent_egp"].notna()
    & df["monthly_rent_egp"].gt(0)
    & df["size_sqm"].notna()
    & df["size_sqm"].gt(0)
)

analysis_df = df.loc[valid_mask].copy()

if analysis_df.empty:
    raise ValueError(
        "No records remain after the analytical validity checks."
    )

# 4. Calculate price per square meter
analysis_df["price_per_sqm"] = (
    analysis_df["monthly_rent_egp"] / analysis_df["size_sqm"]
)

# 5. Summarize by room count
room_summary = (
    analysis_df.groupby("rooms")
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
    )
    .reset_index()
    .sort_values("rooms")
)

# Keep room count readable in the output
room_summary["rooms"] = room_summary["rooms"].astype(int)

# 6. Save results
room_summary.to_csv(
    SUMMARY_PATH,
    index=False,
    float_format="%.2f",
)

# 7. Display results
print(f"\nInput records: {len(df):,}")
print(f"Records included in room analysis: {len(analysis_df):,}")
print(f"Records excluded from this analysis: {len(df) - len(analysis_df):,}")

print("\n" + "=" * 70)
print("RENTAL SUMMARY BY ROOM COUNT")
print("=" * 70)

display_columns = [
    "rooms",
    "listing_count",
    "median_monthly_rent_egp",
    "mean_monthly_rent_egp",
    "median_size_sqm",
    "median_price_per_sqm",
]

print(
    room_summary[display_columns].to_string(
        index=False,
        formatters={
            "median_monthly_rent_egp": "{:,.2f}".format,
            "mean_monthly_rent_egp": "{:,.2f}".format,
            "median_size_sqm": "{:,.2f}".format,
            "median_price_per_sqm": "{:,.2f}".format,
        },
    )
)

# 8. Create a chart of median rent by room count
plot_df = room_summary.loc[
    room_summary["listing_count"] >= 5
].copy()

if plot_df.empty:
    plot_df = room_summary.copy()
    print(
        "\nWarning: No room-count category has at least five listings. "
        "The chart will show all available categories."
    )

fig, ax = plt.subplots(figsize=(11, 6))

bars = ax.bar(
    plot_df["rooms"].astype(str),
    plot_df["median_monthly_rent_egp"],
)

ax.set_title(
    "Median Monthly Rent by Number of Rooms",
    fontsize=15,
    fontweight="bold",
    pad=16,
)
ax.set_xlabel("Number of Rooms", fontsize=11)
ax.set_ylabel("Median Monthly Rent (EGP)", fontsize=11)

ax.grid(
    axis="y",
    linestyle="--",
    alpha=0.35,
)
ax.set_axisbelow(True)

for bar, value, count in zip(
    bars,
    plot_df["median_monthly_rent_egp"],
    plot_df["listing_count"],
):
    ax.annotate(
        f"{value:,.0f}\n(n={count})",
        xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
        xytext=(0, 4),
        textcoords="offset points",
        ha="center",
        va="bottom",
        fontsize=8,
    )

fig.tight_layout()
fig.savefig(
    CHART_PATH,
    dpi=200,
    bbox_inches="tight",
)
plt.close(fig)

# Update manifest with 08 if manifest exists
manifest_path = CHART_DIR / "visualization_manifest.csv"
if manifest_path.exists():
    try:
        m_df = pd.read_csv(manifest_path)
        if "08_median_rent_by_room_count.png" not in m_df["chart_file"].values:
            new_row = pd.DataFrame([{
                "chart_file": "08_median_rent_by_room_count.png",
                "description": "Compare median monthly rent across room-count categories; labels include listing counts."
            }])
            m_df = pd.concat([m_df, new_row], ignore_index=True)
            m_df.to_csv(manifest_path, index=False)
    except Exception:
        pass

print("\n" + "=" * 70)
print("ROOM ANALYSIS COMPLETED")
print("=" * 70)
print(f"\nSummary CSV: {SUMMARY_PATH}")
print(f"Chart PNG:   {CHART_PATH}")
print(
    "\nInterpretation note: These are descriptive associations, "
    "not proof that room count alone causes higher rent."
)
print(
    "Extreme positive rents have not been automatically removed. "
    "Review sensitivity results before drawing final conclusions."
)
