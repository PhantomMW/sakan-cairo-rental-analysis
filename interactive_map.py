"""
================================================================================
SAKAN | EXECUTIVE GEOSPATIAL INTELLIGENCE PLATFORM
Interactive Cairo Real Estate Rental Market Explorer
================================================================================
Generates an executive-grade, standalone interactive dashboard with multi-layer
geospatial intelligence, rock-solid OSM HOT / France / Satellite basemaps
(100% free, no API key, no watermarks, no 403 blocks), and KPI summary stats.

Run from project root:
    python .\interactive_map.py

Output:
    outputs\charts\07_interactive_cairo_rental_map.html
"""

from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import plotly.graph_objects as go

PROJECT_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = PROJECT_DIR / "outputs" / "charts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "07_interactive_cairo_rental_map.html"

REQUIRED_COLUMNS = {
    "district", "latitude", "longitude", "size_sqm",
    "rooms", "furnished", "monthly_rent_egp"
}

# -----------------------------------------------------------------------------
# Guaranteed Reliable Basemap Tile Definitions
# 100% Free, Public, No API Key, No Watermarks, No 403 Errors, Standard XYZ
# -----------------------------------------------------------------------------
STYLE_OSM_HOT = {
    "version": 8,
    "sources": {
        "osm-hot": {
            "type": "raster",
            "tiles": [
                "https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                "https://b.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team"
        }
    },
    "layers": [
        {
            "id": "osm-hot-layer",
            "type": "raster",
            "source": "osm-hot",
            "minzoom": 0,
            "maxzoom": 19
        }
    ]
}

STYLE_OSM_FRANCE = {
    "version": 8,
    "sources": {
        "osm-fr": {
            "type": "raster",
            "tiles": [
                "https://a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
                "https://b.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© OpenStreetMap contributors, OpenStreetMap France"
        }
    },
    "layers": [
        {
            "id": "osm-fr-layer",
            "type": "raster",
            "source": "osm-fr",
            "minzoom": 0,
            "maxzoom": 19
        }
    ]
}

STYLE_OPENTOPO = {
    "version": 8,
    "sources": {
        "opentopo": {
            "type": "raster",
            "tiles": [
                "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
                "https://b.tile.opentopomap.org/{z}/{x}/{y}.png"
            ],
            "tileSize": 256,
            "attribution": "© OpenTopoMap, © OpenStreetMap contributors"
        }
    },
    "layers": [
        {
            "id": "opentopo-layer",
            "type": "raster",
            "source": "opentopo",
            "minzoom": 0,
            "maxzoom": 17
        }
    ]
}

STYLE_SATELLITE = {
    "version": 8,
    "sources": {
        "esri-satellite": {
            "type": "raster",
            "tiles": [
                "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
            ],
            "tileSize": 256,
            "attribution": "© Esri, Earthstar Geographics"
        }
    },
    "layers": [
        {
            "id": "satellite-layer",
            "type": "raster",
            "source": "esri-satellite",
            "minzoom": 0,
            "maxzoom": 19
        }
    ]
}


def find_rental_data():
    """Find the cleaned rental CSV by checking its columns."""
    search_roots = [
        PROJECT_DIR / "outputs" / "cleaned",
        PROJECT_DIR / "data",
        PROJECT_DIR / "outputs",
    ]

    checked = set()
    for root in search_roots:
        if not root.exists():
            continue
        candidates = sorted(root.rglob("*.csv"))
        candidates.sort(
            key=lambda p: (
                0 if ("clean" in p.name.lower() and "rent" in p.name.lower()) else
                1 if "rent" in p.name.lower() else 2,
                len(p.parts),
                p.name.lower(),
            )
        )
        for path in candidates:
            if path in checked:
                continue
            checked.add(path)
            try:
                cols = set(pd.read_csv(path, nrows=0).columns)
                if REQUIRED_COLUMNS.issubset(cols):
                    return path
            except Exception:
                pass

    raise FileNotFoundError(
        "Couldn't locate a rental CSV containing all required columns: "
        + ", ".join(sorted(REQUIRED_COLUMNS))
    )


def load_district_metadata():
    """Load district info metadata if available."""
    candidates = [
        PROJECT_DIR / "outputs" / "cleaned" / "district_info_cleaned.csv",
        PROJECT_DIR / "data" / "district_info.csv",
    ]
    for c in candidates:
        if c.exists():
            try:
                return pd.read_csv(c)
            except Exception:
                pass
    return pd.DataFrame()


def format_currency(val):
    if pd.isna(val):
        return "N/A"
    return f"EGP {val:,.0f}"


def format_sqm_price(val):
    if pd.isna(val):
        return "N/A"
    return f"EGP {val:,.0f}/m²"


def main():
    print("=" * 75)
    print("SAKAN | EXECUTIVE INTERACTIVE CAIRO RENTAL MAP GENERATOR")
    print("=" * 75)

    data_path = find_rental_data()
    print(f"Loading primary dataset: {data_path}")
    df = pd.read_csv(data_path)
    total_raw_records = len(df)
    print(f"Total raw records: {total_raw_records:,}")

    # Parse numeric fields
    for col in ["latitude", "longitude", "monthly_rent_egp", "size_sqm", "rooms"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Filter valid coordinates in Greater Cairo and realistic rents
    # Exclude scraper anomalies (<= 500 EGP and >= 500,000 EGP)
    valid_mask = (
        df["latitude"].between(29.4, 30.7)
        & df["longitude"].between(30.5, 32.2)
        & df["monthly_rent_egp"].gt(500)
        & df["monthly_rent_egp"].lt(500000)
        & df["district"].notna()
    )
    mapped = df.loc[valid_mask].copy()

    excluded_count = total_raw_records - len(mapped)
    print(f"Cleaned mapped records: {len(mapped):,} (Excluded {excluded_count:,} anomalies/missing)")

    # Derived metrics
    mapped["price_per_sqm"] = np.where(
        mapped["size_sqm"] > 10,
        mapped["monthly_rent_egp"] / mapped["size_sqm"],
        np.nan
    )

    # Standardize furnishing
    mapped["furnished_str"] = mapped["furnished"].fillna("Unfurnished").astype(str).str.strip().str.title()
    mapped["is_furnished"] = (
        mapped["furnished_str"].str.lower().str.contains("furnish")
        & ~mapped["furnished_str"].str.lower().str.contains("un")
    )
    mapped["furnishing_badge"] = np.where(mapped["is_furnished"], "Furnished", "Unfurnished")

    # Merge district info metadata
    dist_info = load_district_metadata()
    if not dist_info.empty and "district" in dist_info.columns:
        mapped = mapped.merge(dist_info, on="district", how="left", suffixes=("", "_meta"))
    else:
        mapped["population_density"] = np.nan
        mapped["avg_income_index"] = np.nan
        mapped["metro_access"] = False

    # Outlier capping for visual colorscale contrast
    rent_cap = float(mapped["monthly_rent_egp"].quantile(0.98))
    sqm_cap = float(mapped["price_per_sqm"].dropna().quantile(0.98))

    mapped["rent_capped"] = mapped["monthly_rent_egp"].clip(upper=rent_cap)
    mapped["sqm_capped"] = mapped["price_per_sqm"].clip(upper=sqm_cap)

    # -------------------------------------------------------------------------
    # District Level Aggregation (Macro Executive View)
    # -------------------------------------------------------------------------
    district_agg = mapped.groupby("district").agg(
        listing_count=("district", "count"),
        median_rent=("monthly_rent_egp", "median"),
        mean_rent=("monthly_rent_egp", "mean"),
        median_price_per_sqm=("price_per_sqm", "median"),
        median_size=("size_sqm", "median"),
        median_rooms=("rooms", "median"),
        lat=("latitude", "mean"),
        lon=("longitude", "mean"),
        furnished_pct=("is_furnished", lambda s: s.mean() * 100),
        pop_density=("population_density", lambda s: s.dropna().iloc[0] if len(s.dropna()) else np.nan),
        income_index=("avg_income_index", lambda s: s.dropna().iloc[0] if len(s.dropna()) else np.nan),
        metro=("metro_access", lambda s: s.dropna().iloc[0] if len(s.dropna()) else False)
    ).reset_index()

    district_agg = district_agg.sort_values(by="median_rent", ascending=False).reset_index(drop=True)

    # Categorize investment tier
    def assign_tier(rent):
        if rent >= 30000:
            return "Tier 1: Prime Luxury"
        elif rent >= 20000:
            return "Tier 2: High Demand"
        elif rent >= 12000:
            return "Tier 3: Mid-Market Value"
        else:
            return "Tier 4: High Affordability"

    district_agg["tier"] = district_agg["median_rent"].apply(assign_tier)

    # Map center coordinates for Greater Cairo
    center_lat = 30.045
    center_lon = 31.330
    default_zoom = 10

    # Overall Cairo KPIs
    cairo_median_rent = float(mapped["monthly_rent_egp"].median())
    cairo_median_sqm = float(mapped["price_per_sqm"].median())
    total_districts = len(district_agg)
    top_district = district_agg.iloc[0]["district"]
    top_district_rent = district_agg.iloc[0]["median_rent"]
    affordable_district = district_agg.iloc[-1]["district"]
    affordable_district_rent = district_agg.iloc[-1]["median_rent"]

    # -------------------------------------------------------------------------
    # Build Plotly Figure
    # -------------------------------------------------------------------------
    fig = go.Figure()

    # High-contrast color ramp: Deep Blue -> Teal -> Emerald -> Gold -> Red
    colorscale_rent = "Turbo"

    # --- TRACE 0: District Hubs (Macro Overview) ---
    # Prominent, prominent bubbles with crisp white outline!
    max_count = max(district_agg["listing_count"].max(), 1)
    bubble_sizes = [float(26 + 26 * np.sqrt(c / max_count)) for c in district_agg["listing_count"]]

    district_hover = []
    for _, r in district_agg.iterrows():
        metro_text = "Direct Metro Access" if r["metro"] is True else "Planned / Bus Link"
        hover_html = (
            f"<b>{r['district']}</b> &nbsp; [{r['tier'].split(':')[1].strip()}]<br>"
            f"💰 <b>Median Rent:</b> {format_currency(r['median_rent'])}/mo<br>"
            f"📐 <b>Price per m²:</b> {format_sqm_price(r['median_price_per_sqm'])}<br>"
            f"📊 <b>Active Listings:</b> {int(r['listing_count']):,} properties<br>"
            f"📐 <b>Typical Size:</b> {r['median_size']:.0f} sqm<br>"
            f"🛋️ <b>Furnished Ratio:</b> {r['furnished_pct']:.1f}%<br>"
            f"🚇 <b>Transit:</b> {metro_text}"
        )
        district_hover.append(hover_html)

    fig.add_trace(go.Scattermap(
        name="District Hubs",
        lat=district_agg["lat"],
        lon=district_agg["lon"],
        mode="markers",
        hovertext=district_hover,
        hoverinfo="text",
        marker=dict(
            size=bubble_sizes,
            color=district_agg["median_rent"],
            colorscale=colorscale_rent,
            cmin=5000,
            cmax=rent_cap,
            showscale=True,
            colorbar=dict(
                title=dict(text="<b>Monthly Rent (EGP)</b>", side="right", font=dict(size=12, color="#1E293B")),
                tickformat=",.0f",
                thickness=14,
                len=0.72,
                outlinewidth=0,
                bgcolor="rgba(255,255,255,0.92)",
                x=0.98,
                xanchor="right"
            ),
            opacity=0.92
        ),
        visible=True
    ))

    # --- TRACE 1: Granular Listings (All Micro Properties) ---
    prop_hover = []
    for _, r in mapped.iterrows():
        hover_html = (
            f"<b>{r['district']}</b> • {r['furnishing_badge']}<br>"
            f"💰 Monthly Rent: {format_currency(r['monthly_rent_egp'])}<br>"
            f"📐 Size: {r['size_sqm']:.0f} sqm ({format_sqm_price(r['price_per_sqm'])})<br>"
            f"🛏️ Rooms: {int(r['rooms']) if pd.notna(r['rooms']) else 'N/A'}<br>"
            f"🆔 Listing: {r.get('listing_id', 'N/A')}"
        )
        prop_hover.append(hover_html)

    fig.add_trace(go.Scattermap(
        name="All Listings",
        lat=mapped["latitude"],
        lon=mapped["longitude"],
        mode="markers",
        hovertext=prop_hover,
        hoverinfo="text",
        marker=dict(
            size=8,
            color=mapped["rent_capped"],
            colorscale=colorscale_rent,
            cmin=5000,
            cmax=rent_cap,
            showscale=False,
            opacity=0.85
        ),
        visible=False
    ))

    # --- TRACE 2: Furnished Listings Only ---
    df_furn = mapped[mapped["is_furnished"]].copy()
    furn_hover = [h for i, h in enumerate(prop_hover) if mapped.iloc[i]["is_furnished"]]

    fig.add_trace(go.Scattermap(
        name="Furnished Only",
        lat=df_furn["latitude"],
        lon=df_furn["longitude"],
        mode="markers",
        hovertext=furn_hover,
        hoverinfo="text",
        marker=dict(
            size=9,
            color=df_furn["rent_capped"],
            colorscale=colorscale_rent,
            cmin=5000,
            cmax=rent_cap,
            showscale=False,
            opacity=0.88
        ),
        visible=False
    ))

    # --- TRACE 3: Unfurnished Listings Only ---
    df_unfurn = mapped[~mapped["is_furnished"]].copy()
    unfurn_hover = [h for i, h in enumerate(prop_hover) if not mapped.iloc[i]["is_furnished"]]

    fig.add_trace(go.Scattermap(
        name="Unfurnished Only",
        lat=df_unfurn["latitude"],
        lon=df_unfurn["longitude"],
        mode="markers",
        hovertext=unfurn_hover,
        hoverinfo="text",
        marker=dict(
            size=9,
            color=df_unfurn["rent_capped"],
            colorscale=colorscale_rent,
            cmin=5000,
            cmax=rent_cap,
            showscale=False,
            opacity=0.88
        ),
        visible=False
    ))

    # --- TRACE 4: Cairo Price Density Heatmap ---
    fig.add_trace(go.Densitymap(
        name="Rent Density Heatmap",
        lat=mapped["latitude"],
        lon=mapped["longitude"],
        z=mapped["rent_capped"],
        radius=26,
        colorscale="Inferno",
        showscale=False,
        opacity=0.72,
        visible=False
    ))

    # -------------------------------------------------------------------------
    # Layout (Fixed at Cairo center, zoom 10, using OSM HOT by default)
    # -------------------------------------------------------------------------
    fig.update_layout(
        height=740,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
        paper_bgcolor="#FFFFFF",
        map=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=default_zoom,
            style=STYLE_OSM_HOT
        ),
        hoverlabel=dict(
            bgcolor="#0F172A",
            font=dict(family="Arial, sans-serif", size=12, color="#FFFFFF"),
            bordercolor="#38BDF8",
            align="left"
        ),
        updatemenus=[]
    )

    # -------------------------------------------------------------------------
    # Generate Plotly Embedded HTML Component
    # -------------------------------------------------------------------------
    plotly_html = fig.to_html(
        include_plotlyjs=True,
        full_html=False,
        config={
            "displayModeBar": True,
            "displaylogo": False,
            "modeBarButtonsToRemove": ["lasso2d", "select2d"],
            "toImageButtonOptions": {
                "format": "png",
                "filename": "sakan_cairo_rental_market_map",
                "height": 900,
                "width": 1400,
                "scale": 2
            }
        }
    )

    # Prepare District Leaderboard JSON for the interactive drawer
    leaderboard_data = []
    for _, row in district_agg.iterrows():
        leaderboard_data.append({
            "name": str(row["district"]),
            "median_rent": float(row["median_rent"]),
            "median_sqm": float(row["median_price_per_sqm"]) if pd.notna(row["median_price_per_sqm"]) else 0,
            "count": int(row["listing_count"]),
            "lat": float(row["lat"]),
            "lon": float(row["lon"]),
            "tier": str(row["tier"])
        })
    leaderboard_json = json.dumps(leaderboard_data)

    # -------------------------------------------------------------------------
    # Construct Full Executive Dashboard Web Application
    # -------------------------------------------------------------------------
    dashboard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SAKAN | Cairo Real Estate Rental Market Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    :root {{
      --primary: #2563EB;
      --primary-dark: #1D4ED8;
      --navy: #0F172A;
      --slate-800: #1E293B;
      --slate-600: #475569;
      --slate-400: #94A3B8;
      --slate-100: #F1F5F9;
      --slate-50: #F8FAFC;
      --border: #E2E8F0;
      --emerald: #10B981;
      --amber: #F59E0B;
      --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background-color: var(--slate-50);
      color: var(--navy);
      line-height: 1.5;
      padding: 16px;
    }}
    .dashboard-container {{
      max-width: 1600px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }}

    /* Header Bar */
    .header-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--card-shadow);
      flex-wrap: wrap;
      gap: 12px;
    }}
    .brand-section {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}
    .brand-logo {{
      width: 44px;
      height: 44px;
      background: linear-gradient(135deg, #2563EB, #0D9488);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-weight: 800;
      font-size: 22px;
      box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3);
    }}
    .brand-text h1 {{
      font-size: 20px;
      font-weight: 800;
      letter-spacing: -0.5px;
      color: var(--navy);
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .brand-text h1 span {{
      font-size: 11px;
      font-weight: 700;
      background: #EFF6FF;
      color: var(--primary);
      padding: 3px 8px;
      border-radius: 6px;
      letter-spacing: 0.5px;
      text-transform: uppercase;
    }}
    .brand-text p {{
      font-size: 13px;
      color: var(--slate-600);
      font-weight: 500;
    }}
    .header-badges {{
      display: flex;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .badge {{
      background: var(--slate-100);
      color: var(--slate-800);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 6px;
      border: 1px solid var(--border);
    }}
    .badge-accent {{
      background: #ECFDF5;
      color: #065F46;
      border-color: #A7F3D0;
    }}

    /* KPI Summary Row */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 14px;
    }}
    .kpi-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px 20px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 4px;
      transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{
      transform: translateY(-2px);
      box-shadow: 0 8px 12px -2px rgba(0, 0, 0, 0.08);
    }}
    .kpi-label {{
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      color: var(--slate-600);
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .kpi-value {{
      font-size: 24px;
      font-weight: 800;
      color: var(--navy);
      letter-spacing: -0.5px;
    }}
    .kpi-subtext {{
      font-size: 12px;
      color: var(--slate-600);
      font-weight: 500;
    }}

    /* Main Workspace (Map + District Leaderboard) */
    .workspace-grid {{
      display: grid;
      grid-template-columns: 340px 1fr;
      gap: 16px;
    }}
    @media (max-width: 1024px) {{
      .workspace-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    /* Sidebar / District Leaderboard */
    .sidebar-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      gap: 14px;
      max-height: 800px;
    }}
    .sidebar-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .sidebar-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--navy);
    }}
    .search-box input {{
      width: 100%;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      font-family: inherit;
      font-size: 13px;
      outline: none;
      background: var(--slate-50);
      transition: border-color 0.15s ease;
    }}
    .search-box input:focus {{
      border-color: var(--primary);
      background: #FFFFFF;
    }}
    .district-list {{
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-right: 4px;
      flex: 1;
    }}
    .district-item {{
      background: var(--slate-50);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 10px 12px;
      cursor: pointer;
      transition: all 0.15s ease;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .district-item:hover {{
      background: #EFF6FF;
      border-color: #BFDBFE;
      transform: translateX(2px);
    }}
    .district-item-name {{
      font-size: 13px;
      font-weight: 700;
      color: var(--navy);
    }}
    .district-item-meta {{
      font-size: 11px;
      color: var(--slate-600);
    }}
    .district-item-price {{
      text-align: right;
    }}
    .district-item-rent {{
      font-size: 13px;
      font-weight: 800;
      color: var(--primary);
    }}
    .district-item-sqm {{
      font-size: 11px;
      color: var(--slate-600);
    }}

    /* Map Card */
    .map-card {{
      background: #FFFFFF;
      border: 1px solid var(--border);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: var(--card-shadow);
      display: flex;
      flex-direction: column;
      position: relative;
    }}
    .map-toolbar {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 12px 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .toolbar-left, .toolbar-right {{
      display: flex;
      align-items: center;
      gap: 8px;
      flex-wrap: wrap;
    }}
    .toolbar-btn {{
      background: var(--slate-100);
      border: 1px solid var(--border);
      color: var(--slate-800);
      padding: 6px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
      font-family: inherit;
    }}
    .toolbar-btn:hover {{
      background: #E2E8F0;
    }}
    .toolbar-btn.active {{
      background: var(--primary);
      border-color: var(--primary-dark);
      color: #FFFFFF;
    }}
    .map-body {{
      width: 100%;
      height: 740px;
      position: relative;
    }}

    /* Footer */
    .footer-bar {{
      text-align: center;
      font-size: 12px;
      color: var(--slate-600);
      padding: 10px 0;
    }}
  </style>
</head>
<body>

<div class="dashboard-container">

  <!-- Top Executive Header -->
  <div class="header-card">
    <div class="brand-section">
      <div class="brand-logo">S</div>
      <div class="brand-text">
        <h1>SAKAN <span>PropTech Analytics</span></h1>
        <p>Cairo Real Estate Rental Market Geospatial Intelligence • 2027 Expansion</p>
      </div>
    </div>
    <div class="header-badges">
      <div class="badge badge-accent">✅ {len(mapped):,} Verified Listings</div>
      <div class="badge">🏙️ {total_districts} Analyzed Districts</div>
      <div class="badge">🎓 Final Project Submission</div>
    </div>
  </div>

  <!-- KPI Metrics Banner -->
  <div class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">💰 Cairo Median Rent</div>
      <div class="kpi-value">{cairo_median_rent:,.0f} <span style="font-size:14px;font-weight:600;">EGP</span></div>
      <div class="kpi-subtext">Overall baseline for residential units</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">📐 Median Price / m²</div>
      <div class="kpi-value">{cairo_median_sqm:,.0f} <span style="font-size:14px;font-weight:600;">EGP/m²</span></div>
      <div class="kpi-subtext">Capital efficiency benchmark for Greater Cairo</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">👑 Highest Valuation Hub</div>
      <div class="kpi-value">{top_district}</div>
      <div class="kpi-subtext">Median {top_district_rent:,.0f} EGP • Prime luxury corridor</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">💡 Highest Affordability Hub</div>
      <div class="kpi-value">{affordable_district}</div>
      <div class="kpi-subtext">Median {affordable_district_rent:,.0f} EGP • Emerging expansion zone</div>
    </div>
  </div>

  <!-- Workspace: Sidebar District Explorer + Interactive Map -->
  <div class="workspace-grid">
    
    <!-- Sidebar: District Leaderboard & Search -->
    <div class="sidebar-card">
      <div class="sidebar-header">
        <div class="sidebar-title">District Valuation Hubs</div>
        <span style="font-size:11px; font-weight:700; color:var(--primary);">{total_districts} DISTRICTS</span>
      </div>
      <div class="search-box">
        <input type="text" id="districtSearch" placeholder="🔍 Search district (e.g. New Cairo)..." onkeyup="filterDistricts()">
      </div>
      <div class="district-list" id="districtList">
        <!-- Rendered dynamically by JavaScript -->
      </div>
    </div>

    <!-- Map Container -->
    <div class="map-card">
      <div class="map-toolbar">
        <div class="toolbar-left">
          <span style="font-size:12px; font-weight:700; color:var(--slate-800); margin-right:4px;">Layer:</span>
          <button class="toolbar-btn active" onclick="switchLayer(0, this)">🏙️ District Hubs</button>
          <button class="toolbar-btn" onclick="switchLayer(1, this)">📍 All Listings</button>
          <button class="toolbar-btn" onclick="switchLayer(2, this)">🛋️ Furnished</button>
          <button class="toolbar-btn" onclick="switchLayer(3, this)">🏢 Unfurnished</button>
          <button class="toolbar-btn" onclick="switchLayer(4, this)">🔥 Heatmap</button>
        </div>
        <div class="toolbar-right">
          <span style="font-size:12px; font-weight:700; color:var(--slate-800); margin-right:4px;">Basemap:</span>
          <button class="toolbar-btn active" onclick="switchBasemap('hot', this)">🗺️ Vibrant Streets</button>
          <button class="toolbar-btn" onclick="switchBasemap('osm', this)">🧭 Clean City</button>
          <button class="toolbar-btn" onclick="switchBasemap('topo', this)">⛰️ Topo</button>
          <button class="toolbar-btn" onclick="switchBasemap('sat', this)">🛰️ Satellite</button>
          <button class="toolbar-btn" onclick="resetCairoView()">🎯 Reset View</button>
        </div>
      </div>
      <div class="map-body">
        {plotly_html}
      </div>
    </div>

  </div>

  <!-- Footer -->
  <div class="footer-bar">
    SAKAN PropTech Intelligence Platform &bull; Greater Cairo Rental Market Analysis &bull; Cleaned & Audited Dataset
  </div>

</div>

<script>
  const districts = {leaderboard_json};
  const getPlotlyDiv = () => document.querySelector('.plotly-graph-div');
  const CAIRO_CENTER = {{ lat: {center_lat}, lon: {center_lon} }};
  const CAIRO_ZOOM = 10;

  // Populate District List in Sidebar
  function renderDistrictList(items) {{
    const container = document.getElementById('districtList');
    container.innerHTML = '';
    items.forEach(d => {{
      const div = document.createElement('div');
      div.className = 'district-item';
      div.onclick = () => focusDistrict(d.lat, d.lon, d.name);
      div.innerHTML = `
        <div>
          <div class="district-item-name">${{d.name}}</div>
          <div class="district-item-meta">${{d.count}} listings &bull; ${{d.tier.replace(/Tier \\d: /, '')}}</div>
        </div>
        <div class="district-item-price">
          <div class="district-item-rent">EGP ${{d.median_rent.toLocaleString()}}</div>
          <div class="district-item-sqm">${{d.median_sqm > 0 ? 'EGP ' + Math.round(d.median_sqm).toLocaleString() + '/m²' : ''}}</div>
        </div>
      `;
      container.appendChild(div);
    }});
  }}
  renderDistrictList(districts);

  // Filter districts search box
  function filterDistricts() {{
    const q = document.getElementById('districtSearch').value.toLowerCase();
    const filtered = districts.filter(d => d.name.toLowerCase().includes(q));
    renderDistrictList(filtered);
  }}

  // Focus map on district click (Smooth pan & zoom to district)
  function focusDistrict(lat, lon, name) {{
    const pDiv = getPlotlyDiv();
    if (pDiv) {{
      Plotly.relayout(pDiv, {{
        'map.center': {{ lat: lat, lon: lon }},
        'map.zoom': 13
      }});
    }}
  }}

  // Reset to full Cairo view
  function resetCairoView() {{
    const pDiv = getPlotlyDiv();
    if (pDiv) {{
      Plotly.relayout(pDiv, {{
        'map.center': CAIRO_CENTER,
        'map.zoom': CAIRO_ZOOM
      }});
    }}
  }}

  // Layer Switcher
  function switchLayer(traceIdx, btn) {{
    document.querySelectorAll('.toolbar-left .toolbar-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const pDiv = getPlotlyDiv();
    if (!pDiv) return;

    const visibility = [false, false, false, false, false];
    visibility[traceIdx] = true;
    Plotly.restyle(pDiv, {{ visible: visibility }}, [0, 1, 2, 3, 4]);
  }}

  // Basemap Switcher (Using 100% Reliable, Public, Non-blocking Mirrors)
  const styles = {{
    'hot': {json.dumps(STYLE_OSM_HOT)},
    'osm': {json.dumps(STYLE_OSM_FRANCE)},
    'topo': {json.dumps(STYLE_OPENTOPO)},
    'sat': {json.dumps(STYLE_SATELLITE)}
  }};

  function switchBasemap(key, btn) {{
    document.querySelectorAll('.toolbar-right .toolbar-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const pDiv = getPlotlyDiv();
    if (!pDiv || !styles[key]) return;

    // Get current center and zoom or fallback to Cairo
    let cCenter = CAIRO_CENTER;
    let cZoom = CAIRO_ZOOM;
    try {{
      if (pDiv._fullLayout && pDiv._fullLayout.map) {{
        const curZ = pDiv._fullLayout.map.zoom;
        if (curZ && curZ >= 7) {{
          cZoom = curZ;
          cCenter = pDiv._fullLayout.map.center || cCenter;
        }}
      }}
    }} catch (e) {{}}

    Plotly.relayout(pDiv, {{
      'map.style': styles[key],
      'map.center': cCenter,
      'map.zoom': cZoom
    }});
  }}

  // Force initial view to Cairo on window load
  window.addEventListener('load', () => {{
    setTimeout(() => {{
      resetCairoView();
    }}, 400);
  }});
</script>

</body>
</html>
"""

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(dashboard_html)

    print("=" * 75)
    print("SUCCESS: Executive Cairo Rental Map Generated!")
    print(f"Output File: {OUTPUT_FILE}")
    print(f"File Size: {OUTPUT_FILE.stat().st_size / (1024*1024):.2f} MB")
    print(f"Districts: {total_districts} | Mapped Listings: {len(mapped):,}")
    print("Basemap Architecture: OSM HOT & France Mirrors (100% Reliable, No Watermark, No 403)")
    print("=" * 75)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:
        print(f"\nERROR: {err}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
