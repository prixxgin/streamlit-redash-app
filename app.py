import streamlit as st
import pandas as pd
import requests
import altair as alt

# --- Load Redash config from .streamlit/secrets.toml ---
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
        st.error(f"❌ Failed to run query. Status code: {r.status_code}")
        st.text(f"Response: {r.text}")
        return pd.DataFrame()

# --- Run query
df = run_query()

if df.empty:
    st.warning("No data returned from Redash.")
    st.stop()

# --- Display table
st.dataframe(df)

# --- Chart: Count per Granular Status (if exists)
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

# --- CSV download
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("📥 Download CSV", csv, file_name="query_results.csv")
