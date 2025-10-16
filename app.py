import geopandas as gpd
from shapely.geometry import Point
import streamlit as st

# --- Load barangay shapefile or geojson ---
@st.cache_data
def load_barangays(path="barangays.geojson"):
    try:
        barangays = gpd.read_file(path)
        # Ensure coordinate reference system is WGS84
        if barangays.crs is None or barangays.crs.to_string() != "EPSG:4326":
            barangays = barangays.to_crs(epsg=4326)
        return barangays
    except Exception as e:
        st.error(f"Error loading barangay data: {e}")
        return None


def get_barangay_code(lat: float, lon: float, barangays: gpd.GeoDataFrame):
    """
    Given a latitude and longitude, return the barangay name and PSGC code.
    """
    if barangays is None or barangays.empty:
        return {"error": "Barangay shapefile not loaded or empty."}

    try:
        point = Point(lon, lat)
        match = barangays[barangays.contains(point)]
        if not match.empty:
            result = match.iloc[0]
            brgy_name = result.get("BRGY_NAME", "Unknown Barangay")
            psgc_code = result.get("PSGC_CODE", "Unknown Code")
            city_name = result.get("MUN_NAME", "Unknown Municipality")
            province_name = result.get("PROV_NAME", "Unknown Province")
            return {
                "Barangay": brgy_name,
                "Municipality": city_name,
                "Province": province_name,
                "PSGC_Code": psgc_code
            }
        else:
            return {"error": "No barangay found for this location."}
    except Exception as e:
        return {"error": f"Error determining barangay: {e}"}
