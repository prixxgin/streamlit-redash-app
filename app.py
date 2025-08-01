import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

st.set_page_config(page_title="📍 Barangay Billing Tool", layout="wide")
st.title("📦 Barangay-Based Billing per Shipper")

# Load Data with Debugging
def load_data_safe():
    try:
        pickups = pd.read_csv("pickups.csv")
        st.success("✅ pickups.csv loaded")
    except Exception as e:
        st.error(f"❌ Error loading pickups.csv: {e}")
        st.stop()

    try:
        rates = pd.read_csv("rate_card.csv")
        st.success("✅ rate_card.csv loaded")
    except Exception as e:
        st.error(f"❌ Error loading rate_card.csv: {e}")
        st.stop()

    try:
        zones = gpd.read_file("barangays.geojson")
        st.success("✅ barangays.geojson loaded")
    except Exception as e:
        st.error(f"❌ Error loading barangays.geojson: {e}")
        st.stop()

    return pickups, rates, zones

pickup_df, rate_df, barangay_gdf = load_data_safe()

# Check required columns
required_cols = ['shipper', 'lat', 'long']
missing = [col for col in required_cols if col not in pickup_df.columns]
if missing:
    st.error(f"❌ Missing columns in pickups.csv: {missing}")
    st.stop()

# Convert to GeoDataFrame
try:
    pickup_df['geometry'] = pickup_df.apply(lambda row: Point(float(row['long']), float(row['lat'])), axis=1)
    pickup_gdf = gpd.GeoDataFrame(pickup_df, geometry='geometry', crs='EPSG:4326')
except Exception as e:
    st.error(f"❌ Error creating geometry: {e}")
    st.stop()

# Spatial Join
try:
    matched = gpd.sjoin(
        pickup_gdf,
        barangay_gdf[['barangay_name', 'geometry']],
        how='left',
        predicate='within'
    )
    st.success("✅ Spatial join successful")
except Exception as e:
    st.error(f"❌ Spatial join failed: {e}")
    st.stop()

# Merge Rate Card
try:
    matched = matched.merge(rate_df, left_on='barangay_name', right_on='barangay', how='left')
except Exception as e:
    st.error(f"❌ Rate card merge failed: {e}")
    st.stop()

# Calculate Billing
billing = matched.groupby('shipper', as_index=False)['rate'].sum()

# Show Results
st.subheader("📋 Billing Summary")
st.dataframe(billing)

# Download
st.download_button("⬇️ Download CSV", billing.to_csv(index=False), "billing_summary.csv")

# Optional Map
with st.expander("📍 Pickup Map"):
    st.map(pickup_df[['lat', 'long']])

# Optional Matched Data
with st.expander("📑 Matched Details"):
    st.dataframe(matched[['shipper', 'lat', 'long', 'barangay_name', 'rate']])
