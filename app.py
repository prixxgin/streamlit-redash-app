import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# -------------------------------
# 🎯 Page Setup
# -------------------------------
st.set_page_config(page_title="📍 Barangay Billing Tool", layout="wide")
st.title("📦 Barangay-Based Billing per Shipper")

# -------------------------------
# 📥 File Upload for pickups.csv
# -------------------------------
uploaded_file = st.file_uploader("📤 Upload Pickups CSV (lat, long, shipper)", type="csv")

if not uploaded_file:
    st.info("👆 Upload a CSV file with columns: `shipper`, `lat`, `long` to proceed.")
    st.stop()

# -------------------------------
# 📄 Load Other Local Files
# -------------------------------
try:
    rate_df = pd.read_csv("rate_card.csv")
    barangay_gdf = gpd.read_file("barangays.geojson")
except Exception as e:
    st.error(f"❌ Error loading rate card or geojson: {e}")
    st.stop()

# -------------------------------
# 🔄 Load Uploaded Pickup Data
# -------------------------------
try:
    pickup_df = pd.read_csv(uploaded_file)
    required_columns = {'shipper', 'lat', 'long'}
    if not required_columns.issubset(pickup_df.columns):
        st.error(f"❌ Uploaded file must contain columns: {required_columns}")
        st.stop()
except Exception as e:
    st.error(f"❌ Failed to read uploaded CSV: {e}")
    st.stop()

# -------------------------------
# 🧭 Geospatial Matching
# -------------------------------
pickup_df = pickup_df.copy()
pickup_df['geometry'] = pickup_df.apply(lambda row: Point(float(row['long']), float(row['lat'])), axis=1)
pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')

try:
    matched = gpd.sjoin(
        pickup_gdf,
        barangay_gdf[['barangay_name', 'geometry']],
        how='left',
        predicate='within'
    )
except Exception as e:
    st.error(f"❌ Spatial join failed: {e}")
    st.stop()

# -------------------------------
# 💰 Merge with Rate Card
# -------------------------------
try:
    matched = matched.merge(rate_df, left_on='barangay_name', right_on='barangay', how='left')
except Exception as e:
    st.error(f"❌ Merging rate card failed: {e}")
    st.stop()

# -------------------------------
# 📊 Billing Summary
# -------------------------------
billing = matched.groupby('shipper', as_index=False)['rate'].sum()

# -------------------------------
# 📋 Display Billing Table
# -------------------------------
st.subheader("📋 Billing Summary")
st.dataframe(billing, use_container_width=True)

st.download_button(
    label="⬇️ Download Billing CSV",
    data=billing.to_csv(index=False),
    file_name="billing_summary.csv",
    mime="text/csv"
)

# -------------------------------
# 🗺️ Pickup Map
# -------------------------------
with st.expander("📍 View Pickup Map"):
    map_df = pickup_df.rename(columns={'lat': 'latitude', 'long': 'longitude'})
    st.map(map_df[['latitude', 'longitude']])

# -------------------------------
# 📑 Matched Pickup Details
# -------------------------------
with st.expander("📑 Matched Pickup Data"):
    st.dataframe(matched[['shipper', 'lat', 'long', 'barangay_name', 'rate']], use_container_width=True)
