import pandas as pd
from shapely.geometry import Point, shape
from fastkml import kml

# === Load KML ===
with open("barangays.kml", "rb") as f:
    doc = f.read()

k = kml.KML()
k.from_string(doc)

# Traverse KML features
polygons = []
for feature in list(k.features()):
    for subfeature in feature.features():
        for placemark in subfeature.features():
            geom = shape(placemark.geometry.__geo_interface__)
            brgy_code = placemark.extended_data.elements[0].data[0].value  # adjust key
            polygons.append((geom, brgy_code))

# === Load CSV ===
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
