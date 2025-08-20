import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from fastkml import kml
from shapely.geometry import shape
from io import BytesIO

st.set_page_config(page_title="Barangay Mapper", page_icon="📍", layout="wide")

st.title("📍 Barangay Mapper")

# Upload lat/long file
latlong_file = st.file_uploader("Upload CSV/Excel with latitude & longitude", type=["csv", "xlsx"])

# Upload barangay KML
kml_file = st.file_uploader("Upload Barangay Boundaries (KML)", type=["kml"])

if latlong_file and kml_file:
    # --- Load Lat/Long Data ---
    if latlong_file.name.endswith(".csv"):
        df = pd.read_csv(latlong_file)
    else:
        df = pd.read_excel(latlong_file)

    if not {"latitude", "longitude"}.issubset(df.columns):
        st.error("Uploaded file must contain 'latitude' and 'longitude' columns.")
        st.stop()

    st.subheader("Uploaded Lat/Long Data")
    st.dataframe(df.head())

    # Convert to GeoDataFrame
    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )

    # --- Parse KML into GeoDataFrame ---
    kml_text = kml_file.read().decode("utf-8")
    k = kml.KML()
    k.from_string(kml_text)

    features = []
    for document in k.features():
        for placemark in document.features():
            features.append({
                "name": placemark.name,
                "geometry": shape(placemark.geometry)
            })

    gdf_barangays = gpd.GeoDataFrame(features, crs="EPSG:4326")

    st.subheader("Barangay Boundaries from KML")
    st.write(gdf_barangays.head())

    # --- Spatial Join ---
    gdf_joined = gpd.sjoin(gdf_points, gdf_barangays, how="left", predicate="within")
    gdf_joined = gdf_joined.drop(columns=["index_right"])

    st.subheader("Joined Data (Points + Barangays)")
    st.dataframe(gdf_joined.head())

    # --- Download Buttons ---
    csv = gdf_joined.drop(columns="geometry").to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download as CSV", csv, "barangay_results.csv", "text/csv")

    geojson = gdf_joined.to_json()
    st.download_button("📥 Download as GeoJSON", geojson, "barangay_results.geojson", "application/json")
