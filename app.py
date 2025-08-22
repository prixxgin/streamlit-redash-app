import pandas as pd
import fiona
from shapely.geometry import shape, Point

# Load barangay polygons from GeoJSON or KML
polygons = []
with fiona.open("barangays.json") as src:
    for feature in src:
        geom = shape(feature["geometry"])
        brgy_code = feature["properties"]["BRGY_CODE"]  # adjust key
        polygons.append((geom, brgy_code))

# Load CSV
df = pd.read_csv("input.csv")

def get_barangay_code(lat, lon):
    point = Point(lon, lat)
    for geom, code in polygons:
        if geom.contains(point):
            return code
    return None

df["barangay_code"] = df.apply(lambda row: get_barangay_code(row["latitude"], row["longitude"]), axis=1)

df.to_csv("barangay_with_code.csv", index=False)
print("✅ barangay_with_code.csv generated")
