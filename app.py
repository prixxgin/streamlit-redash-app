import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# Page setup
st.set_page_config(page_title="📍 Barangay Billing Tool", layout="wide")
st.title("📦 Barangay-Based Billing per Shipper")

# Load Data
@st.cache_data
def load_data():
    try:
        pickups = pd.read_csv("pickups.csv")
        rates = pd.read_csv("rate_card.csv")
        zones = gpd.read_file("barangays.geojson")
        return pickups, rates, zones
    except Exception as e:
        st.error(f"❌ Failed to load files: {e}")
        st.stop()

pickup_df, rate_df, barangay_gdf = load_data()

# Convert pickups to GeoDataFrame
pickup_df['geometry'] = pickup_df.apply(lambda row: Point(row['long'], row['lat']), axis=1)
pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')

# Spatial Join: match lat/long to barangay polygons
matched = gpd.sjoin(
    pickup_gdf,
    barangay_gdf[['barangay_name', 'geometry']],
    how='left',
    predicate='within'
)

# Merge with Rate Card
matched = matched.merge(rate_df, left_on='barangay_name', right_on='barangay', how='left')

# Calculate Billing
billing = matched.groupby('shipper', as_index=False)['rate'].sum()

# UI - Billing Table
st.subheader("📋 Billing Summary per Shipper")
st.dataframe(billing, use_container_width=True)

# Download button
st.download_button(
    label="⬇️ Download Billing CSV",
    data=billing.to_csv(index=False),
    file_name="billing_summary.csv",
    mime="text/csv"
)

# UI - Optional Map
with st.expander("📍 View Pickup Map"):
    st.map(pickup_df[['lat', 'long']])

# UI - Optional Raw Data
with st.expander("📑 Matched Pickup Details"):
    st.dataframe(matched[['shipper', 'lat', 'long', 'barangay_name', 'rate']], use_container_width=True)
