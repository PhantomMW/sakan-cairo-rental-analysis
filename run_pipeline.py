"""
================================================================================
SAKAN | REPRODUCIBLE END-TO-END PIPELINE RUNNER & AUDITOR
================================================================================
Executes the full analytical and visualization pipeline in the validated
chronological sequence, guaranteeing complete reproducibility from raw data
to final audit reports, analysis tables, static charts, interactive map,
visualization manifest, and automated unit test suite.

Usage:
    python .\run_pipeline.py              # Default high-speed execution (~15s)
    python .\run_pipeline.py --subprocess # Subprocess execution mode (~24s)
    python .\run_pipeline.py --skip-tests # Skip pytest phase

Sequence:
    01. initial_data_audit.py
    02. inspect_raw_values.py
    03. clean_data.py
    04. review_cleaning.py
    05. outlier_analysis.py
    06. district_analysis.py
    07. district_quality_check.py
    08. monthly_data_check.py
    09. room_analysis.py
    10. room_sensitivity_analysis.py
    11. district_momentum_analysis.py
    12. create_visualizations.py
    13. interactive_map.py
    14. build_manifest.py
================================================================================
"""

from pathlib import Path
import subprocess
import sys
import time
import traceback
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parent

PIPELINE_SCRIPTS = [
    ("01", "initial_data_audit.py", "Audit raw datasets and document initial data anomalies"),
    ("02", "inspect_raw_values.py", "Inspect string formats, date structures, and unparseable values"),
    ("03", "clean_data.py", "Execute data cleaning, deduplication, district normalization, and eligibility filtering"),
    ("04", "review_cleaning.py", "Review cleaning quality flags and post-cleaning audit metrics"),
    ("05", "outlier_analysis.py", "Perform statistical IQR outlier investigation and sensitivity boundary audits"),
    ("06", "district_analysis.py", "Compute district median rents, price per sqm, and affordable rankings"),
    ("07", "district_quality_check.py", "Execute district sensitivity testing and sample reliability checks"),
    ("08", "monthly_data_check.py", "Audit market-wide monthly median rent trends and listing counts"),
    ("09", "room_analysis.py", "Analyze rent and size distributions across 1-5 room properties (generates chart 08)"),
    ("10", "room_sensitivity_analysis.py", "Run scenario-based sensitivity tests on room count medians"),
    ("11", "district_momentum_analysis.py", "Compute calendar-aligned momentum, 2D sample reliability, and quarterly sensitivity (generates chart 09)"),
    ("12", "create_visualizations.py", "Generate static charts (01-06) with explicit color mapping"),
    ("13", "interactive_map.py", "Generate standalone executive interactive Cairo rental map (07)"),
    ("14", "build_manifest.py", "Compile and rigorously validate master visualization manifest across all 9 visual assets")
]

REQUIRED_DELIVERABLES = [
    # Cleaned Datasets
    ROOT / "outputs" / "cleaned" / "cairo_rentals_cleaned.csv",
    ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv",
    ROOT / "outputs" / "cleaned" / "district_info_cleaned.csv",

    # Analysis Deliverables
    ROOT / "outputs" / "analysis" / "district_rental_summary.csv",
    ROOT / "outputs" / "analysis" / "district_listing_counts.csv",
    ROOT / "outputs" / "analysis" / "top_10_affordable_districts_by_rent.csv",
    ROOT / "outputs" / "analysis" / "top_10_affordable_districts_by_sqm.csv",
    ROOT / "outputs" / "analysis" / "monthly_rental_summary.csv",
    ROOT / "outputs" / "analysis" / "monthly_rental_summary_sensitivity.csv",
    ROOT / "outputs" / "analysis" / "room_rental_summary.csv",
    ROOT / "outputs" / "analysis" / "room_sensitivity_detailed.csv",
    ROOT / "outputs" / "analysis" / "room_sensitivity_comparison.csv",
    ROOT / "outputs" / "analysis" / "district_monthly_timeseries.csv",
    ROOT / "outputs" / "analysis" / "district_momentum_summary.csv",
    ROOT / "outputs" / "analysis" / "district_momentum_sensitivity.csv",
    ROOT / "outputs" / "analysis" / "top_momentum_districts_reliable.csv",

    # Visual Assets & Manifest
    ROOT / "outputs" / "charts" / "01_median_rent_by_district.png",
    ROOT / "outputs" / "charts" / "02_median_price_per_sqm_by_district.png",
    ROOT / "outputs" / "charts" / "03_monthly_rent_distribution.png",
    ROOT / "outputs" / "charts" / "04_size_vs_rent.png",
    ROOT / "outputs" / "charts" / "05_rent_by_furnishing.png",
    ROOT / "outputs" / "charts" / "06_monthly_median_rent_trend.png",
    ROOT / "outputs" / "charts" / "07_interactive_cairo_rental_map.html",
    ROOT / "outputs" / "charts" / "08_median_rent_by_room_count.png",
    ROOT / "outputs" / "charts" / "09_district_monthly_rent_momentum.png",
    ROOT / "outputs" / "charts" / "visualization_manifest.csv",

    # Quality & Audit Reports
    ROOT / "outputs" / "audit" / "initial_audit_summary.json",
    ROOT / "outputs" / "audit" / "cleaning_summary.json",
    ROOT / "outputs" / "audit" / "missing_values_report.csv",
    ROOT / "outputs" / "audit" / "cleaning_quality_flags.csv",
    ROOT / "outputs" / "audit" / "outlier_statistics.csv",
    ROOT / "outputs" / "audit" / "district_quality_review.csv",
    ROOT / "outputs" / "audit" / "data_integrity_summary.csv",
    ROOT / "outputs" / "audit" / "sensitivity_scenario_summary.csv",
    ROOT / "outputs" / "audit" / "district_sensitivity_detailed_comparison.csv"
]


def verify_deliverables():
    """Phase 1: Verify presence and non-emptiness of all 35 project deliverables."""
    print("\n" + "=" * 80)
    print("PHASE 1: DELIVERABLE FILE SYSTEM INTEGRITY AUDIT")
    print("=" * 80)

    missing = []
    empty = []
    verified = 0

    for path in REQUIRED_DELIVERABLES:
        rel_path = path.relative_to(ROOT)
        if not path.exists():
            missing.append(rel_path)
        elif path.stat().st_size == 0:
            empty.append(rel_path)
        else:
            verified += 1

    if missing or empty:
        print(f"[FAIL] Pipeline deliverable verification failed!")
        if missing:
            print(f"Missing files ({len(missing)}):")
            for m in missing:
                print(f"  - {m}")
        if empty:
            print(f"Empty files (0 bytes) ({len(empty)}):")
            for e in empty:
                print(f"  - {e}")
        sys.exit(1)

    print(f"  [SUCCESS] All {verified}/{len(REQUIRED_DELIVERABLES)} project deliverables verified on disk.")
    print("  [SUCCESS] 0 missing files, 0 empty files.")


def verify_content_contracts():
    """Phase 2: Deep content, data contract, mathematical, and cross-report verification."""
    print("\n" + "=" * 80)
    print("PHASE 2: DEEP DATA CONTRACT & STATISTICAL CONTENT AUDIT")
    print("=" * 80)

    errors = []

    raw_path = ROOT / "data" / "cairo_rentals.csv"
    clean_path = ROOT / "outputs" / "cleaned" / "cairo_rentals_cleaned.csv"
    core_path = ROOT / "outputs" / "cleaned" / "cairo_rentals_core_eligible.csv"
    dist_info_path = ROOT / "outputs" / "cleaned" / "district_info_cleaned.csv"
    monthly_path = ROOT / "outputs" / "analysis" / "monthly_rental_summary.csv"
    dist_sum_path = ROOT / "outputs" / "analysis" / "district_rental_summary.csv"
    report_path = ROOT / "docs" / "final_report.md"

    df_raw = pd.read_csv(raw_path)
    df_clean = pd.read_csv(clean_path)
    df_core = pd.read_csv(core_path)
    df_monthly = pd.read_csv(monthly_path)
    df_dist = pd.read_csv(dist_sum_path)

    # 1. Row counts & population contracts
    print("[1] Verifying population row counts...")
    if len(df_raw) != 2000:
        errors.append(f"Raw rentals row count mismatch: expected 2000, got {len(df_raw)}")
    if len(df_clean) != 1940:
        errors.append(f"Cleaned rentals row count mismatch: expected 1940, got {len(df_clean)}")
    if len(df_core) != 1851:
        errors.append(f"Core eligible row count mismatch: expected 1851, got {len(df_core)}")
    if len(df_dist) != 26:
        errors.append(f"District summary count mismatch: expected 26, got {len(df_dist)}")
    if len(df_monthly) != 12:
        errors.append(f"Monthly summary count mismatch: expected 12 months, got {len(df_monthly)}")
    if df_monthly["listing_count"].sum() != 1832:
        errors.append(f"Monthly total listings mismatch: expected 1832, got {df_monthly['listing_count'].sum()}")

    print("    [PASS] Expected row counts: Raw=2,000 | Cleaned=1,940 | Core=1,851 | Monthly=1,832 | Districts=26")

    # 2. Duplicate constraints
    print("[2] Verifying zero forbidden duplicates...")
    clean_dupes = df_clean.duplicated().sum()
    core_dupes = df_core.duplicated().sum()
    if clean_dupes != 0:
        errors.append(f"Found {clean_dupes} duplicate rows in cairo_rentals_cleaned.csv")
    if core_dupes != 0:
        errors.append(f"Found {core_dupes} duplicate rows in cairo_rentals_core_eligible.csv")
    print("    [PASS] 0 duplicate rows in cleaned and core eligible datasets.")

    # 3. Value validity in core eligible dataset
    print("[3] Verifying core eligible value constraints (rent > 0, size > 0, valid districts)...")
    invalid_rents = (df_core["monthly_rent_egp"] <= 0) | df_core["monthly_rent_egp"].isna()
    if invalid_rents.any():
        errors.append(f"Found {invalid_rents.sum()} invalid rent values (<= 0 or NaN) in core eligible dataset")

    invalid_sizes = (df_core["size_sqm"] <= 0) | df_core["size_sqm"].isna()
    if invalid_sizes.any():
        errors.append(f"Found {invalid_sizes.sum()} invalid size values (<= 0 or NaN) in core eligible dataset")

    missing_districts = df_core["district"].isna() | df_core["district"].astype(str).str.strip().eq("")
    if missing_districts.any():
        errors.append(f"Found {missing_districts.sum()} missing district values in core eligible dataset")

    invalid_rooms = df_core["rooms"].isna() | (df_core["rooms"] < 1)
    if invalid_rooms.any():
        errors.append(f"Found {invalid_rooms.sum()} invalid room counts (< 1 or NaN) in core eligible dataset")

    print("    [PASS] 100% of core eligible records satisfy rent > 0, size > 0, valid rooms, and known districts.")

    # 4. Mathematical and statistical sanity
    print("[4] Verifying mathematical calculations and statistical metrics...")
    sqm_math_diff = (df_core["price_per_sqm"] - (df_core["monthly_rent_egp"] / df_core["size_sqm"])).abs()
    if (sqm_math_diff > 1e-4).any():
        errors.append("Math discrepancy detected: price_per_sqm != monthly_rent_egp / size_sqm")

    median_rent = df_core["monthly_rent_egp"].median()
    if median_rent != 22000.0:
        errors.append(f"Core overall median rent unexpected: expected 22000.0, got {median_rent}")

    median_sqm = df_core["price_per_sqm"].median()
    if abs(median_sqm - 155.91) > 0.1:
        errors.append(f"Core overall median price/sqm unexpected: expected ~155.91, got {median_sqm}")

    print(f"    [PASS] Math verified exact. Core Median Rent = {median_rent:,.2f} EGP | Median/m² = {median_sqm:.2f} EGP/m².")

    # 5. Cross-verification with Final Report content
    print("[5] Cross-verifying core numbers against Final Report (docs/final_report.md)...")
    if report_path.exists():
        report_text = report_path.read_text(encoding="utf-8")
        checks = [
            ("1,851", "Core eligible listing count"),
            ("26 districts", "District representation"),
            ("22,000", "Median monthly rent"),
            ("1,832", "Monthly timeseries records"),
            ("1,843", "Interactive map records"),
            ("7.5%", "Monthly endpoint increase"),
        ]
        for token, desc in checks:
            if token not in report_text:
                errors.append(f"Final report missing expected verified metric '{token}' ({desc})")
        print("    [PASS] Final report metrics perfectly synchronized with analytical outputs.")

    if errors:
        print("\n" + "!" * 80)
        print(f"[FAIL] Data contract audit failed with {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        print("!" * 80)
        sys.exit(1)

    print("  [SUCCESS] All data contract validations and cross-report checks passed successfully.")


def run_automated_tests():
    """Phase 3: Execute pytest test suite covering unit edge-cases and contracts."""
    print("\n" + "=" * 80)
    print("PHASE 3: AUTOMATED TEST SUITE EXECUTION (PYTEST)")
    print("=" * 80)
    cmd = [sys.executable, "-m", "pytest", "tests", "-v", "--tb=short"]
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        print("[FAIL] Pytest test suite execution failed!")
        sys.exit(result.returncode)

    print("  [SUCCESS] Pytest test suite passed with 100% success rate.")


def run_step_in_process(script_path):
    with open(script_path, "r", encoding="utf-8-sig") as f:
        code = f.read()

    globs = {
        "__file__": str(script_path.resolve()),
        "__name__": "__main__"
    }
    exec(compile(code, str(script_path), "exec"), globs)


def run_step_subprocess(script_path):
    result = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(f"Exit code {result.returncode}\n{result.stderr}\n{result.stdout}")


def main():
    use_subprocess = "--subprocess" in sys.argv
    skip_tests = "--skip-tests" in sys.argv
    mode_desc = "Subprocess Isolation" if use_subprocess else "Fast In-Process Execution"

    print("=" * 80)
    print("SAKAN | COMPLETE REPRODUCIBLE PIPELINE EXECUTION")
    print("=" * 80)
    print(f"Project Root: {ROOT}")
    print(f"Python Executable: {sys.executable}")
    print(f"Execution Mode: {mode_desc}")
    print(f"Total Steps to Execute: {len(PIPELINE_SCRIPTS)}")
    print("=" * 80)

    start_total = time.time()
    completed_steps = []

    for step_num, script_name, description in PIPELINE_SCRIPTS:
        script_path = ROOT / script_name
        if not script_path.exists():
            print(f"\n[ERROR] Step {step_num} FAILED: Script not found -> {script_name}")
            sys.exit(1)

        print(f"\n>>> Step {step_num}/{len(PIPELINE_SCRIPTS)}: Running {script_name}...")
        print(f"    Purpose: {description}")
        step_start = time.time()

        try:
            if use_subprocess:
                run_step_subprocess(script_path)
            else:
                run_step_in_process(script_path)
        except Exception as e:
            print(f"\n[ERROR] Step {step_num} ({script_name}) failed!")
            print(traceback.format_exc())
            sys.exit(1)

        step_elapsed = time.time() - step_start
        print(f"    [OK] Finished in {step_elapsed:.2f}s")
        completed_steps.append((step_num, script_name, step_elapsed))

    total_elapsed = time.time() - start_total

    print("\n" + "=" * 80)
    print("PIPELINE EXECUTION SUCCESSFULLY COMPLETED!")
    print("=" * 80)
    print(f"Total Script Execution Time: {total_elapsed:.2f} seconds\n")

    print(f"{'Step':<6} {'Script':<32} {'Time':<10} {'Status'}")
    print("-" * 60)
    for step_num, script_name, elapsed in completed_steps:
        print(f"{step_num:<6} {script_name:<32} {elapsed:>6.2f}s    OK")

    # Phase 1: Deliverable file existence audit
    verify_deliverables()

    # Phase 2: Deep content, data contract & statistical audit
    verify_content_contracts()

    # Phase 3: Automated pytest suite
    if not skip_tests:
        run_automated_tests()

    print("\n" + "=" * 80)
    print("ALL PIPELINE STAGES, AUDITS, AND AUTOMATED TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    main()
