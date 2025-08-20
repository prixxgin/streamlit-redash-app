import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape
from io import BytesIO

# Try importing fastkml if available
try:
    from fastkml import kml
    HAS_FASTKML = True
except ImportError:
    HAS_FASTKML = False

st.set_page_config(page_title="Barangay Mapper", page_icon="📍", layout="wide")
st.title("📍 Barangay Mapper")

# Upload lat/long file
latlong_file = st.file_uploader("Upload CSV/Excel with latitude & longitude", type=["csv", "xlsx"])

# Upload barangay boundaries (KML, GeoJSON, or Shapefile ZIP)
boundary_file = st.file_uploader("Upload Barangay Boundaries (KML / GeoJSON / Shapefile ZIP)", 
                                 type=["kml", "geojson", "json", "zip", "shp"])

if latlong_file and boundary_file:
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

    gdf_points = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df["longitude"], df["latitude"]),
        crs="EPSG:4326"
    )

    # --- Load Boundaries ---
    if boundary_file.name.endswith(".kml"):
        if not HAS_FASTKML:
            st.error("KML support requires `fastkml`. Please add `fastkml==0.12` in requirements.txt.")
            st.stop()

        kml_text = boundary_file.read().decode("utf-8")
        k = kml.KML()
        k.from_string(kml_text)

        features = []
        for document in k.features():
            for placemark in document.features():
                features.append({
                    "name": placemark.name,
                    "geometry": shape(placemark.geometry)
                })

        gdf_boundaries = gpd.GeoDataFrame(features, crs="EPSG:4326")

    else:
        # Handle GeoJSON / Shapefile
        gdf_boundaries = gpd.read_file(boundary_file)

    st.subheader("Uploaded Boundaries")
    st.write(gdf_boundaries.head())

    # --- Spatial Join ---
    gdf_joined = gpd.sjoin(gdf_points, gdf_boundaries, how="left", predicate="within")
    gdf_joined = gdf_joined.drop(columns=["index_right"])

    st.subheader("Joined Data (Points + Boundaries)")
    st.dataframe(gdf_joined.head())

    # --- Download ---
    csv = gdf_joined.drop(columns="geometry").to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download as CSV", csv, "results.csv", "text/csv")

    geojson = gdf_joined.to_json()
    st.download_button("📥 Download as GeoJSON", geojson, "results.geojson", "application/json")
