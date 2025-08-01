import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

st.set_page_config(page_title="📍 Barangay Billing Tool", layout="wide")
st.title("📦 Barangay-Based Billing per Shipper")

# --- Load Files ---
try:
    pickup_df = pd.read_csv("pickups.csv")
    rate_df = pd.read_csv("rate_card.csv")
    barangay_gdf = gpd.read_file("barangays.geojson")
except Exception as e:
    st.error(f"⚠️ Error loading files: {e}")
    st.stop()

# --- Convert pickups to GeoDataFrame ---
pickup_df['geometry'] = pickup_df.apply(lambda row: Point(row['long'], row['lat']), axis=1)
pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')

# --- Spatial Join ---
matched = gpd.sjoin(pickup_gdf, barangay_gdf[['barangay_name', 'geometry']], how='left', predicate='within')

# --- Merge Rate Card ---
matched = matched.merge(rate_df, left_on='barangay_name', right_on='barangay', how='left')

# --- Billing Summary ---
billing = matched.groupby('shipper')['rate'].sum().reset_index()

# --- UI Output ---
st.subheader("📋 Billing Summary per Shipper")
st.dataframe(billing, use_container_width=True)

st.download_button(
    label="⬇️ Download Billing as CSV",
    data=billing.to_csv(index=False),
    file_name="billing_summary.csv",
    mime="text/csv"
)

with st.expander("📍 View Pickup Map"):
    st.map(pickup_df[['lat', 'long']])

with st.expander("📑 Raw Matched Data"):
    st.dataframe(matched[['shipper', 'lat', 'long', 'barangay_name', 'rate']], use_container_width=True)
