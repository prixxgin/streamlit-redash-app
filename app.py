import streamlit as st
import pandas as pd
import requests
import altair as alt

# --- Load secrets from .streamlit/secrets.toml ---
REDASH_URL = st.secrets["redash"]["url"]
API_KEY = st.secrets["redash"]["api_key"]
QUERY_ID = st.secrets["redash"]["query_id"]

headers = {
    "Authorization": f"Key {API_KEY}"
}

st.title("📊 Redash Query Viewer")

@st.cache_data(ttl=300)
def run_query():
    exec_url = f"{REDASH_URL}/api/queries/{QUERY_ID}/results"
    r = requests.get(exec_url, headers=headers)
    if r.status_code == 200:
        data = r.json()["query_result"]["data"]["rows"]
        return pd.DataFrame(data)
    else:
        st.error("❌ Failed to run query.")
        return pd.DataFrame()

# --- Run query on load
df = run_query()

if df.empty:
    st.warning("No data returned from Redash.")
    st.stop()

# --- Filter: Manual input for tracking_id
if "tracking_id" in df.columns:
    tracking_input = st.text_input("🔍 Enter Tracking ID (partial or full)")
    if tracking_input:
        df = df[df["tracking_id"].astype(str).str.contains(tracking_input, case=False, na=False)]

# --- Show filtered results
st.dataframe(df)

# --- Chart: Count per Granular Status
if "granular_status" in df.columns:
    status_counts = df["granular_status"].value_counts().reset_index()
    status_counts.columns = ["granular_status", "count"]

    chart = alt.Chart(status_counts).mark_bar().encode(
        x=alt.X("granular_status:N", sort="-y"),
        y="count:Q",
        tooltip=["granular_status", "count"]
    ).properties(
        title="Granular Status Count"
    ).interactive()

    st.altair_chart(chart, use_container_width=True)
else:
    st.info("ℹ️ No 'granular_status' column found to plot.")

# --- Download CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, file_name="query_results.csv")
