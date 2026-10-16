"""
================================================================================
SAKAN | REPRODUCIBLE END-TO-END PIPELINE RUNNER & DELIVERABLE AUDITOR
================================================================================
Executes the full analytical and visualization pipeline in the validated
chronological sequence, guaranteeing complete reproducibility from raw data
to final audit reports, analysis tables, static charts, interactive map,
and verified visualization manifest.

Usage:
    python .\run_pipeline.py              # High-speed in-process execution (~15s)
    python .\run_pipeline.py --subprocess # Subprocess execution mode (~24s)

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
"""

from pathlib import Path
import subprocess
import sys
import time
import traceback

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
    print("\n" + "=" * 80)
    print("DELIVERABLE INTEGRITY AUDIT")
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
    print("=" * 80)


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
    print(f"Total Execution Time: {total_elapsed:.2f} seconds\n")

    print(f"{'Step':<6} {'Script':<32} {'Time':<10} {'Status'}")
    print("-" * 60)
    for step_num, script_name, elapsed in completed_steps:
        print(f"{step_num:<6} {script_name:<32} {elapsed:>6.2f}s    OK")

    # Actively verify every required file on disk
    verify_deliverables()


if __name__ == "__main__":
    main()
