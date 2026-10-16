\# Cairo Real Estate Rental Market Analysis



\## 1. Business Context

\*\*Guidance:\*\* Use this section to align your data science workflow with Sakanâ€™s strategic business objectives.



\*   **The Company:** Sakan, Cairo's premier property technology platform.

*   **The Situation:** Rapid platform growth has resulted in a massive influx of daily rental listing data. However, this raw data is heavily fragmented, noisy, and contains severe anomalies. 

*   **The Objective:** Sakan's executive team is targeting a major expansion in early 2027. They need a pristine analytical pipeline to transform messy simulated portal listing data into high-confidence business intelligence.

*   **The Challenge:** Before any machine learning or predictive modeling can occur, the raw dataset must be meticulously cleaned. Following data sanitization, the executive board requires a comprehensive Exploratory Data Analysis (EDA) to map out high-yield investment zones across Greater Cairo.



\---



\## 2. Core Analytical Questions

\*\*Guidance:\*\* Formulate specific, answerable questions that your EDA will address. Consider the underlying drivers of the Egyptian real estate market. 



To support the 2027 expansion strategy, your analysis must answer the following:



1\. \*\*District Valuation:\*\* Which Cairo districts (e.g., New Cairo, Sheikh Zayed, Maadi, Nasr City) command the highest median rent and the highest price per square meter (EGP/mÂ²)?

2\. \*\*Feature Importance:\*\* How do specific property featuresâ€”primarily total square meterage, number of bedrooms, and furnishing status (Unfurnished, Semi-Furnished, Fully-Furnished)â€”correlate with the final listing price?

3\. \*\*Market Momentum:\*\* Based on month-on-month data, which neighborhoods are experiencing the most aggressive rent increases, indicating high tenant demand or gentrification?

4\. \*\*Data Integrity:\*\* What proportion of the original scrape consisted of duplicate listings or extreme outliers (e.g., phantom listings priced at 1 EGP or 1,000,000 EGP/month), and how does removing them shift the baseline market averages?



\---



\## 3. Data Science Process Steps Mapping

\*\*Guidance:\*\* Map your technical toolkit (Pandas, NumPy, Matplotlib, Seaborn, Plotly) to the required analytical phases.



\*   \*\*Phase 1: Data Ingestion \& Cleaning (Pandas)\*\*

&#x20;   \*   \*Task:\* Import `cairo\_rentals.csv`.

&#x20;   \*   \*Task:\* Handle missing values, standardize unit formatting (e.g., extracting numeric values from string-based size columns), and drop exact duplicate rows.

\*   \*\*Phase 2: Outlier Mitigation (NumPy \& Pandas)\*\*

&#x20;   \*   \*Task:\* Utilize NumPy boolean masking to filter out extreme statistical outliers in rental prices (EGP) and property sizes (mÂ²) to prevent skewed visualizations.

\*   \*\*Phase 3: Data Integration \& Feature Engineering (Pandas)\*\*

&#x20;   \*   \*Task:\* Merge the cleaned listings with `district\_info.csv` to append demographic and location metadata.

&#x20;   \*   \*Task:\* Engineer a new target metric: `price\_per\_sqm` (Rental Price / Property Size).

&#x20;   \*   \*Task:\* Calculate month-on-month price deltas.

\*   \*\*Phase 4: Exploratory Analysis \& Aggregation (Pandas)\*\*

&#x20;   \*   \*Task:\* Use `groupby` operations to aggregate average prices across districts and furnishing tiers.

\*   \*\*Phase 5: Statistical Visualization (Matplotlib \& Seaborn)\*\*

&#x20;   \*   \*Task:\* Generate foundational distribution charts (histograms of rent prices).

&#x20;   \*   \*Task:\* Create advanced correlation visualizations (e.g., Seaborn heatmaps or boxplots comparing rent across districts).

\*   \*\*Phase 6: Geospatial Visualization (Plotly)\*\*

&#x20;   \*   \*Task:\* Build an interactive map using district coordinates to visually highlight high-price and rapidly appreciating micro-markets across the Cairo metropolis.



\---



\## 4. Expected Outcomes

\*\*Guidance:\*\* Define what success looks like for this consultancy engagement.



By the conclusion of this analysis, you will deliver:

1\. \*\*A Cleaned Analytical Dataset:\*\* A robust dataset free of extreme outliers, missing critical variables, and duplicates, ready for future machine learning applications.

2\. \*\*Interactive Geographic Intelligence:\*\* A Plotly-based interactive map that Sakan executives can use to physically pinpoint their 2027 marketing and acquisition efforts.

3\. \*\*The Data Story:\*\* A cohesive narrative summarizing the statistical findings. This narrative must move beyond generic observations, offering definitive recommendations on where Sakan should focus its resources to maximize platform yield based on EGP/mÂ² trends.

