"""
================================================================================
SAKAN | VISUALIZATION MANIFEST BUILDER & VALIDATOR
================================================================================
Scans outputs/charts/ to verify that all 8 static visualizations and the
interactive HTML map exist and are non-empty, then compiles the definitive
visualization manifest (visualization_manifest.csv).

Run from project root:
    python .\build_manifest.py
"""

from pathlib import Path
import pandas as pd
import sys

ROOT = Path(__file__).resolve().parent
CHART_DIR = ROOT / "outputs" / "charts"

EXPECTED_VISUALIZATIONS = {
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


def build_manifest():
    print("=" * 70)
    print("SAKAN | COMPILING & VALIDATING VISUALIZATION MANIFEST")
    print("=" * 70)

    CHART_DIR.mkdir(parents=True, exist_ok=True)
    missing_files = []
    manifest_rows = []

    for filename, description in EXPECTED_VISUALIZATIONS.items():
        file_path = CHART_DIR / filename
        if not file_path.exists():
            missing_files.append((filename, "Missing from disk"))
            continue

        file_size = file_path.stat().st_size
        if file_size == 0:
            missing_files.append((filename, "File exists but is 0 bytes"))
            continue

        size_kb = round(file_size / 1024, 1)
        manifest_rows.append({
            "chart_file": filename,
            "description": description
        })
        print(f"  [OK] {filename:<40} ({size_kb:>7.1f} KB)")

    if missing_files:
        print("\n[ERROR] Visualization Manifest Validation FAILED:")
        for name, reason in missing_files:
            print(f"  - {name}: {reason}")
        print("\nEnsure all chart generation scripts have run before building the manifest.")
        sys.exit(1)

    manifest_df = pd.DataFrame(manifest_rows)
    manifest_path = CHART_DIR / "visualization_manifest.csv"
    manifest_df.to_csv(manifest_path, index=False)

    print("\n" + "=" * 70)
    print(f"SUCCESS: Visualization manifest compiled with all {len(manifest_rows)} assets.")
    print(f"Output: {manifest_path}")
    print("=" * 70)


if __name__ == "__main__":
    build_manifest()
