import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Load barangay boundaries (GeoJSON / Shapefile with barangay codes)
@st.cache_data
def load_barangays():
    barangays = gpd.read_file("barangays.geojson")  # Replace with your dataset
    barangays = barangays.to_crs(epsg=4326)
    return barangays

st.title("Barangay Code Finder from CSV")

uploaded_file = st.file_uploader("Upload a CSV file with Latitude and Longitude", type=["csv"])

if uploaded_file:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    st.write("📄 Uploaded Data:", df.head())

    # Check if lat/lon columns exist
    if {"latitude", "longitude"}.issubset(df.columns):
        barangays = load_barangays()

        # Convert lat/lon to Point
        gdf_points = gpd.GeoDataFrame(
            df,
            geometry=[Point(xy) for xy in zip(df["longitude"], df["latitude"])],
            crs="EPSG:4326"
        )

        # Spatial join (find which barangay each point belongs to)
        joined = gpd.sjoin(gdf_points, barangays, how="left", predicate="within")

        # Extract result
        df["barangay_name"] = joined["brgy_name"]   # Adjust column names
        df["barangay_code"] = joined["brgy_code"]

        st.success("Barangay codes added ✅")
        st.write(df.head())

        # Allow download
        st.download_button(
            label="⬇ Download CSV with Barangay Codes",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="barangay_results.csv",
            mime="text/csv"
        )
    else:
        st.error("CSV must have 'latitude' and 'longitude' columns")
