<div align="center">

# SAKAN
### Cairo Rental Market Analysis

**An End-to-End Data Analytics Project**

Transforming Raw Rental Listings into Meaningful Market Insights

<br>

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=for-the-badge&logo=numpy&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=for-the-badge)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualization-4C72B0?style=for-the-badge)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![OpenStreetMap](https://img.shields.io/badge/OpenStreetMap-Geospatial_Intelligence-2E8B57?style=for-the-badge&logo=openstreetmap&logoColor=white)

</div>

---

## Table of Contents

- [Project Overview](#project-overview)
- [Key Results](#key-results)
- [Project Objectives](#project-objectives)
- [Technology Stack](#technology-stack)
- [Analytical Workflow](#analytical-workflow)
- [Dataset Overview](#dataset-overview)
- [Data Cleaning and Quality Assurance](#data-cleaning-and-quality-assurance)
- [Feature Engineering](#feature-engineering)
- [Exploratory Data Analysis](#exploratory-data-analysis)
- [Visualizations](#visualizations)
- [Interactive Geographic Map](#interactive-geographic-map)
- [Project Structure](#project-structure)
- [Installation and Setup](#installation-and-setup)
- [Running the Project](#running-the-project)
- [Automated Testing and Data Contract Auditing](#automated-testing-and-data-contract-auditing)
- [Project Deliverables](#project-deliverables)
- [Analytical Considerations](#analytical-considerations)
- [Conclusion](#conclusion)

---

## Project Overview

**SAKAN — Cairo Rental Market Analysis** is a Python-based data analytics project designed to transform raw rental-listing data into structured datasets, statistical summaries, visualizations, and geographic insights.

The project examines Cairo's rental market by analyzing advertised rental prices, district-level differences, property characteristics, monthly price movements, and data-quality issues.

The workflow follows an end-to-end analytical process, including data auditing, cleaning, feature engineering, exploratory data analysis, statistical evaluation, sensitivity analysis, and visualization.

The resulting analytical outputs provide a structured view of the observed rental-listing landscape and support comparisons across districts and property characteristics.

### Core Focus

- Rental-price analysis across Cairo's districts.
- Monthly rent and rent-per-square-meter comparisons.
- Property size, room count, and furnishing-status analysis.
- Monthly rental-price trend analysis.
- Data-quality assessment and outlier investigation.
- Statistical sensitivity analysis.
- Interactive geographic exploration of rental listings.

---

## Key Results

The completed analysis produced the following results:

| Metric | Result |
|---|---:|
| Initial rental records | 2,000 |
| Exact duplicate records removed | 60 |
| Records after exact deduplication | 1,940 |
| Core eligible analytical records | 1,851 |
| Districts represented in the core analysis | 26 |
| Median monthly advertised rent | EGP 22,000 |
| Median monthly rent per square meter | Approximately EGP 155.91/m² |
| Records included in monthly trend analysis | 1,832 |
| Listings included in the interactive geographic map | 1,843 |

### Monthly Rental Trend

The median advertised monthly rent increased from **EGP 20,000 in September 2025** to **EGP 21,500 in August 2026**.

This represents an increase of approximately **7.5%** between the two observed endpoints.

The trend describes changes in the analyzed listings. It should not be interpreted as a definitive measure of changes across the entire Cairo rental market because listing composition and sample size may vary over time.

### Data Quality

The project identifies duplicate records, missing values, invalid analytical fields, and unusual observations.

It also evaluates the sensitivity of selected analytical results to extreme rent and property-size values.

Rather than automatically removing every statistical outlier, the workflow distinguishes unusual observations from confirmed data errors.

---

## Project Objectives

The project addresses the following analytical questions.

### 1. District-Level Rental Analysis

- How does median monthly rent vary across districts?
- Which districts have comparatively high or low advertised rents?
- How does median rent per square meter differ between districts?
- How many eligible listings are available for each district?

### 2. Property Characteristics

- How does property size relate to monthly advertised rent?
- How do rental prices vary by room count?
- How do advertised rents differ by furnishing status?
- How useful is rent per square meter for comparing properties of different sizes?

### 3. Monthly Rental Trends

- How did median advertised rent change during the observed period?
- How do monthly listing counts vary?
- How do district-level rental-price movements differ?
- How sensitive are the observed trends to selected filtering criteria?

### 4. Data Quality and Reliability

- How many exact duplicate records are present?
- Which fields contain missing or invalid values?
- Which observations require additional scrutiny?
- How do extreme observations affect summary statistics?
- How do analytical results change under selected sensitivity scenarios?

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language and pipeline execution |
| Pandas | Data cleaning, transformation, grouping, and aggregation |
| NumPy | Numerical operations and data filtering |
| Matplotlib | Static charts and statistical visualization |
| Seaborn | Distribution analysis and comparative visualization |
| Plotly | Interactive visualization and geospatial mapping intelligence |
| HTML / CSS / JS | Standalone interactive executive dashboard output |
| CSV | Storage of datasets and analytical results |
| JSON | Structured audit summaries |
| PowerShell | Windows command-line execution and file management |
| Git and GitHub | Version control and project hosting |

---

## Analytical Workflow

The project implements a structured workflow that transforms raw records into analytical outputs.

### 1. Initial Data Audit

The initial audit examines the raw datasets to establish their structure and identify potential quality issues.

The audit includes:

- Dataset dimensions and column types.
- Missing-value counts.
- Duplicate-record detection.
- Numeric-field inspection.
- Date parsing and validity.
- District-name consistency.
- Potentially invalid or unusual observations.

The audit results are exported to structured reports for further inspection.

### 2. Data Cleaning

The cleaning stage prepares the rental listings for analysis.

Key operations include:

- Removing exact duplicate records.
- Standardizing numeric values and dates.
- Normalizing furnishing categories.
- Reviewing district names and metadata matching.
- Identifying records with missing or invalid analytical fields.
- Separating the cleaned baseline dataset from the core eligible analytical dataset.
- Producing cleaning summaries and quality-control reports.

### 3. Feature Engineering

The project derives rental price per square meter to support size-adjusted comparisons.

### 4. Exploratory Data Analysis

The project examines rental-price distributions and relationships between rent, district, property size, room count, furnishing status, and listing date.

### 5. Statistical and Sensitivity Analysis

The workflow examines extreme observations and compares selected analytical results under alternative filtering criteria.

### 6. Visualization and Reporting

The project generates static charts, structured CSV outputs, audit reports, a visualization manifest, and an interactive geographic map.

---

## Dataset Overview

The project uses two source datasets.

### 1. Cairo Rental Listings

**File:** `data/cairo_rentals.csv`

The rental-listings dataset contains information about advertised rental properties, including fields such as:

- Listing identifier.
- District.
- Geographic coordinates.
- Property size in square meters.
- Number of rooms.
- Furnishing status.
- Monthly advertised rent in Egyptian pounds.
- Listing date.

These fields support rental-price comparisons, property-level analysis, monthly trends, and geographic exploration.

### 2. District Metadata

**File:** `data/district_info.csv`

The district metadata dataset contains contextual district attributes, including fields such as:

- Population density.
- Average income index.
- Metro accessibility.

### 3. Data Provenance, Analytical Nature, and Terms of Use

- **Data Nature (Semi-Synthetic Benchmark Dataset):** The dataset is a **semi-synthetic / simulated research benchmark dataset** generated to model the market distribution and structural characteristics of residential rental listings across Greater Cairo. It replicates listing structures found on major Egyptian property portals (e.g., Property Finder, Aqarmap, OLX) while deliberately injecting real-world data quality challenges—including exact duplicate listings, unformatted currency text ("10,000", "27500 EGP"), inconsistent furnishing labels, missing values, and extreme outliers (such as EGP 1,000,000 asking rents and 22,300 m² sizes). These anomalies provide a realistic environment to demonstrate automated data cleaning, quality auditing, and non-parametric statistical methods.
- **Geographic Precision (Approximate & Centroid-Based):** Latitude and longitude coordinates are **approximate, centroid-anchored coordinates with simulated spatial dispersion (jitter)** around Greater Cairo district centers. They are tailored for interactive map clustering, layer toggling, and density heatmaps, and do not represent verified cadastral surveys or identifiable private addresses.
- **Observation Period:** A simulated 12-calendar-month period spanning September 2025 through August 2026.
- **Project Scope:** Educational portfolio project and analytical case study. It does not represent officially recorded lease registrations or certified market transaction data.
- **Asking Prices vs. Executed Leases:** All pricing fields reflect *advertised asking rents* rather than executed lease contracts. They do not reflect final negotiated discounts or tenant concessions.
- **Privacy & Compliance:** The dataset contains purely property-level attributes. No personally identifiable information (PII) is included or stored.

---

## Data Cleaning and Quality Assurance

Data quality is a central part of the analytical process.

Raw rental listings may contain duplicate records, missing values, inconsistent categories, invalid measurements, or unusually high prices.

The project documents these issues and separates general cleaning from the requirements of individual analytical tasks.

### Data Processing Results

| Processing Stage | Records | Description |
|---|---:|---|
| Raw rental dataset | 2,000 | Original rental records |
| Exact duplicates removed | 60 | Identical records identified during cleaning |
| Cleaned baseline dataset | 1,940 | Records remaining after exact deduplication |
| Core eligible dataset | 1,851 | Records with an eligible district, positive rent, and positive property size |
| Monthly trend analysis | 1,832 | Core eligible records with valid listing dates |
| Interactive geographic map | 1,843 | Records meeting geographic and map-specific price criteria |
| Sensitivity analysis subset | 1,831 | Records meeting the selected rent and property-size thresholds |

### Quality Assurance Principles

**Duplicate handling**

Exact duplicate records are removed before the primary analytical stages.

**Missing and invalid values**

Missing values and invalid analytical fields are documented. Records are included in individual analyses according to the requirements of those analyses.

**Outlier investigation**

Extreme rent and property-size values are examined through statistical summaries and sensitivity analysis. Statistical unusualness alone does not establish that a record is incorrect.

**Sample-size transparency**

Different analyses use different record counts because their requirements differ. For example, monthly trend analysis requires valid listing dates, while geographic mapping requires valid coordinates and compliance with the map's filtering criteria.

**Reproducibility**

Audit reports, cleaned datasets, analytical summaries, and visualization outputs provide a traceable record of the workflow's results.

---

## Feature Engineering

### Monthly Rent per Square Meter

The project calculates rent per square meter as a size-adjusted rental-price metric.

The formula is:

**Rent per Square Meter (EGP/m²) = Monthly Rent (EGP) ÷ Property Size (m²)**

Where:

- **Monthly Rent (EGP)** is the advertised monthly rental price.
- **Property Size (m²)** is the property's reported area in square meters.

The calculation is performed when both rent and property size are positive.

### Why This Metric Matters

Monthly rent alone does not account for differences in property size.

Rent per square meter helps compare properties of different sizes and provides an additional perspective for district-level analysis.

However, this metric should be interpreted alongside location, property characteristics, listing volume, and the distribution of observed prices.

---

## Exploratory Data Analysis

The project analyzes rental listings across multiple dimensions.

### District-Level Analysis

District summaries examine:

- Number of eligible listings.
- Median monthly rent.
- Mean monthly rent.
- Minimum and maximum advertised rent.
- Average property size.
- Median rent per square meter.

Median values are emphasized when comparing typical advertised rental prices because extreme observations can substantially affect the mean.

### Property Size and Rental Price

The analysis explores the relationship between property size and advertised monthly rent.

This comparison helps examine how rental prices vary across properties with different reported areas.

### Room Count and Rental Price

Rental-price distributions are compared across room-count categories.

The analysis helps identify differences in advertised rent between properties with different numbers of rooms.

### Furnishing Status and Rental Price

The project compares advertised rental prices across furnishing categories.

These comparisons are descriptive and do not independently establish that furnishing status causes a particular price difference.

### Monthly Rental Trends

The monthly analysis examines:

- Number of listings per month.
- Median monthly advertised rent.
- Mean monthly advertised rent.
- Changes in rental-price distributions over time.
- District-level monthly rental-price movements.

Monthly results are interpreted in the context of the available observations and their coverage.

### District Rental Momentum

The project also examines monthly rental-price movements across districts.

These summaries provide a comparative view of observed changes in district-level median rent, subject to the available sample and the analytical filtering criteria.

---

## Visualizations

The project generates **eight static charts and one interactive geographic map**.

| No. | Visualization | Purpose |
|---|---|---|
| 01 | Median Rent by District | Compare typical monthly advertised rents across districts |
| 02 | Median Rent per Square Meter by District | Compare size-adjusted rental prices |
| 03 | Monthly Rent Distribution | Examine the distribution and spread of advertised rents |
| 04 | Property Size vs. Rent | Explore the relationship between property size and monthly rent |
| 05 | Rent by Furnishing Status | Compare rental-price distributions across furnishing categories |
| 06 | Monthly Median Rent Trend | Examine monthly changes in median advertised rent |
| 07 | Interactive Cairo Rental Map | Explore rental listings geographically |
| 08 | Median Rent by Room Count | Compare rental prices across room-count categories |
| 09 | District Monthly Rent Momentum | Compare observed monthly rental-price movements across districts |

The generated visual assets are stored in:

```text
outputs/charts/
```

The directory includes the static charts, interactive map, and visualization manifest.

---

## Interactive Geographic Map

**Output file:**

`outputs/charts/07_interactive_cairo_rental_map.html`

The interactive map contains **1,843 rental listings** that satisfy the map's geographic and price-filtering criteria.

It complements the statistical analysis by presenting rental listings in their geographic context.

### Opening the Map

1. Navigate to the `outputs/charts/` directory.
2. Open `07_interactive_cairo_rental_map.html` in a modern web browser.
3. Explore the geographic distribution and available listing information.

The map uses external basemap tiles. An internet connection is therefore required to display the underlying map tiles correctly.

---

## Project Structure

```text
sakan_rental_analysis/
│
├── data/
│   ├── cairo_rentals.csv
│   └── district_info.csv
│
├── docs/
│   ├── analysis_questions.md
│   └── final_report.md
│
├── outputs/
│   ├── audit/
│   │   ├── initial_audit_summary.json
│   │   ├── cleaning_summary.json
│   │   ├── missing_values_report.csv
│   │   ├── cleaning_quality_flags.csv
│   │   ├── outlier_statistics.csv
│   │   ├── district_quality_review.csv
│   │   ├── data_integrity_summary.csv
│   │   └── sensitivity reports
│   │
│   ├── cleaned/
│   │   ├── cairo_rentals_cleaned.csv
│   │   ├── cairo_rentals_core_eligible.csv
│   │   └── district_info_cleaned.csv
│   │
│   ├── analysis/
│   │   ├── district_rental_summary.csv
│   │   ├── district_listing_counts.csv
│   │   ├── monthly_rental_summary.csv
│   │   ├── room_rental_summary.csv
│   │   └── district-level analysis outputs
│   │
│   └── charts/
│       ├── 01_median_rent_by_district.png
│       ├── 02_median_price_per_sqm_by_district.png
│       ├── 03_monthly_rent_distribution.png
│       ├── 04_size_vs_rent.png
│       ├── 05_rent_by_furnishing.png
│       ├── 06_monthly_median_rent_trend.png
│       ├── 07_interactive_cairo_rental_map.html
│       ├── 08_median_rent_by_room_count.png
│       ├── 09_district_monthly_rent_momentum.png
│       └── visualization_manifest.csv
│
├── run_pipeline.py
├── initial_data_audit.py
├── inspect_raw_values.py
├── clean_data.py
├── review_cleaning.py
├── outlier_analysis.py
├── district_analysis.py
├── district_quality_check.py
├── monthly_data_check.py
├── room_analysis.py
├── room_sensitivity_analysis.py
├── district_momentum_analysis.py
├── create_visualizations.py
├── interactive_map.py
├── build_manifest.py
│
├── README.md
└── .gitignore
```

### Directory Guide

| Directory | Contents |
|---|---|
| `data/` | Source datasets |
| `docs/` | Analysis questions and final report |
| `outputs/audit/` | Data-quality reports and sensitivity summaries |
| `outputs/cleaned/` | Cleaned datasets and the core eligible dataset |
| `outputs/analysis/` | District, monthly, room-count, and related analytical summaries |
| `outputs/charts/` | Static charts, interactive map, and visualization manifest |

---

## Installation and Setup

### Prerequisites

- Python 3.10 or newer.
- Git.
- A terminal such as Windows PowerShell.

### 1. Clone the Repository

```bash
git clone https://github.com/PhantomMW/sakan-cairo-rental-analysis.git
cd sakan-cairo-rental-analysis
```

### 2. Create a Virtual Environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

A virtual environment keeps the project's Python dependencies separate from other Python installations.

### 3. Install Dependencies

Install the pinned, production-tested dependencies from `requirements.txt`:

```powershell
python -m pip install -r requirements.txt
```

### 4. Verify the Project Files

From the project root, verify that `run_pipeline.py` and the required source datasets are present in `data/`.

---

## Running the Project

Execute the unified analysis pipeline from the project root:

```powershell
# Default high-speed execution mode (runs all 14 stages in ~7.5 seconds):
python .\run_pipeline.py

# Subprocess execution mode (runs in fresh Python processes in ~19 seconds):
python .\run_pipeline.py --subprocess
```

The pipeline executes all 14 analytical and visualization stages in strict dependency order, logs runtime benchmarks, and automatically audits all 35 deliverables across `outputs/` to ensure full data consistency and synchronization.

### Reviewing the Results

After execution, inspect the following directories:

**Data quality reports**

```text
outputs/audit/
```

**Cleaned datasets**

```text
outputs/cleaned/
```

**Analytical summaries**

```text
outputs/analysis/
```

**Charts and interactive map**

```text
outputs/charts/
```

**Final analytical report**

```text
docs/final_report.md
```

The generated files provide access to the cleaned data, analysis results, quality checks, and visualizations.

---

## Automated Testing and Data Contract Auditing

The repository includes a comprehensive automated test suite powered by `pytest`, validating 16 distinct unit edge-cases, pipeline contracts, and mathematical invariants.

### Running the Test Suite Directly

```powershell
pytest -v
```

### Test Suite Coverage:

1. **Empty Dataset Handling:** Validates that empty source files produce structured empty schemas without crashing.
2. **Missing Essential Columns:** Asserts that input tables missing required schema keys (`monthly_rent_egp`, `size_sqm`, `district`) fail fast with informative `ValueError` exceptions.
3. **Zero and Negative Numerical Values:** Enforces that non-positive rents ($\le 0$) and sizes ($\le 0$) are audited into `quality_flags` and strictly excluded from the core analytical population.
4. **Extreme Outlier Codes (999,999 & 1,000,000 EGP):** Ensures high-leverage outliers are audited, retained in core analysis for non-parametric evaluation, and excluded in sensitivity scenarios.
5. **Invalid and Empty Timestamps:** Asserts that corrupt date formats and missing dates coerce safely to `NaT` and are excluded from monthly timeseries aggregation.
6. **Out-of-Bounds Coordinates:** Validates that coordinates outside the Greater Cairo geospatial bounding box ($[29.4, 30.7]^\circ\text{N}, [30.5, 32.2]^\circ\text{E}$) or invalid GPS values are flagged and omitted from the interactive map.
7. **Duplicate Row Deduplication:** Asserts exact duplicate detection removes repeated rows down to single instances.
8. **Unmapped Districts in Metadata:** Validates left-merge joins so novel districts not present in `district_info.csv` remain intact and get logged in `outputs/audit/unmatched_districts.csv`.
9. **Furnishing Category Normalization:** Verifies conversion of messy text variations ('semi', 'yes', 'f', 'not furnished') and auditing unmapped values.
10. **Single-Record Dataset ($N=1$):** Ensures mathematical feature engineering (`price_per_sqm`) and aggregations execute without indexing or zero-division errors.
11. **Production Deliverables & Contracts:** Validates exact expected row counts (Raw=2,000, Cleaned=1,940, Core=1,851, Monthly=1,832, Map=1,843, Districts=26), zero duplicates in output tables, and exact mathematical equality between `price_per_sqm` and `monthly_rent_egp / size_sqm`.

---

## Project Deliverables

The completed project includes:

- A structured data-cleaning workflow.
- Initial data-audit reports.
- Cleaned rental-listings datasets.
- A core eligible analytical dataset.
- Missing-value and data-integrity reports.
- Outlier statistics and sensitivity-analysis outputs.
- District-level rental summaries.
- Rent-per-square-meter comparisons.
- Monthly rental-price summaries.
- Room-count and furnishing-status comparisons.
- District-level rental momentum analysis.
- Eight static visualizations.
- An interactive geographic map.
- A visualization manifest.
- A final analytical report.

---

## Analytical Considerations

The results should be interpreted in light of the dataset's coverage and limitations.

### Advertised Prices

The analysis examines advertised rental prices rather than independently verified transaction prices.

### Dataset Coverage

The findings describe the available rental listings. They should not automatically be generalized to every rental property or transaction in Cairo.

### Extreme Observations

Extreme prices and property sizes can affect summary statistics. The project investigates their impact through quality checks and sensitivity analysis.

### Changing Listing Composition

Changes in monthly median rent may reflect changes in the mix of properties listed, as well as changes in advertised prices.

### Descriptive Analysis

Relationships between rent and property characteristics are exploratory. They do not independently establish causation.

### Geographic Coverage

The interactive map includes records that meet its geographic and price-filtering criteria. Its record count therefore differs from the core eligible analytical dataset.

---

## Conclusion

**SAKAN — Cairo Rental Market Analysis** demonstrates an end-to-end approach to rental-market analytics using Python.

The project combines data cleaning, feature engineering, exploratory analysis, statistical evaluation, sensitivity analysis, and visualization to transform raw rental listings into structured analytical outputs.

Its district-level comparisons, property-level analysis, monthly rental trends, and interactive geographic map provide complementary perspectives on the observed rental market.

By documenting data-quality decisions and maintaining clear distinctions between analytical samples, the project emphasizes transparency, reproducibility, and responsible interpretation of results.

---

<div align="center">

### SAKAN
**Cairo Rental Market Analysis**

*Turning Rental Data into Meaningful Insights.*

</div>