import streamlit as st
import pandas as pd
import requests
import time

# --- Redash Configuration ---
REDASH_URL = "https://redash-ph.ninjavan.co"  # Replace with your Redash URL
API_KEY = st.secrets["NwAJMjjxsgVpHH6fATD7dajZrL2yXECJCmvqmHMY"]

headers = {
    "Authorization": f"Key {API_KEY}"
}

@st.cache_data
def get_saved_queries():
    url = f"{REDASH_URL}/api/queries"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        st.error("Failed to fetch saved queries.")
        return []

st.title("🔍 Redash Query Viewer")

queries = get_saved_queries()
if not queries:
    st.stop()

query_options = {q["ZARA Delivery Report"]: q["2724"] for q in queries}
query_name = st.selectbox("Select a Query", list(query_options.keys()))
selected_query_id = query_options[query_name]

if st.button("Run Query"):
    with st.spinner("Running query..."):
        exec_url = f"{REDASH_URL}/api/queries/{selected_query_id}/results"
        r = requests.get(exec_url, headers=headers)
        if r.status_code == 200:
            data = r.json()["query_result"]["data"]["rows"]
            df = pd.DataFrame(data)
            st.success("Query successful!")
            st.dataframe(df)

            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download as CSV", csv, file_name="result.csv")
        else:
            st.error("Query execution failed.")
