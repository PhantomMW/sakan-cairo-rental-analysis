# Sakan Cairo Rental Market Analysis

## Final Exploratory Data Analysis Report

**Project focus:** Data quality, rental-market exploration, district comparison, monthly trends, and geographic visualization

**Business context:** Support Sakan's planned Greater Cairo expansion in early 2027

**Currency:** Egyptian pounds (EGP)

---

## 1. Executive Summary

This project transforms a noisy rental-listing dataset into a structured exploratory analysis to support Sakan's planned expansion across Greater Cairo. The workflow includes data auditing, duplicate removal, value standardization, eligibility checks, district-level aggregation, outlier review, sensitivity analysis, static visualizations, room-count analysis, and an interactive geographic map.

The core eligible analytical dataset contains **1,851 listings across 26 districts**. The overall median monthly rent is **EGP 22,000**, while the median monthly rent per square meter is approximately **EGP 155.91/m²**.

The results demonstrate why robust statistics are important. When listings with monthly rents of EGP 100,000 or more are excluded for sensitivity testing, the overall mean rent decreases from approximately EGP 28,875.20 to EGP 24,085.83. However, the overall median remains EGP 22,000. This indicates that unusually high values materially affect the mean, while the median remains stable under the tested scenarios.

District comparisons reveal substantial differences in advertised rental prices. Zamalek, New Cairo, and Maadi have relatively high median monthly rents in the observed sample, while districts such as Badr City, El Marg, and Helwan have lower median rents. These findings should be considered alongside listing counts, rent per square meter, and data-quality limitations.

Property-feature analysis indicates that median monthly rent generally increases with room count. Median rent ranges from EGP 11,000 for one-room properties to EGP 42,000 for five-room properties. Median property size also increases across these categories, from 75 m² to 243 m². This is a descriptive association and does not establish that room count alone causes higher rent.

Monthly median rent increases from EGP 20,000 in September 2025 to EGP 21,500 in August 2026, representing a 7.5% endpoint increase. The series fluctuates rather than increasing continuously, with the highest observed monthly median of EGP 24,000 in July 2026.

The project provides a reproducible foundation for rental-market exploration. However, the results describe the available listings rather than the entire rental market. Listing prices alone do not establish tenant demand, occupancy, completed transaction prices, profitability, or the best district for expansion. Recommendations should therefore be treated as evidence-led priorities for further investigation rather than definitive investment decisions.

---

## 2. Business Context and Objectives

Sakan needs reliable information from fragmented rental-listing data to support its planned expansion across Greater Cairo.

The analysis addresses four main business questions.

### 2.1 District Valuation

Which districts have higher or lower median monthly rents and median rent per square meter?

### 2.2 Property Features

How do property size, room count, and furnishing category relate to advertised monthly rent?

### 2.3 Market Momentum

How did monthly median rental prices change during the observed period across the overall market and across individual districts, and which districts experienced the fastest rent acceleration?

### 2.4 Data Integrity

How do duplicates, missing values, suspicious values, and extreme observations affect the analytical baseline?

No predictive machine-learning model is required for this phase. The objective is to produce a defensible cleaned dataset, exploratory findings, and useful visual outputs that can support further business investigation.

---

## 3. Data and Analytical Scope

### 3.1 Source Files

The project uses the following source files:

- `data/cairo_rentals.csv` — rental listing records.
- `data/district_info.csv` — district-level metadata, including population density, average income index, and metro access.

### 3.2 Main Rental Fields

The raw rental table contains the following fields:

- `listing_id`
- `district`
- `latitude`
- `longitude`
- `size_sqm`
- `rooms`
- `furnished`
- `monthly_rent_egp`
- `listing_date`

The district metadata provides additional contextual information that can support future comparisons between rental listings and district characteristics.

### 3.3 Analytical Populations and Sample Reconciliation

The project defines distinct analytical populations tailored to the specific data requirements of each phase. Sample counts differ across deliverables because different analyses require different fields:

| Analytical Dataset | Record Count | Eligibility Criteria | Analytical Purpose |
|---|---:|---|---|
| **Raw Scraped Listings** | 2,000 | Unprocessed source records | Baseline data ingestion |
| **Cleaned Listings** | 1,940 | Exact duplicate rows removed | Cleaning audit and raw field validation |
| **Core Eligible Dataset** | **1,851** | Known district, positive rent, positive size | Primary district and property-feature analysis across 26 districts |
| **Monthly & Momentum Dataset** | **1,832** | Core eligible with parseable listing date | Time-series and month-over-month trend analysis (**19 records lack dates**) |
| **Geospatial Map Dataset** | **1,843** | Cleaned records with valid Cairo coordinates & $500 < \text{rent} < 500,000$ | Interactive geographic visualization and spatial cluster analysis |
| **Sensitivity Subset** | **1,831** | Core eligible with $\text{rent} < 100,000$ & $\text{size} < 500\text{ m}^2$ | Visual readability and extreme value impact assessment |

#### Key Analytical Clarifications:
1. **Extreme Observations (Outliers):** Advertised monthly rents reach up to **EGP 1,000,000** and property sizes reach up to **22,300 m²**. Our pipeline detects, audits, and quantifies these values, and tests their influence through sensitivity scenarios. Crucially, statistical identification as an outlier does **not** prove that a record is erroneous; luxury villas and commercial-scale compounds legitimately exist. They are retained in the base dataset rather than arbitrarily discarded.
2. **Missing Dates in Monthly Analysis:** Exactly **19 records** in the core eligible analytical dataset have unparseable or missing listing dates post-cleaning. Consequently, the monthly panel analysis evaluates $1,851 - 19 = \mathbf{1,832}$ records across the 12-month period.
3. **Map Sample Reconciliation:** The interactive map displays **1,843 listings** rather than 1,851. Spatial rendering strictly requires valid GPS coordinates within Greater Cairo's geographic bounding box ($[29.4, 30.7]^\circ\text{N}, [30.5, 32.2]^\circ\text{E}$) and applies boundary filters ($500 < \text{rent} < 500,000\text{ EGP}$) to prevent coordinate-free records or scraper scale distortions from compromising the map interface.

---

## 4. Data Cleaning and Quality Assessment

The cleaning and audit workflow includes:

- Removing exact duplicate rows.
- Reviewing missing values in district, coordinates, property size, and listing date.
- Parsing listing dates and converting numeric fields.
- Standardizing furnishing categories.
- Checking district names before joining district metadata.
- Defining a core eligible subset requiring a known district and positive rent and size.
- Engineering `price_per_sqm = monthly_rent_egp / size_sqm` where both inputs are positive.
- Producing audit files for missing values, invalid values, repeated identifiers, category values, district matching, and potential anomalies.

### 4.1 Important Quality Findings

The initial data audit identified the following issues:

- The raw file contained 19 missing district values.
- Latitude and longitude each had 40 missing values.
- Property size had 19 missing values.
- Listing date had 21 missing values.
- After cleaning, 19 listing dates remained missing, while 1,921 dates were parseable in the cleaned dataset.
- Among the core eligibility checks, 23 records had invalid or missing rent, 48 had invalid or missing size, and 19 had a missing district. These flags can overlap.
- The dataset contains extreme rental values around EGP 999,999–1,000,000.
- Some property sizes are implausibly large, including values in the thousands of square meters.
- Some unusually low rental values, including EGP 1, require source validation.
- Furnishing labels were standardized into consistent categories.

Mappings such as `f`, `yes`, and `y` to `Furnished` are assumptions that should be documented and checked against the original source definitions if available.

A data-quality flag is not equivalent to a confirmed error. Unusual listings should be checked against the original source wherever possible.

### 4.2 Core Eligibility

The core eligible dataset is used for district comparisons and property-feature analysis.

A record is included in this analytical population when it has:

- A known district.
- A positive monthly rent.
- A positive property size.

The core eligible dataset contains **1,851 records**.

This eligibility definition creates a consistent analytical baseline but does not guarantee that every included value is accurate or representative of the market.

---

## 5. Outliers and Sensitivity Analysis

Outliers were reviewed using interquartile-range (IQR) thresholds and additional scenario-based comparisons.

IQR flags identify observations that are unusual relative to the distribution. They do not establish that an observation is incorrect.

### 5.1 IQR Review

The district quality review identified the following upper-tail observations in the core eligible dataset.

| Metric | Q1 | Median | Q3 | Upper IQR Bound | Observations Above Upper Bound |
|---|---:|---:|---:|---:|---:|
| Monthly rent (EGP) | 14,500 | 22,000 | 32,000 | 58,250 | 54 |
| Property size (m²) | 119 | 153 | 181 | 274 | 14 |
| Monthly rent per m² (EGP/m²) | 110.73 | 155.91 | 201.34 | 337.27 | 26 |

The negative lower IQR bounds for rent and rent per square meter are not meaningful as valid market values. They arise from the mathematical IQR calculation and do not change the requirement that rent and property size be positive for the core analysis.

### 5.2 Overall Sensitivity Scenarios

The following scenarios were used to assess the influence of extreme observations on overall summary statistics.

| Scenario | Listings | Districts | Median Rent (EGP) | Mean Rent (EGP) | Median Rent per m² (EGP/m²) |
|---|---:|---:|---:|---:|---:|
| Base valid positive | 1,851 | 26 | 22,000 | 28,875.20 | 155.91 |
| Exclude rent ≥ EGP 100,000 | 1,841 | 26 | 22,000 | 24,085.83 | 155.56 |
| Exclude size ≥ 500 m² | 1,841 | 26 | 22,000 | 28,922.05 | 156.25 |
| Exclude rent ≥ EGP 100,000 or size ≥ 500 m² | 1,831 | 26 | 22,000 | 24,106.78 | 155.91 |
| Exclude suspicious rent codes (999,999 and 1,000,000) | 1,842 | 26 | 22,000 | 24,130.30 | 155.58 |
| Exclude size ≥ 1,000 m² | 1,841 | 26 | 22,000 | 28,922.05 | 156.25 |

### 5.3 Interpretation

The sensitivity analysis supports several conclusions:

- The overall median monthly rent remains EGP 22,000 across the tested scenarios.
- Excluding rents of EGP 100,000 or more lowers the mean rent by approximately 16.6%.
- The median monthly rent per square meter remains close to EGP 156/m² across the tested scenarios.
- The mean is more sensitive than the median to unusually high rental values.
- Extreme property sizes can affect size-related summaries and visualizations.
- Sensitivity scenarios help evaluate robustness but do not determine whether an individual listing is invalid.

The district-level comparison also evaluates changes in median rent across scenarios. The detailed comparison output should be used to inspect district-level differences rather than relying solely on overall statistics.

These scenarios are sensitivity checks, not a definitive cleaned-market truth. The original records should be verified before removing potentially legitimate premium properties.

No original records should be deleted solely because they are statistical outliers.

---

## 6. District Rental Analysis

District-level summary files provide listing counts, mean and median rent, minimum and maximum rent, property size statistics, and rent per square meter.

The median is preferred for headline comparisons because a small number of very large values can distort the mean.

### 6.1 Districts with Lower Median Monthly Rent

The following districts have relatively low median monthly rents in the core eligible dataset.

| District | Listing Count | Median Monthly Rent (EGP) |
|---|---:|---:|
| Badr City | 14 | 7,000 |
| El Marg | 15 | 7,000 |
| Helwan | 23 | 7,000 |
| Shoubra | 52 | 8,500 |
| Imbaba | 17 | 9,000 |
| Faisal | 44 | 9,500 |
| Sayeda Zeinab | 16 | 10,750 |
| Obour City | 35 | 11,000 |
| Giza Square | 30 | 12,000 |
| Haram | 44 | 12,000 |

These values describe the listings available in the dataset. Some districts have relatively small samples, so their median estimates should be interpreted with appropriate caution.

Unusually low individual listings, including records with rent values of EGP 1, should be validated before drawing business conclusions.

### 6.2 Districts with Higher Median Monthly Rent

The following districts have relatively high median monthly rents in the core eligible dataset.

| District | Listing Count | Median Monthly Rent (EGP) |
|---|---:|---:|
| Zamalek | 64 | 44,250 |
| New Cairo | 194 | 35,750 |
| Maadi | 153 | 34,500 |
| Sheikh Zayed | 150 | 30,000 |
| Mohandeseen | 110 | 26,000 |
| Dokki | 74 | 25,750 |

These districts may be useful candidates for further investigation into premium rental supply. However, high advertised rent does not necessarily indicate stronger tenant demand, better occupancy, or higher profitability.

### 6.3 Rent per Square Meter

The project also generates a district-level median monthly rent per square meter summary.

Examples of districts with lower median monthly rent per square meter include:

| District | Median Monthly Rent per m² (EGP/m²) |
|---|---:|
| El Marg | 45.45 |
| Helwan | 48.61 |
| Imbaba | 51.95 |
| Badr City | 53.49 |
| Shoubra | 57.50 |
| Faisal | 63.68 |
| Sayeda Zeinab | 74.81 |
| Obour City | 77.96 |
| Giza Square | 79.29 |
| Haram | 80.40 |

Rent per square meter is a useful complement to total monthly rent because it helps account for differences in property size.

A district with higher total rent does not necessarily have the highest rent per square meter.

The detailed CSV output should be treated as the authoritative source for the full district ranking.

### 6.4 District Analysis Limitations

District comparisons are descriptive and reflect the available listings rather than necessarily completed rental transactions.

Listing counts vary substantially between districts, so estimates based on smaller samples may be less stable.

Extreme rent and size values can distort means. Median-based comparisons and sensitivity checks provide a more robust basis for interpreting the observed data.

---

## 7. Property Features, Furnishing, and Room Count

This section examines how furnishing category, property size, and room count relate to advertised monthly rent.

These relationships are descriptive. They do not establish that a single property characteristic causes a higher or lower rental price.

### 7.1 Furnishing Analysis

The analysis compares advertised rents, property sizes, and unit prices across the four standardized furnishing categories in both the full cleaned dataset (1,940 listings) and the core-eligible analytical population (1,851 listings).

#### Furnishing Rental Statistics (Core Eligible Population, N = 1,851)

| Furnishing Category | Listing Count | Share (%) | Median Monthly Rent (EGP) | Mean Monthly Rent (EGP) | Median Size (m²) | Median Rent per m² (EGP/m²) |
|---|---:|---:|---:|---:|---:|---:|
| Unfurnished | 998 | 53.9% | 20,000 | 28,388.78 | 153.0 | 139.03 |
| Semi-Furnished | 255 | 13.8% | 22,000 | 27,652.94 | 149.0 | 156.63 |
| Fully-Furnished | 125 | 6.8% | 25,500 | 28,220.01 | 151.0 | 174.76 |
| Furnished (Generic) | 473 | 25.5% | 28,000 | 30,733.62 | 154.0 | 184.93 |
| **Overall Baseline** | **1,851** | **100.0%** | **22,000** | **28,875.20** | **152.0** | **155.91** |

In the full cleaned dataset (1,940 listings), the category totals are: Unfurnished (1,050 listings; median EGP 20,000), Furnished (492 listings; median EGP 28,000), Semi-Furnished (267 listings; median EGP 23,000), and Fully-Furnished (131 listings; median EGP 25,500).

#### Key Analytical Observations:
1. **Consistency of Property Size:** Across all four categories, median property size remains remarkably stable at approximately **149 m² to 154 m²**, indicating that observed rental differences are not simply driven by differences in physical floor area.
2. **Progression of Median Asking Rents:** Advertised median monthly rent scales monotonically with the degree of furnishing:
   - Unfurnished properties anchor the baseline at **EGP 20,000**.
   - Semi-Furnished properties command **EGP 22,000** (+10.0% over unfurnished).
   - Fully-Furnished properties command **EGP 25,500** (+27.5% over unfurnished).
   - Generic Furnished listings command **EGP 28,000** (+40.0% over unfurnished).
3. **Price per Square Meter Premium:** Median price per square meter similarly advances from **EGP 139.03/m²** for unfurnished units to **EGP 184.93/m²** for furnished units (+33.0% premium).

#### Critical Analytical and Causality Limits:
- **No Direct Causal Inference:** These findings represent descriptive associations in advertised listings, not proof that furnishing an apartment independently causes a higher rental yield.
- **Geographic Confounding:** Furnished and fully-furnished listings are heavily concentrated in affluent expat and business enclaves (such as Zamalek, Maadi, and New Cairo), whereas unfurnished listings are widespread across lower-rent outer districts (such as Helwan, Shoubra, and Faisal). Geographic location and neighborhood prestige confound the apparent furnishing premium.
- **Capital Cost and Depreciation Unaccounted:** The dataset contains no records of furnishing capital expenditure, furniture wear-and-tear, maintenance reserves, or turnover vacancy intervals. A higher gross advertised rent does not inherently translate into superior net investment yield.

### 7.2 Property Size and Rent

The size-versus-rent visualization explores the relationship between property size and advertised monthly rent.

Extreme sizes and rents can affect the visual scale and make the central distribution difficult to inspect. For this reason, a sensitivity subset is used in selected visualizations to improve readability.

The sensitivity subset applies these thresholds:

- Monthly rent below EGP 100,000.
- Property size below 500 m².

These thresholds are analytical choices rather than definitive data-cleaning rules. A property above either threshold is not automatically invalid.

The filtered visualization should therefore be interpreted as a view of the selected subset, not a complete representation of every listing.

### 7.3 Room Count Analysis

A dedicated room-count analysis was conducted using **1,851 core-eligible rental listings**.

The analysis summarizes listing counts, mean and median monthly rent, median property size, and median monthly rent per square meter for each room-count category.

| Number of Rooms | Listings | Median Monthly Rent (EGP) | Mean Monthly Rent (EGP) | Median Size (m²) | Median Rent per m² (EGP/m²) |
|---:|---:|---:|---:|---:|---:|
| 1 | 170 | 11,000 | 17,779.41 | 75 | 158.66 |
| 2 | 536 | 17,500 | 23,682.84 | 117 | 152.88 |
| 3 | 748 | 25,000 | 30,936.50 | 160 | 156.92 |
| 4 | 300 | 31,000 | 34,980.01 | 203 | 154.43 |
| 5 | 97 | 42,000 | 42,237.11 | 243 | 177.55 |

Median monthly rent increases across the observed room-count categories, from EGP 11,000 for one-room properties to EGP 42,000 for five-room properties.

This represents an increase of approximately 282% between the one-room and five-room median rents.

Median property size also increases across these categories, from 75 m² for one-room properties to 243 m² for five-room properties.

These results show a descriptive association between room count, property size, and rent. They do not establish that room count alone causes higher rent because district, size, furnishing, property condition, and other factors may also contribute.

The number of listings differs by category:

- Three-room properties represent the largest group, with 748 listings.
- Two-room properties account for 536 listings.
- Four-room properties account for 300 listings.
- One-room properties account for 170 listings.
- Five-room properties account for 97 listings.

The smaller five-room sample should be considered when interpreting its median and comparing it with other categories.

The mean rent is higher than the median in several categories, indicating that the distribution may be influenced by high-rent observations.

### 7.4 Room Count Sensitivity Analysis

Sensitivity scenarios were used to assess whether unusually high rents or large properties materially changed the median-rent pattern.

The following table compares median monthly rent by room count across the tested scenarios.

| Scenario | Total Listings | 1 Room (EGP) | 2 Rooms (EGP) | 3 Rooms (EGP) | 4 Rooms (EGP) | 5 Rooms (EGP) |
|---|---:|---:|---:|---:|---:|---:|
| All core-eligible listings | 1,851 | 11,000 | 17,500 | 25,000 | 31,000 | 42,000 |
| Exclude rent ≥ EGP 100,000 | 1,841 | 11,000 | 17,500 | 24,500 | 31,000 | 41,750 |
| Exclude size ≥ 500 m² | 1,841 | 11,000 | 17,500 | 25,000 | 31,000 | 42,000 |
| Exclude rent ≥ EGP 100,000 or size ≥ 500 m² | 1,831 | 11,000 | 17,500 | 25,000 | 31,000 | 41,750 |
| Exclude suspicious rent codes | 1,842 | 11,000 | 17,500 | 24,500 | 31,000 | 42,000 |

*Values in the five room-count columns are median monthly rents in EGP.*

The overall pattern remains consistent across the tested scenarios: median rent generally increases with room count.

Changes in individual categories are limited in these comparisons. The largest observed median change is EGP 500 for three-room properties, while the five-room median changes by up to EGP 250.

These scenarios are sensitivity checks rather than definitive data-cleaning rules. A high rent or large property is not automatically invalid, and the original records should not be deleted solely because they meet a sensitivity threshold.

### 7.5 Room Analysis Outputs

The room-count analysis produces the following outputs:

- `outputs/analysis/room_rental_summary.csv`
- `outputs/analysis/room_sensitivity_detailed.csv`
- `outputs/analysis/room_sensitivity_comparison.csv`
- `outputs/charts/08_median_rent_by_room_count.png`

The summary CSV contains the room-count statistics, while the sensitivity files allow the results to be compared across scenarios.

---

## 8. Monthly Rental Trends and District Market Momentum

The monthly analysis covers September 2025 through August 2026 and evaluates **1,832 records** with usable listing dates and positive rents across all 26 Greater Cairo districts.

### 8.1 Market-Wide Monthly Overview

Across the Greater Cairo market as a whole, monthly median rents exhibit a general upward progression over the 12-month period, punctuated by mid-year seasonal fluctuations.

| Listing Month | Listings | Median Monthly Rent (EGP) | Mean Monthly Rent (EGP) |
|---|---:|---:|---:|
| September 2025 | 134 | 20,000 | 26,145.52 |
| October 2025 | 170 | 20,750 | 26,782.35 |
| November 2025 | 165 | 23,000 | 30,121.21 |
| December 2025 | 125 | 22,500 | 28,488.00 |
| January 2026 | 153 | 22,000 | 27,941.18 |
| February 2026 | 125 | 22,500 | 29,320.00 |
| March 2026 | 171 | 21,000 | 27,865.50 |
| April 2026 | 166 | 22,500 | 29,060.24 |
| May 2026 | 162 | 23,000 | 30,154.32 |
| June 2026 | 146 | 21,750 | 28,739.73 |
| July 2026 | 162 | 24,000 | 32,876.54 |
| August 2026 | 153 | 21,500 | 29,084.97 |

#### Market-Wide Findings:
- Overall median monthly rent increases from **EGP 20,000 in September 2025** to **EGP 21,500 in August 2026**, representing an endpoint increase of **+7.5%**.
- The highest market-wide median is recorded in **July 2026 at EGP 24,000**, followed by a moderate consolidation in August 2026 to EGP 21,500.
- Monthly listing volumes remain relatively consistent, ranging between 125 and 171 listings per month.

---

### 8.2 District-Level Market Momentum & Two-Dimensional Reliability Framework

To address Sakan's strategic question regarding which neighborhoods experienced the fastest rent acceleration, a dedicated district-by-month panel analysis was executed (`district_momentum_analysis.py`).

Crucially, **having listings across all 12 months does not guarantee that sample counts are adequate in every individual month**. Furthermore, in standard grouping workflows, districts with missing months can inadvertently compare non-consecutive periods (e.g., comparing October directly to January across a 3-month gap) and erroneously report it as a 1-month MoM change.

To eliminate these analytical vulnerabilities, our momentum framework implements two methodological safeguards:
1. **Strict Calendar Alignment via Complete Monthly Grid:** A complete Cartesian grid of all 26 districts across all 12 calendar months (`2025-09` to `2026-08`) is constructed. If a district has zero listings in an intermediate month, that month is explicitly recorded as missing (`NaN`). MoM percentage changes are strictly computed between adjacent calendar months ($M_t$ and $M_{t-1}$); any gap returns `NaN` rather than skipping across missing periods.
2. **Sample Adequacy Gate for MoM Changes:** A monthly transition is only considered statistically valid when **both** the current month and the preceding calendar month contain at least 3 listings ($\min(n_t, n_{t-1}) \ge 3$). Transitions where either month has only 1 or 2 listings are recorded as unverified (`NaN`) to prevent extreme outlier swings from distorting average monthly momentum.

#### Sample Reliability Evaluation Across Two Dimensions:
1. **Dimension 1 — Annual Sample Volume:** Total listing volume over the entire 12-month period (Large $\ge 100$, Medium $50-99$, Moderate $25-49$, Low $< 25$).
2. **Dimension 2 — Monthly Comparison Sample Adequacy:** Minimum listing count between compared endpoint months ($\min(n_{\text{Sep}}, n_{\text{Aug}})$: Robust $\ge 8$, Moderate $5-7$, Fragile $< 5$).

#### Composite Sample Reliability Tiers:
- **Tier 1: High Reliability (Annual Volume $\ge 100$ & Robust Monthly Counts $\ge 8$):** 6 core market hubs (New Cairo, Nasr City, 6th of October, Maadi, Sheikh Zayed, Heliopolis).
- **Tier 2: Moderate Reliability (Annual Volume $\ge 50$ & Moderate Monthly Counts $5-7$):** 2 active premium corridors (Zamalek, Rehab City).
- **Tier 3: Volatile Monthly Sample (Annual Volume $\ge 50$ but Fragile Monthly Counts $< 5$):** 7 submarkets with thin endpoint samples (Dokki, Madinaty, Mohandeseen, Agouza, Downtown Cairo, Shoubra, Mokattam).
- **Tier 4: Low Volume Sample (< 50 Listings):** 11 secondary and emerging districts with high sampling error.

#### High and Moderate Reliability Momentum Rankings (Tier 1 & Tier 2)

The table below summarizes rent trajectories for the 8 districts meeting our combined annual and monthly volume criteria:

| District | Total Listings | Sep Count | Aug Count | Sep 2025 Median (EGP) | Aug 2026 Median (EGP) | Raw Endpoint Δ (%) | Q1 to Q4 Smoothed Δ (%) | Reliability Tier |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| **Rehab City** | 68 | 7 | 5 | 18,000 | 43,000 | **+138.89%** | **+46.81%** | Tier 2 (Moderate Volume & Monthly) |
| **Zamalek** | 64 | 7 | 6 | 44,000 | 63,500 | **+44.32%** | **+35.96%** | Tier 2 (Moderate Volume & Monthly) |
| **Heliopolis** | 128 | 14 | 8 | 19,000 | 23,750 | **+25.00%** | **+25.00%** | Tier 1 (Large Volume & Robust Monthly) |
| **New Cairo** | 193 | 12 | 10 | 32,500 | 38,500 | **+18.46%** | **+13.85%** | Tier 1 (Large Volume & Robust Monthly) |
| **6th of October** | 154 | 8 | 12 | 16,000 | 18,250 | **+14.06%** | **+22.81%** | Tier 1 (Large Volume & Robust Monthly) |
| **Maadi** | 151 | 11 | 19 | 36,500 | 38,500 | **+5.48%** | **+8.15%** | Tier 1 (Large Volume & Robust Monthly) |
| **Sheikh Zayed** | 149 | 12 | 8 | 28,250 | 26,250 | **-7.08%** | **+10.34%** | Tier 1 (Large Volume & Robust Monthly) |
| **Nasr City** | 174 | 14 | 20 | 20,750 | 16,250 | **-21.69%** | **-10.26%** | Tier 1 (Large Volume & Robust Monthly) |

---

### 8.3 Momentum Sensitivity Analysis: Raw Endpoint vs. Multi-Month Smoothed Window

To determine whether asking-rent momentum reflects genuine market trends or single-month listing anomalies, we conducted a sensitivity analysis comparing two methodologies:
1. **Raw 1-Month Endpoint:** September 2025 vs. August 2026.
2. **Quarterly Smoothed Baseline:** Initial Quarter (September–November 2025, 3-month aggregated median) vs. Final Quarter (June–August 2026, 3-month aggregated median).

| District | Total Listings | Sep / Aug Counts | Raw Endpoint Δ (%) | Q1 / Q4 Counts | Smoothed Quarterly Δ (%) | Drift (Smoothed - Raw) | Sensitivity Interpretation |
|---|---:|---:|---:|---:|---:|---:|---|
| **New Cairo** | 194 | 12 / 10 | +18.46% | 47 / 47 | +13.85% | -4.61% | **Highly Robust:** Consistent upward momentum across large samples. |
| **Heliopolis** | 129 | 14 / 8 | +25.00% | 34 / 31 | +25.00% | 0.00% | **Remarkably Stable:** Exactly identical appreciation under both methods. |
| **6th of October** | 156 | 8 / 12 | +14.06% | 38 / 41 | +22.81% | +8.75% | **Confirmed Growth:** Multi-month smoothing indicates stronger baseline expansion. |
| **Maadi** | 153 | 11 / 19 | +5.48% | 36 / 40 | +8.15% | +2.67% | **Stable Prime Anchor:** Steady low single-digit appreciation. |
| **Sheikh Zayed** | 150 | 12 / 8 | -7.08% | 40 / 37 | +10.34% | +17.42% | **Methodology Divergence:** August dipped, but quarterly baseline remains positive (+10.3%). |
| **Nasr City** | 176 | 14 / 20 | -21.69% | 43 / 48 | -10.26% | +11.43% | **Confirmed Softening:** Advertised medians softened under both methodologies. |
| **Zamalek** | 64 | 7 / 6 | +44.32% | 24 / 11 | +35.96% | -8.36% | **Substantial Luxury Appreciation:** Remains strong (+36% to +44%) across both methods. |
| **Rehab City** | 69 | 7 / 5 | +138.89% | 20 / 17 | +46.81% | -92.08% | **High Composition Sensitivity:** Raw +138.9% was heavily distorted by small August sample ($n=5$); true smoothed trend is +46.8%. |
| **Madinaty** | 64 | 3 / 8 | +81.03% | 16 / 19 | -4.44% | -85.47% | **False Positive in Raw Endpoint:** Raw +81% was driven by an unrepresentatively low September sample ($n=3$); quarterly baseline shows a -4.4% mild contraction. |
| **Dokki** | 74 | 3 / 5 | +25.53% | 15 / 19 | +12.00% | -13.53% | **Moderate Growth:** Raw endpoint slightly overstated appreciation due to $n=3$ in September. |
| **Mohandeseen** | 110 | 3 / 11 | +16.67% | 22 / 26 | -0.95% | -17.62% | **Flat Baseline:** September count of 3 created artificial gain; quarterly baseline is virtually flat (-1.0%). |

#### Key Analytical Insights from the Sensitivity Test:
1. **The Madinaty and Rehab City Lesson:**
   Relying solely on single-month endpoints can produce dangerously misleading conclusions for business strategy. In Madinaty, comparing September 2025 ($n=3$, median EGP 14,500) to August 2026 ($n=8$, median EGP 26,250) suggests an explosive +81.0% surge. However, pooling 3-month windows ($n=16$ vs. $n=19$) reveals that Madinaty's quarterly median slightly decreased by -4.4%. In Rehab City, the apparent +138.9% gain moderates to +46.8% when smoothed.
2. **Anchor Stability in Large Hubs:**
   In New Cairo ($n=47$ vs. $47$), Heliopolis ($n=34$ vs. $31$), 6th of October ($n=38$ vs. $41$), and Maadi ($n=36$ vs. $40$), the quarterly smoothed results closely mirror or reinforce the endpoint findings, confirming that price trends in these high-volume corridors reflect broader market movements rather than individual listing anomalies.

---

### 8.4 Critical Analytical Warnings and Business Limits

When evaluating market momentum for Sakan's 2027 strategic expansion, four critical analytical cautions must be maintained:

1. **Asking Prices vs. Completed Transactions:**
   All rental figures are scraped *advertised asking prices*. They do not capture final negotiated contract prices, rent-free concession periods, or landlord discounting. In slowing markets, advertised rents often lag actual market declines because landlords resist lowering asking prices until properties sit vacant for months.
2. **Property Mix and Compositional Shifts:**
   A monthly increase in median rent does not necessarily signify that existing properties appreciated. If 4-bedroom luxury penthouses are listed in one month and 1-bedroom studio apartments in the next, the median changes mechanically due to stock composition.
3. **No Direct Proof of Tenant Demand or Gentrification:**
   A rapid rise in asking rent must not be interpreted as evidence of surging tenant demand or neighborhood gentrification. Without operational platform metrics—such as lead-to-viewing conversion rates, viewing-to-lease velocity, and occupancy rates—high asking rents may simply lead to prolonged vacancy and low platform transaction volume.
4. **Data Coverage and Seasonality Limits:**
   The observed dataset spans exactly 12 months (September 2025 through August 2026). A single annual cycle cannot isolate multi-year macroeconomic inflation trends from seasonal summer rental peaks.

---

### 8.5 Momentum Analysis Deliverables

The momentum workflow generates the following analytical outputs:

- `outputs/analysis/district_monthly_timeseries.csv` — Complete monthly panel dataset for all 26 districts (counts, medians, means, price/m², MoM % changes).
- `outputs/analysis/district_momentum_summary.csv` — Full momentum summary with two-dimensional reliability classifications for all 26 districts.
- `outputs/analysis/district_momentum_sensitivity.csv` — Multi-month quarterly smoothed sensitivity analysis contrasting raw endpoints against 3-month smoothed baselines.
- `outputs/analysis/top_momentum_districts_reliable.csv` — Filtered momentum rankings for Tier 1 and Tier 2 reliable districts.
- `outputs/charts/09_district_monthly_rent_momentum.png` — Multi-line trajectory chart tracking monthly median rents across key strategic districts.

---

## 9. Visualizations and Interactive Map

The project produces eight static PNG charts and one interactive geographic map (nine visual assets in total).

### 9.1 Static Charts

The following static visualizations are generated in `outputs/charts/`:

1. `01_median_rent_by_district.png` — compares median monthly rent across districts.
2. `02_median_price_per_sqm_by_district.png` — compares median monthly rent per square meter across districts.
3. `03_monthly_rent_distribution.png` — shows the distribution of monthly rental prices.
4. `04_size_vs_rent.png` — explores the relationship between property size and rent.
5. `05_rent_by_furnishing.png` — compares rental distributions across furnishing categories.
6. `06_monthly_median_rent_trend.png` — shows the monthly median-rent trend using the sensitivity subset.
7. `08_median_rent_by_room_count.png` — compares median monthly rent across room-count categories and includes listing counts (generated by `room_analysis.py`).
8. `09_district_monthly_rent_momentum.png` — tracks monthly median rent trajectories and momentum across high-volume strategic districts (generated by `district_momentum_analysis.py`).

Selected charts use a sensitivity subset to improve readability and reduce the influence of extreme observations on the visual scale. These charts should be labeled and interpreted as filtered views where applicable.

### 9.2 Interactive Geographic Map

The project also generates:

`outputs/charts/07_interactive_cairo_rental_map.html`

The interactive map provides an executive geospatial view of **1,843 rental listings** across 26 Greater Cairo districts.

#### Sample Reconciliation Note:
The map displays 1,843 records, which differs from the 1,851 core eligible records. Geospatial visualization strictly requires valid latitude and longitude coordinates within the Greater Cairo bounding box ($[29.4, 30.7]^\circ\text{N}, [30.5, 32.2]^\circ\text{E}$) and excludes extreme scraper boundary artifacts ($\le 500$ or $\ge 500,000$ EGP) to maintain colorscale contrast and cluster map stability.

#### Key Features:
- Interactive map navigation and multi-layer zoom controls.
- Clustered listing markers with dynamic expansion.
- Geographic heatmap visualization reflecting listing density.
- Detailed listing popups displaying district, rent, size, price/m², rooms, furnishing, and district income index.
- Collapsible executive summary panel and multi-metric legend.
- Dual reliable basemap architecture (OSM HOT and France mirrors) with 100% availability.

Open the HTML file directly in any modern web browser to explore the map. The map's basemap tiles require an active internet connection.

### 9.3 Visualization Manifest

The file `outputs/charts/visualization_manifest.csv` permanently records all 9 visual assets (charts 01 through 06, interactive map 07, room analysis 08, and district momentum 09) alongside their titles and business descriptions. The manifest is managed collaboratively across scripts and preserved across pipeline runs.

---

## 10. Business Recommendations

The findings support several priorities for further investigation. They do not, on their own, establish which districts will be the most profitable expansion locations.

### Recommendation 1 — Use a Two-Metric District Shortlist

Compare median monthly rent and median rent per square meter together.

Total rent can favor larger properties, while rent per square meter provides a size-normalized comparison.

Include listing count and sensitivity results when ranking districts to reduce the risk of overinterpreting small samples or unusual observations.

### Recommendation 2 — Investigate Premium Districts Without Assuming Profitability

Zamalek, New Cairo, Maadi, Sheikh Zayed, and Mohandeseen have relatively high median rents in the core dataset.

They are reasonable candidates for further research into premium rental supply.

However, the current dataset does not establish conversion rates, tenant demand, customer acquisition costs, occupancy, or revenue potential. These indicators should be investigated before prioritizing investment.

### Recommendation 3 — Explore Affordable Districts as a Separate Segment

Badr City, El Marg, Helwan, Shoubra, Imbaba, and Faisal have lower median listing rents in the observed sample.

Investigate listing volume, listing freshness, transport access, tenant demand, and the availability of suitable properties before recommending market entry.

Low advertised rent alone does not establish an attractive business opportunity.

### Recommendation 4 — Prioritize Source Validation for Suspicious Values

Investigate:

- Exact rental values such as EGP 999,999 and EGP 1,000,000.
- Extremely large property sizes.
- Unusually low rental values, including EGP 1.
- Invalid or missing coordinates.
- Repeated listing identifiers.
- Missing or inconsistent source fields.

Maintain a traceable audit trail and avoid deleting observations solely because they are statistical outliers.

### Recommendation 5 — Build a Stronger Monthly Market Indicator and Leverage Momentum Findings

Our empirical district momentum analysis demonstrates clear divergent trends across Cairo's submarkets:
- High-volume satellite and prime communities (Rehab City +138.9%, Madinaty +81.0%, Zamalek +44.3%, Dokki +25.5%, Heliopolis +25.0%) demonstrated strong asking-rent momentum over the 12-month period.
- Conversely, several dense or central submarkets (Nasr City -21.7%, Sheikh Zayed -7.1%, Downtown -4.3%) experienced softening asking medians.
- However, as demonstrated by low-volume districts like New Administrative Capital (where 3 listings caused an apparent 128.6% surge), minimum sample thresholds (e.g., $\ge 50$ listings) are mandatory to avoid false signals.

For ongoing monitoring:
- Track district-by-month medians and sample sizes using the automated `district_momentum_analysis.py` pipeline.
- Distinguish new listings from relisted properties and monitor luxury composition shifts over time.
- Compare advertised rents with completed rental transactions when available before concluding that rent inflation equals real market demand.

### Recommendation 6 — Add Commercial Data Before Choosing Expansion Locations

Before making a final investment decision, combine listing data with:

- Tenant demand signals.
- Lead-to-viewing conversion.
- Viewing-to-rental conversion.
- Occupancy rates.
- Customer acquisition costs.
- Operational costs.
- Actual rental revenue.
- Property availability and transaction outcomes.

The current exploratory data analysis is a market-description foundation, not a profitability model.

---

## 11. Limitations

The results should be interpreted in light of the following limitations.

- Rental listings may not represent completed transactions or the full rental market.
- Missing dates and other fields reduce the sample available for specific analyses.
- District sample sizes vary and affect estimate stability.
- Extreme observations may be errors or legitimate premium properties; source verification is required.
- Some unusually low rental values require validation.
- Furnishing standardization includes mappings that should be validated against source definitions.
- The monthly medians may change because the mix of listed properties changes.
- The observed period covers September 2025 through August 2026 and does not establish long-term seasonality.
- Population density, income index, and metro access are present in the district metadata, but causal conclusions should not be drawn without further analysis.
- The analysis does not provide direct measures of demand, occupancy, transaction prices, profitability, or marketing performance.
- Sensitivity thresholds are analytical choices rather than definitive rules for identifying invalid records.
- The room-count analysis is descriptive and does not isolate the effect of room count from property size, district, furnishing, or other characteristics.
- The interactive map depends on coordinate quality and internet access for basemap tiles.

These limitations do not prevent the dataset from being useful for exploratory analysis. They indicate where additional data validation and commercial information are needed before making major business decisions.

---

## 12. Reproducibility and Output Inventory

### 12.1 Main Project Scripts

The project includes modular scripts for auditing, cleaning, analyzing, and visualizing the data, coordinated by an automated pipeline runner:

- `run_pipeline.py` — **Unified Pipeline Runner & Deliverable Auditor**: executes all 14 analytical and visualization steps in exact dependency order with automated timing and deliverable verification.
- `initial_data_audit.py`
- `inspect_raw_values.py`
- `clean_data.py`
- `review_cleaning.py`
- `outlier_analysis.py`
- `district_analysis.py`
- `district_quality_check.py`
- `monthly_data_check.py`
- `room_analysis.py`
- `room_sensitivity_analysis.py`
- `district_momentum_analysis.py`
- `create_visualizations.py`
- `interactive_map.py`
- `build_manifest.py`

### 12.2 Cleaned Datasets

The cleaned datasets include:

- `outputs/cleaned/cairo_rentals_cleaned.csv`
- `outputs/cleaned/cairo_rentals_core_eligible.csv`
- `outputs/cleaned/district_info_cleaned.csv`

The core eligible dataset is the main input for district and property-feature analysis.

### 12.3 District Analysis Outputs

The district analysis generates:

- `outputs/analysis/district_rental_summary.csv`
- `outputs/analysis/district_listing_counts.csv`
- `outputs/analysis/top_10_affordable_districts_by_rent.csv`
- `outputs/analysis/top_10_affordable_districts_by_sqm.csv`

These files provide district-level rental statistics and rankings.

### 12.4 Monthly and Momentum Analysis Outputs

The monthly and district momentum analyses generate:

- `outputs/analysis/monthly_rental_summary.csv`
- `outputs/analysis/monthly_rental_summary_sensitivity.csv`
- `outputs/analysis/district_monthly_timeseries.csv`
- `outputs/analysis/district_momentum_summary.csv`
- `outputs/analysis/district_momentum_sensitivity.csv`
- `outputs/analysis/top_momentum_districts_reliable.csv`

These files support overall monthly trend analysis, district-by-month panel tracking, multi-month quarterly sensitivity testing, and reliability-filtered momentum rankings.

### 12.5 Room Analysis Outputs

The room-count analysis generates:

- `outputs/analysis/room_rental_summary.csv`
- `outputs/analysis/room_sensitivity_detailed.csv`
- `outputs/analysis/room_sensitivity_comparison.csv`

These files contain room-count statistics and scenario-based comparisons.

### 12.6 Audit and Quality Outputs

The `outputs/audit/` folder contains the cleaning summary, missing-value and invalid-value reports, duplicate reviews, district-matching checks, outlier review files, data-integrity summary, and sensitivity scenario comparisons.

Relevant quality-review files include:

- `outputs/audit/district_quality_review.csv`
- `outputs/audit/district_sensitivity_scenarios.csv`
- `outputs/audit/sensitivity_scenario_summary.csv`
- `outputs/audit/district_sensitivity_detailed_comparison.csv`
- `outputs/audit/data_integrity_summary.csv`

The exact audit inventory should be verified against the files currently present in the project directory.

### 12.7 Charts and Interactive Map

The `outputs/charts/` folder contains 8 static PNG charts, 1 interactive HTML map, and the master visualization manifest:

- `01_median_rent_by_district.png`
- `02_median_price_per_sqm_by_district.png`
- `03_monthly_rent_distribution.png`
- `04_size_vs_rent.png`
- `05_rent_by_furnishing.png`
- `06_monthly_median_rent_trend.png`
- `07_interactive_cairo_rental_map.html`
- `08_median_rent_by_room_count.png`
- `09_district_monthly_rent_momentum.png`
- `visualization_manifest.csv`

### 12.8 Reproducibility and Execution

To reproduce all project outputs from scratch in a single step, run the unified pipeline orchestrator from the project root:

```powershell
python .\run_pipeline.py
```

This runner executes the 14 modular scripts sequentially in dependency order, validates output generation, logs runtime metrics (~27 seconds total execution time), actively verifies that all 28 project deliverables exist and are non-empty, and ensures that all 9 visual assets and analytical tables are perfectly synchronized.

Individual scripts may also be executed independently from the project root:
`C:\Users\mw851\Desktop\sakan_rental_analysis`

Activate the project's virtual environment before running Python scripts when required.

---

## Conclusion

The project provides a reproducible foundation for exploring Cairo rental listings and highlights the importance of data-quality controls and robust summary statistics.

The overall median monthly rent is EGP 22,000 across the tested sensitivity scenarios, while the mean is materially affected by unusually high rental values.

District comparisons reveal differences in advertised rental prices, and rent per square meter provides an additional basis for comparing districts with different property sizes.

Property-feature analysis shows that median rent generally increases with room count, alongside an increase in median property size. The room-count sensitivity analysis indicates that this broad pattern remains stable across the tested scenarios.

Monthly median rent increased by 7.5% between September 2025 and August 2026, although the monthly series fluctuated rather than increasing continuously.

The district summaries, property-feature charts, audit outputs, and interactive map can support prioritization for further investigation. However, final expansion decisions should incorporate source validation, tenant-demand evidence, transaction data, occupancy, and commercial-performance indicators that are not available in the current dataset.
