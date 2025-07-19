import streamlit as st
import pandas as pd
import requests
import time
import altair as alt

# --- Load Redash config from secrets ---
REDASH_URL = st.secrets["redash"]["url"]
API_KEY = st.secrets["redash"]["api_key"]
QUERY_ID = st.secrets["redash"]["query_id"]

headers = {
    "Authorization": f"Key {API_KEY}"
}

st.title("📊 Redash Query Viewer")

@st.cache_data(ttl=300)
def run_query():
    # Step 1: Trigger the query to run
    refresh_url = f"{REDASH_URL}/api/queries/{QUERY_ID}/refresh"
    response = requests.post(refresh_url, headers=headers)

    if response.status_code != 200:
        st.error(f"❌ Failed to trigger query. Status code: {response.status_code}")
        st.text(f"Response: {response.text}")
        return pd.DataFrame()

    job_id = response.json()["job"]["id"]

    # Step 2: Poll for query completion
    job_url = f"{REDASH_URL}/api/jobs/{job_id}"
    max_retries = 30
    for _ in range(max_retries):
        job_response = requests.get(job_url, headers=headers).json()
        status = job_response["job"]["status"]

        if status == 3:
            # Query succeeded
            result_id = job_response["job"]["query_result_id"]
            result_url = f"{REDASH_URL}/api/query_results/{result_id}"
            result_response = requests.get(result_url, headers=headers).json()
            data = result_response["query_result"]["data"]["rows"]
            return pd.DataFrame(data)
        elif status == 4:
            st.error("❌ Query failed to execute.")
            return pd.DataFrame()
        else:
            time.sleep(1)  # wait 1 second before polling again

    st.error("⏰ Query timed out.")
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
