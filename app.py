import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# === Step 1: Load your barangay boundaries (converted from KML to GeoJSON) ===
# Make sure barangays.json is the GeoJSON version of your KML
barangay_gdf = gpd.read_file("barangays.json")

# Inspect columns to find the right barangay code column
print("Columns in barangay data:", barangay_gdf.columns)

# Example: assume the barangay code is stored in column 'BRGY_CODE'
barangay_code_col = "BRGY_CODE"   # change this if different

# === Step 2: Load your CSV with lat/long ===
df = pd.read_csv("input.csv")

# Ensure lat/long column names
lat_col = "latitude"
lon_col = "longitude"

# Convert DataFrame to GeoDataFrame
geometry = [Point(xy) for xy in zip(df[lon_col], df[lat_col])]
points_gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# === Step 3: Spatial join to find barangay ===
joined = gpd.sjoin(points_gdf, barangay_gdf[[barangay_code_col, "geometry"]], how="left", predicate="within")

# === Step 4: Save result ===
output = joined.drop(columns=["geometry", "index_right"])
output.to_csv("barangay_with_code.csv", index=False)

print("✅ barangay_with_code.csv has been generated.")
