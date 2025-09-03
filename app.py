import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Cache barangay file
@st.cache_data
def load_barangays(file_path="barangays.geojson"):
    barangays = gpd.read_file(file_path)
    barangays = barangays.to_crs(epsg=4326)

    # Detect column names dynamically
    name_col, code_col = None, None
    for col in barangays.columns:
        col_lower = col.lower()
        if "brgy" in col_lower and "name" in col_lower:
            name_col = col
        if "psgc" in col_lower or "code" in col_lower:
            code_col = col

    # If not found, just pick first two non-geometry columns
    non_geom_cols = [c for c in barangays.columns if c != "geometry"]
    if not name_col and len(non_geom_cols) > 0:
        name_col = non_geom_cols[0]
    if not code_col and len(non_geom_cols) > 1:
        code_col = non_geom_cols[1]

    return barangays, name_col, code_col

st.title("📍 Barangay Code Finder from CSV")

uploaded_file = st.file_uploader("Upload a CSV file with Latitude and Longitude", type=["csv"])

if uploaded_file:
    # Load CSV
    df = pd.read_csv(uploaded_file)
    st.write("✅ Uploaded Data Preview:", df.head())

    # Check required columns
    if {"latitude", "longitude"}.issubset(df.columns):
        barangays, name_col, code_col = load_barangays()

        # Convert CSV points to GeoDataFrame
        gdf_points = gpd.GeoDataFrame(
            df,
            geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])],
            crs="EPSG:4326"
        )

        # Spatial join
        joined = gpd.sjoin(gdf_points, barangays, how="left", predicate="within")

        # Assign barangay info
        df["barangay_name"] = joined[name_col]
        df["barangay_code"] = joined[code_col]

        st.success("Barangay codes added ✅")
        st.write(df.head())

        # Download button
        st.download_button(
            label="⬇ Download CSV with Barangay Codes",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="barangay_results.csv",
            mime="text/csv"
        )

        st.info(f"Detected columns → Barangay Name: `{name_col}`, Barangay Code: `{code_col}`")

    else:
        st.error("❌ CSV must have 'latitude' and 'longitude' columns")
