import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# === Load barangay zone boundaries (GeoJSON) ===
barangay_gdf = gpd.read_file("barangays.geojson")

# === Load pickup data ===
pickup_df = pd.read_csv("pickups.csv")
pickup_df['geometry'] = pickup_df.apply(lambda row: Point(row['long'], row['lat']), axis=1)
pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')

# === Spatial Join: Match pickups to barangay polygons ===
joined = gpd.sjoin(pickup_gdf, barangay_gdf[['barangay_name', 'geometry']], how='left', predicate='within')

# === Load rate card and merge ===
rate_card = pd.read_csv("rate_card.csv")
joined = joined.merge(rate_card, left_on='barangay_name', right_on='barangay', how='left')

# === Calculate billing per shipper ===
bills = joined.groupby('shipper')['rate'].sum().reset_index()

# === Export result ===
bills.to_csv("billing_summary.csv", index=False)

print("✅ Billing summary generated: billing_summary.csv")
