import geopandas as gpd
from shapely.geometry import Point
import streamlit as st

# --- Load Barangay GeoJSON or Shapefile ---
@st.cache_data
def load_barangays(path="data/barangays.geojson"):
    try:
        barangays = gpd.read_file(path)
        # Ensure CRS is WGS84 (lat/lon)
        if barangays.crs is None or barangays.crs.to_string() != "EPSG:4326":
            barangays = barangays.to_crs(epsg=4326)
        return barangays
    except Exception as e:
        st.error(f"❌ Error loading barangay data: {e}")
        return None


def get_barangay_code(lat: float, lon: float, barangays: gpd.GeoDataFrame):
    """Return barangay info + PSGC code based on lat/lon."""
    if barangays is None or barangays.empty:
        return {"error": "Barangay shapefile not loaded or empty."}

    try:
        point = Point(lon, lat)
        match = barangays[barangays.contains(point)]

        if not match.empty:
            row = match.iloc[0]
            return {
                "Barangay": row.get("BRGY_NAME", "Unknown Barangay"),
                "Municipality": row.get("MUN_NAME", "Unknown Municipality"),
                "Province": row.get("PROV_NAME", "Unknown Province"),
                "PSGC_Code": row.get("PSGC_CODE", "Unknown Code")
            }
        else:
            return {"error": "No barangay found for this location."}
    except Exception as e:
        return {"error": f"Error: {e}"}


# --- Streamlit UI ---
st.title("📍 Barangay Code Finder (Offline)")

barangays = load_barangays("data/barangays.geojson")

lat = st.number_input("Enter Latitude", value=14.5995)
lon = st.number_input("Enter Longitude", value=120.9842)

if st.button("Get Barangay Code"):
    result = get_barangay_code(lat, lon, barangays)
    st.json(result)
