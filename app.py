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
# 📥 Load Data (with error handling)
# -------------------------------
def load_data():
    try:
        pickups = pd.read_csv("pickups.csv")
        rates = pd.read_csv("rate_card.csv")
        zones = gpd.read_file("barangays.geojson")
        return pickups, rates, zones
    except Exception as e:
        st.error(f"❌ Error loading files: {e}")
        st.stop()

pickup_df, rate_df, barangay_gdf = load_data()

# -------------------------------
# 🛠️ Validate and Prepare Data
# -------------------------------
required_columns = {'shipper', 'lat', 'long'}
if not required_columns.issubset(pickup_df.columns):
    st.error(f"❌ pickups.csv must contain columns: {required_columns}")
    st.stop()

pickup_df = pickup_df.copy()
pickup_df['geometry'] = pickup_df.apply(lambda row: Point(float(row['long']), float(row['lat'])), axis=1)
pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')

# -------------------------------
# 🧭 Spatial Join: Point in Barangay Polygon
# -------------------------------
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
# 📊 Billing Summary per Shipper
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
# 🗺️ Map of Pickups
# -------------------------------
with st.expander("📍 View Pickup Map"):
    map_df = pickup_df.rename(columns={'lat': 'latitude', 'long': 'longitude'})
    st.map(map_df[['latitude', 'longitude']])

# -------------------------------
# 📑 Raw Matched Data (Optional)
# -------------------------------
with st.expander("📑 Matched Pickup Details"):
    st.dataframe(matched[['shipper', 'lat', 'long', 'barangay_name', 'rate']], use_container_width=True)
