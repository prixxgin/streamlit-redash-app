import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from io import BytesIO

st.set_page_config(page_title="Lat-Long Processor", page_icon="🌍", layout="wide")

st.title("🌍 Lat/Long File Processor")

# Upload file
uploaded_file = st.file_uploader("Upload CSV/Excel with latitude & longitude columns", type=["csv", "xlsx"])

if uploaded_file:
    # Detect file type
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("Preview of Uploaded Data")
    st.dataframe(df.head())

    # Check for lat/lon columns
    if {"latitude", "longitude"}.issubset(df.columns):
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(
            df,
            geometry=gpd.points_from_xy(df.longitude, df.latitude),
            crs="EPSG:4326"  # WGS84
        )

        # Example transformation: convert to UTM
        gdf_utm = gdf.to_crs(epsg=32651)  # Example: UTM Zone 51N (Philippines)
        gdf["x"] = gdf_utm.geometry.x
        gdf["y"] = gdf_utm.geometry.y

        st.subheader("Processed Data with Projected Coordinates")
        st.dataframe(gdf.head())

        # Download as CSV
        csv = gdf.drop(columns="geometry").to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Processed CSV",
            data=csv,
            file_name="processed_latlong.csv",
            mime="text/csv"
        )

        # Download as GeoJSON
        geojson = gdf.to_json()
        st.download_button(
            label="📥 Download GeoJSON",
            data=geojson,
            file_name="processed_latlong.geojson",
            mime="application/json"
        )

    else:
        st.error("Uploaded file must contain 'latitude' and 'longitude' columns.")
