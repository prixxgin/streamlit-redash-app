import geopandas as gpd
from shapely.geometry import Point

# Load barangay shapefile (download from PhilGIS or PSA)
barangays = gpd.read_file("barangays.geojson")  # or .shp

def get_barangay_code(lat, lon):
    point = Point(lon, lat)
    match = barangays[barangays.contains(point)]
    if not match.empty:
        name = match.iloc[0]['BRGY_NAME']
        code = match.iloc[0]['PSGC_CODE']
        return {"barangay": name, "code": code}
    return None

# Example
print(get_barangay_code(14.5995, 120.9842))  # e.g. Manila
