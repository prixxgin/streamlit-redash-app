import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

st.title("Barangay Finder")
st.write("Upload barangay boundaries (KML/GeoJSON/Shapefile) and lat-long CSV to map barangays.")

# --- Upload boundary file ---
boundary_file = st.file_uploader(
    "Upload boundary file (KML, GeoJSON, or Shapefile as .zip)", type=["kml", "geojson", "zip"]
)

# --- Upload coordinates file ---
latlong_file = st.file_uploader("Upload CSV with 'latitude' and 'longitude' columns", type="csv")

if boundary_file and latlong_file:
    # Load boundaries
    if boundary_file.name.endswith(".kml"):
        try:
            from fastkml import kml
        except ImportError:
            st.error("KML support requires `fastkml`. Please add `fastkml` to requirements.txt")
            st.stop()

        k = kml.KML()
        k.from_string(boundary_file.read())
        features = list(k.features())
        document = list(features[0].features())
        placemarks = list(document[0].features())

        data = []
        for pm in placemarks:
            geom = pm.geometry
            name = pm.name
            data.append({"name": name, "geometry": geom})

        barangays = gpd.GeoDataFrame(data, crs="EPSG:4326")

    elif boundary_file.name.endswith(".geojson"):
        barangays = gpd.read_file(boundary_file)

    elif boundary_file.name.endswith(".zip"):
        # For shapefile, user must upload a zipped shapefile (.shp, .shx, .dbf, .prj together)
        import tempfile, zipfile, os

        with tempfile.TemporaryDirectory() as tmpdir:
            with zipfile.ZipFile(boundary_file, "r") as z:
                z.extractall(tmpdir)
                shp_files = [f for f in os.listdir(tmpdir) if f.endswith(".shp")]
                if not shp_files:
                    st.error("No .shp file found in the uploaded ZIP.")
                    st.stop()
                barangays = gpd.read_file(os.path.join(tmpdir, shp_files[0]))

    else:
        st.error("Unsupported boundary file format")
        st.stop()

    # Load lat/long data
    df = pd.read_csv(latlong_file)
    if not {"latitude", "longitude"}.issubset(df.columns):
        st.error("CSV must have 'latitude' and 'longitude' columns")
        st.stop()

    points = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326"
    )

    # Spatial join
    joined = gpd.sjoin(points, barangays, how="left", predicate="within")

    # Show results
    st.subheader("Results")
    st.dataframe(joined[["latitude", "longitude", "name"]])

    # Download results
    csv = joined[["latitude", "longitude", "name"]].to_csv(index=False)
    st.download_button("Download Results CSV", data=csv, file_name="barangay_results.csv", mime="text/csv")
