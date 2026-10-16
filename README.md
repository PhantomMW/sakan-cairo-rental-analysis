<div align="center">

# 🏙️ SAKAN
## Cairo Rental Market Analysis

### Data-Driven Insights for Real Estate Market Expansion — 2027

<p>
  <strong>Data Cleaning</strong> •
  <strong>Exploratory Data Analysis</strong> •
  <strong>Statistical Analysis</strong> •
  <strong>Geospatial Visualization</strong>
</p>

</div>

---

## 📌 Project Overview

**Sakan Cairo Rental Market Analysis** is an end-to-end data analytics project designed to transform raw, inconsistent rental-listing data into structured, actionable business insights.

The project investigates Cairo's rental market to support Sakan's planned expansion in early 2027. It focuses on identifying district-level rental patterns, comparing rental prices per square meter, exploring property characteristics, examining monthly price movements, and evaluating the impact of data-quality issues on analytical results.

The workflow covers the complete exploratory data analysis process, from raw data auditing and cleaning to statistical analysis, visualization, sensitivity testing, and business recommendations.

> **Core Objective:** Build a reliable analytical foundation that helps Sakan understand Cairo's rental-listing landscape and identify promising areas for further market investigation.

---

## 🎯 Business Objectives

The analysis addresses four primary business questions:

### 1. District-Level Rental Valuation
- Which districts have the highest and lowest median monthly rents?
- How does monthly rent per square meter vary across districts?
- Which areas warrant further investigation based on rental-price patterns?

### 2. Property Characteristics and Rental Prices
- How does property size relate to advertised monthly rent?
- How do rental prices differ across room counts?
- How does furnishing status relate to rental-price distributions?

### 3. Monthly Rental Trends
- How did median advertised rents change over the observed period?
- Which months recorded the highest and lowest median rents?
- How should monthly movements be interpreted in light of changing listing composition?

### 4. Data Quality and Reliability
- How many exact duplicate records were identified?
- Which missing, invalid, or suspicious values require investigation?
- How sensitive are rental-market summaries to extreme observations?

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python** | Core programming language |
| **Pandas** | Data manipulation, cleaning, grouping, and aggregation |
| **NumPy** | Numerical operations and Boolean filtering |
| **Matplotlib** | Statistical charts and data visualization |
| **Seaborn** | Distribution analysis and comparative visualizations |
| **Plotly** | Interactive visualization capabilities |
| **Folium** | Interactive geographic mapping |
| **Jupyter Notebook** | Optional exploratory development environment |
| **PowerShell** | Project execution and file management |

The project uses Python-based data analysis workflows and produces reusable CSV outputs, static charts, and an interactive HTML map.

---

## 📂 Project Structure

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
├── notebooks/
│
├── outputs/
│   │
│   ├── audit/
│   │   ├── initial_audit_summary.json
│   │   ├── cleaning_summary.json
│   │   ├── missing_values_report.csv
│   │   ├── cleaning_quality_flags.csv
│   │   ├── outlier_statistics.csv
│   │   ├── district_quality_review.csv
│   │   ├── data_integrity_summary.csv
│   │   ├── sensitivity_scenario_summary.csv
│   │   └── district_sensitivity_detailed_comparison.csv
│   │
│   ├── cleaned/
│   │   ├── cairo_rentals_cleaned.csv
│   │   ├── cairo_rentals_core_eligible.csv
│   │   └── district_info_cleaned.csv
│   │
│   ├── analysis/
│   │   ├── district_rental_summary.csv
│   │   ├── district_listing_counts.csv
│   │   ├── top_10_affordable_districts_by_rent.csv
│   │   ├── top_10_affordable_districts_by_sqm.csv
│   │   ├── monthly_rental_summary.csv
│   │   ├── monthly_rental_summary_sensitivity.csv
│   │   ├── room_rental_summary.csv
│   │   ├── room_sensitivity_detailed.csv
│   │   ├── room_sensitivity_comparison.csv
│   │   ├── district_monthly_timeseries.csv
│   │   ├── district_momentum_summary.csv
│   │   ├── district_momentum_sensitivity.csv
│   │   └── top_momentum_districts_reliable.csv
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
└── .venv/
```

*Note: The structure above documents the full project files and outputs.*

---

## 📊 Dataset Overview

The project uses two source datasets.

### 1. Cairo Rental Listings

**File:** `data/cairo_rentals.csv`

The rental dataset contains listing-level information, including:

- Listing identifier
- District
- Geographic coordinates
- Property size in square meters
- Number of rooms
- Furnishing status
- Monthly advertised rent in EGP
- Listing date

### 2. District Metadata

**File:** `data/district_info.csv`

The district metadata dataset contains contextual attributes such as:

- Population density
- Average income index
- Metro accessibility

These attributes can provide additional context for district comparisons when appropriately integrated and analyzed.

---

## 🧹 Data Cleaning and Quality Assurance

Raw web-scraped data can contain duplicates, missing fields, inconsistent categories, invalid values, and extreme observations.

The project implements a structured data-quality workflow.

### Cleaning Workflow

1. Inspect the raw datasets and their schemas.
2. Audit missing values and data types.
3. Identify and remove exact duplicate rows.
4. Standardize numeric fields and date values.
5. Normalize furnishing categories.
6. Review district names and metadata matching.
7. Identify records with invalid or missing analytical fields.
8. Create a core eligible dataset for rental analysis.
9. Calculate rental price per square meter.
10. Generate quality-control reports and sensitivity scenarios.

### Data Quality Findings

| Quality Check / Dataset Tier | Result | Eligibility & Notes |
|---|---:|---|
| Initial rental records | 2,000 | Raw scraped listings |
| Exact duplicate rows removed | 60 | Verified identical records |
| Records after exact deduplication | 1,940 | Cleaned baseline dataset |
| Core eligible analytical records | 1,851 | Named district, positive rent, positive size (across 26 districts) |
| Monthly & momentum analysis records | 1,832 | Core eligible with parseable dates (**19 records lack dates**) |
| Interactive geographic map records | 1,843 | Valid Greater Cairo coordinates & $500 < \text{rent} < 500,000$ EGP |
| Sensitivity scenario subset | 1,831 | Rents $< \text{EGP } 100,000$ and size $< 500\text{ m}^2$ |

The raw dataset also contained missing district values, missing coordinates, missing property sizes, and missing listing dates.

Dedicated audit files document missing values, invalid values, repeated listing identifiers, district matching, category standardization, and potential anomalies.

### Important Data Integrity Principles

1. **Statistical Outliers vs. Verified Errors:** Advertised rents reach up to **EGP 1,000,000** and property sizes reach up to **22,300 m²**. Our pipeline detects, audits, and flags these extreme observations, and measures their impact via IQR and sensitivity scenarios. However, labeling an observation as an outlier does **not** prove it is an error; luxury palaces or commercial compounds legitimately exist. They are preserved in the baseline data rather than deleted without source verification.
2. **Missing Dates Exclusion:** Exactly 19 records from the core eligible dataset had missing or unparseable dates post-cleaning, which is why the monthly time-series analyzes $1,851 - 19 = 1,832$ listings.
3. **Map Sample Reconciliation:** The interactive map renders 1,843 listings rather than 1,851 due to spatial requirements (valid coordinates within Greater Cairo bounding box $[29.4, 30.7]^\circ\text{N}, [30.5, 32.2]^\circ\text{E}$ and exclusion of scraper artifacts $\le 500$ or $\ge 500,000$ EGP).

---

## 📐 Feature Engineering

The project derives a rental-price metric that supports comparisons between properties of different sizes.

### Monthly Rent per Square Meter

\[
\text{Price per Square Meter}
=
\frac{\text{Monthly Rent (EGP)}}{\text{Property Size (m}^2\text{)}}
\]

This metric is calculated only when both monthly rent and property size are positive.

It helps compare rental prices across properties and districts while accounting for differences in property size.

However, price per square meter should be interpreted alongside property characteristics, district, and sample size rather than as a complete measure of property value.

---

## 📈 Exploratory Data Analysis

The project produces district-level summaries, monthly statistics, furnishing comparisons, and property-size analyses.

### District-Level Analysis

District summaries include:

- Listing count
- Mean monthly rent
- Median monthly rent
- Minimum and maximum rent
- Mean property size

Median rent is emphasized because extreme observations can substantially distort mean values.

### Property-Level Analysis

The analysis explores relationships between:

- Property size and monthly rent
- Room count and monthly rent
- Furnishing status and monthly rent
- Property size and rent per square meter

These comparisons are exploratory. Observed relationships do not establish causation.

### Monthly Trend Analysis

Monthly summaries include:

- Number of listings
- Median monthly rent
- Mean monthly rent

The analysis uses valid listing dates and positive rents. A separate sensitivity summary supports comparison under the project's selected filtering thresholds.

---

## 📊 Visualizations

Eight static charts provide complementary views of the rental market, accompanied by an interactive geographic map (nine visual assets in total).

| # | Visualization | Purpose |
|---|---|---|
| 01 | Median Rent by District | Compare typical advertised rents across districts |
| 02 | Median Price per Square Meter | Compare size-adjusted rental prices |
| 03 | Monthly Rent Distribution | Examine the distribution and spread of advertised rents |
| 04 | Property Size vs. Rent | Explore the relationship between size and monthly rent |
| 05 | Rent by Furnishing Status | Compare rent distributions across furnishing categories |
| 06 | Monthly Median Rent Trend | Examine changes in median rent over time |
| 08 | Median Rent by Room Count | Compare rents across room numbers (1–5 rooms) with listing volumes |
| 09 | District Monthly Rent Momentum | Track median monthly rent trajectories across strategic submarkets |

All static visualizations are stored in:

```text
outputs/charts/
```

The file `visualization_manifest.csv` provides an inventory of generated charts and their descriptions.

---

## 🗺️ Interactive Geographic Map

**Output:** `outputs/charts/07_interactive_cairo_rental_map.html`

The interactive map provides an executive geospatial view of **1,843 rental listings** across Cairo and nearby areas (reconciled from the 1,851 core eligible dataset by requiring valid Greater Cairo GPS coordinates and excluding scraper boundary artifacts).

Depending on the generated map version, features include:

- Geographic positioning of rental listings
- District-level exploration
- Listing markers and clustering
- Rental-price information in popups
- Property details
- Furnishing information
- Interactive map layers
- Geographic context for comparing locations

The HTML file can be opened in a modern web browser without running a Python server.

**Important:** The current Folium map uses external basemap tiles, so an internet connection is required to display the underlying map tiles correctly.

The map is a descriptive exploration tool. Geographic concentrations of listings should not automatically be interpreted as concentrations of tenant demand.

---

## 🔎 Outlier Detection and Sensitivity Analysis

Outlier analysis is essential because extreme values can distort rental-market summaries.

The project uses interquartile-range (IQR) flags and threshold-based sensitivity scenarios to investigate the impact of unusual observations.

### Overall Sensitivity Results

| Scenario | Listings | Median Rent (EGP) | Mean Rent (EGP) | Median Rent/m² (EGP) |
|---|---:|---:|---:|---:|
| Base valid-positive dataset | 1,851 | 22,000 | 28,875.20 | 155.91 |
| Exclude rent ≥ EGP 100,000 | 1,841 | 22,000 | 24,085.83 | 155.56 |
| Exclude size ≥ 500 m² | 1,841 | 22,000 | 28,922.05 | 156.25 |
| Exclude either rent ≥ EGP 100,000 or size ≥ 500 m² | 1,831 | 22,000 | 24,106.78 | 155.91 |
| Exclude suspicious rent codes | 1,842 | 22,000 | 24,130.30 | 155.58 |
| Exclude size ≥ 1,000 m² | 1,841 | 22,000 | 28,922.05 | 156.25 |

### Key Findings

- The overall median monthly rent remains EGP 22,000 across the tested scenarios.
- Excluding rents of EGP 100,000 or more reduces the mean rent by approximately 16.6%.
- The median rent per square meter remains close to EGP 156/m² across these scenarios.
- The results demonstrate that mean-based summaries are more sensitive to unusually high rental values.
- Sensitivity thresholds are analytical assumptions, not definitive rules for determining whether a listing is invalid.

Detailed results are available in:

```text
outputs/audit/
```

Relevant files include:

- `outlier_statistics.csv`
- `potential_outliers_for_review.csv`
- `extreme_rental_prices_for_review.csv`
- `extreme_property_sizes_for_review.csv`
- `sensitivity_scenario_summary.csv`
- `district_sensitivity_scenarios.csv`
- `district_sensitivity_detailed_comparison.csv`

---

## 💡 Key Findings

### 1. Median Rent Provides a More Stable Overall Baseline

The core eligible dataset has a median monthly rent of **EGP 22,000**.

This median remains unchanged across the tested overall sensitivity scenarios, even when extreme rental values are excluded.

### 2. Extreme Rental Values Affect the Mean

The mean monthly rent decreases from **EGP 28,875.20 to EGP 24,085.83** when records with rents of EGP 100,000 or more are excluded.

This reinforces the importance of reviewing distributions and using robust statistics when analyzing noisy rental data.

### 3. Districts Show Different Rental Price Levels

The district-level analysis identifies meaningful differences in median advertised rent.

Examples of districts with higher median rents in the core dataset include:

- Zamalek
- New Cairo
- Maadi
- Sheikh Zayed
- Mohandeseen

Examples of districts with lower median rents include:

- Badr City
- El Marg
- Helwan
- Shoubra
- Imbaba
- Faisal

These comparisons are descriptive and should be interpreted alongside listing counts and median rent per square meter.

### 4. Monthly Median Rent Fluctuates

The monthly median rent increases from EGP 20,000 in September 2025 to EGP 21,500 in August 2026.

This represents a **7.5% increase between the two endpoints**, but the monthly series fluctuates rather than increasing continuously.

### 5. Data Quality Directly Influences Business Interpretation

Duplicates, missing fields, inconsistent categories, and extreme values can change the results of downstream analysis.

The audit reports and sensitivity scenarios provide transparency into these issues and make the analytical process easier to review.

---

## 💼 Business Recommendations

### 1. Evaluate Districts Using Multiple Metrics

Use median monthly rent, median rent per square meter, listing volume, and data-quality indicators together.

A district with high total rent does not necessarily have the highest rent per square meter or the strongest business opportunity.

### 2. Investigate Premium Rental Segments

Districts with higher median rents can be prioritized for further research into premium listing supply, property characteristics, and potential customer segments.

High advertised rents alone do not prove stronger demand or higher profitability.

### 3. Evaluate Affordable Rental Segments Separately

Districts with lower median rents may represent a different market segment.

Before prioritizing these areas, investigate listing availability, transport accessibility, demand indicators, and commercial feasibility.

### 4. Improve Data Validation at the Source

Introduce validation rules for:

- Monthly rent
- Property size
- Geographic coordinates
- Listing dates
- District names
- Duplicate or repeated listings

Where possible, verify suspicious values against their original source before excluding them from analysis.

### 5. Develop a District-by-Month Monitoring Framework

Future analysis should calculate monthly median rents for individual districts, apply minimum sample-size requirements, and track changes in listing composition.

This would support a more reliable assessment of local rental trends.

### 6. Combine Market Analysis with Business Performance Data

Before making a final expansion decision, supplement listing data with demand, conversion, occupancy, acquisition-cost, and revenue indicators.

The current analysis supports market exploration but does not independently establish commercial profitability.

---

## ⚙️ Installation and Setup

### Prerequisites

- Python 3.10 or a compatible version supported by the installed dependencies
- PowerShell on Windows, or another compatible terminal
- Access to the project datasets
- Internet access for the interactive map's external basemap tiles

### 1. Clone or Download the Project

Place the project in a local directory.

Example:

```powershell
cd C:\Users\<username>\Desktop\sakan_rental_analysis
```

Replace `<username>` with your Windows username.

### 2. Create a Virtual Environment

```powershell
py -m venv .venv
```

### 3. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

Upgrade pip:

```powershell
python -m pip install --upgrade pip
```

Install the main libraries:

```powershell
python -m pip install pandas numpy matplotlib seaborn plotly folium
```

If a `requirements.txt` file is added to the project, use it to reproduce the intended environment:

```powershell
python -m pip install -r .\requirements.txt
```

---

## ▶️ Running the Analysis

Run commands from the project root so that relative file paths resolve correctly:
`C:\Users\<username>\Desktop\sakan_rental_analysis`

### Option 1: Unified Pipeline Runner (Recommended)

To reproduce the entire project from end to end with automated timing and verification, run:

```powershell
python .\run_pipeline.py
```

By default, this executes all 14 stages in fast in-process mode, completing in **under 15 seconds** (or ~8 seconds on modern systems) to prevent execution timeouts in resource-constrained environments.

Alternatively, you can run in full subprocess process-isolation mode:

```powershell
python .\run_pipeline.py --subprocess
```

Upon completion, the runner automatically audits that all 35 project deliverables exist on disk and are non-empty.

### Option 2: Step-by-Step Execution

You can also run individual scripts sequentially:

| Stage | Script | Purpose |
|---|---|---|
| 1 | `initial_data_audit.py` | Inspect the raw datasets |
| 2 | `inspect_raw_values.py` | Investigate raw field values |
| 3 | `clean_data.py` | Clean and standardize rental data |
| 4 | `review_cleaning.py` | Review cleaning results |
| 5 | `outlier_analysis.py` | Identify and review potential outliers |
| 6 | `district_analysis.py` | Generate district-level rental summaries |
| 7 | `district_quality_check.py` | Evaluate data quality and sensitivity scenarios |
| 8 | `monthly_data_check.py` | Inspect monthly data and date coverage |
| 9 | `room_analysis.py` | Analyze rent by room count and generate chart (08) |
| 10 | `room_sensitivity_analysis.py` | Evaluate room-count scenarios under sensitivity filters |
| 11 | `district_momentum_analysis.py` | Calculate district momentum, 2D sample reliability, and chart (09) |
| 12 | `create_visualizations.py` | Generate static charts (01–06) with explicit color styling |
| 13 | `interactive_map.py` | Generate the interactive geographic map (07) |
| 14 | `build_manifest.py` | Compile and validate master visualization manifest across all 9 assets |

Example execution:

```powershell
python .\initial_data_audit.py
python .\inspect_raw_values.py
python .\clean_data.py
python .\review_cleaning.py
python .\outlier_analysis.py
python .\district_analysis.py
python .\district_quality_check.py
python .\monthly_data_check.py
python .\room_analysis.py
python .\room_sensitivity_analysis.py
python .\district_momentum_analysis.py
python .\create_visualizations.py
python .\interactive_map.py
python .\build_manifest.py
```

**Execution note:** Some scripts depend on outputs generated by earlier scripts. When running step-by-step, maintain the sequence shown above.

---

## 📁 Output Reference

### Cleaned Data

```text
outputs/cleaned/
```

Contains cleaned rental records (`cairo_rentals_cleaned.csv`), the core eligible analytical dataset (`cairo_rentals_core_eligible.csv`), and cleaned district metadata (`district_info_cleaned.csv`).

### Audit Reports

```text
outputs/audit/
```

Contains data-quality summaries, missing-value reports, duplicate reviews, invalid-value reports, outlier flags, data integrity summaries, and sensitivity comparisons.

### Analysis Results

```text
outputs/analysis/
```

Contains district-level summaries, affordable-district tables, listing counts, monthly statistics, detailed room-count breakdowns, district-level monthly timeseries, 2D sample reliability classifications, and quarterly smoothed momentum sensitivity comparisons.

### Charts and Map

```text
outputs/charts/
```

Contains the 8 static visualizations (01–06, 08, 09), the interactive HTML map (07), and the master visualization manifest (`visualization_manifest.csv`).

### Documentation

```text
docs/
```

Contains the business questions (`analysis_questions.md`) and the comprehensive final analytical report (`final_report.md`).

---

## ⚠️ Limitations

The results should be interpreted in light of the following limitations:

- Advertised rents may differ from completed rental transaction prices.
- The dataset may not represent the entire Cairo rental market.
- Missing values reduce the sample available for some analyses.
- Districts have different listing counts, which affects the stability of their summaries.
- Some extreme observations may be legitimate properties rather than errors.
- Furnishing categories may depend on assumptions made during standardization.
- Monthly median changes may reflect shifts in listing composition as well as changes in asking prices.
- The observed period does not establish long-term market seasonality.
- The dataset does not directly measure tenant demand, occupancy, conversion rates, acquisition costs, or profitability.
- Observational relationships do not establish causation.

The analysis should therefore be used as a foundation for further investigation, not as a standalone investment decision model.

---

## 🚀 Future Improvements

Potential commercial and operational extensions include:

- Integration of actual transaction and signed lease agreement data.
- Tracking tenant lead volumes, viewing-to-lease conversion rates, and occupancy.
- Customer acquisition cost (CAC) and operational unit-economics modeling per district.
- Tracking listing freshness, duration on market, and relisted price revisions.
- In-person field validation of luxury anomalies and coordinate verification.
- Automated API pipelines for continuous rental market ingests.

---

## 📄 Project Documentation

The detailed report is available at:

```text
docs/final_report.md
```

The original business questions and project requirements are documented in:

```text
docs/analysis_questions.md
```

---

## ✅ Conclusion

Sakan Cairo Rental Market Analysis demonstrates a structured approach to cleaning and exploring noisy real-estate listing data.

By combining data-quality audits, district-level statistics, price-per-square-meter comparisons, monthly trend analysis, sensitivity testing, static visualizations, and an interactive geographic map, the project provides a practical analytical foundation for further market research.

The central lesson is that **reliable business insights depend on transparent data-quality decisions, robust statistical summaries, and careful interpretation of the available evidence**.

The next step is to combine these descriptive findings with real demand and business-performance indicators before making final expansion decisions.

---

<div align="center">

**SAKAN | Cairo Rental Market Analysis**

*Turning rental-listing data into clearer market insights.*

</div>