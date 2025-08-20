import geopandas as gpd
from shapely.geometry import Point

# Load your KML file (make sure you installed 'fiona' and 'geopandas')
# Some KMLs need the driver specified
barangays = gpd.read_file("barangays.kml", driver="KML")

def get_barangay_code(lat, lon):
    # GeoPandas uses (lon, lat) not (lat, lon)
    point = Point(lon, lat)
    
    # Check which polygon contains the point
    result = barangays[barangays.geometry.contains(point)]
    
    if not result.empty:
        return {
            "barangay_name": result.iloc[0].get("Name"),   # or the column name from your KML
            "barangay_code": result.iloc[0].get("PSGC"),  # depends on your KML schema
        }
    return None

# Example: test point
lat, lon = 14.5896, 120.9811
print(get_barangay_code(lat, lon))
