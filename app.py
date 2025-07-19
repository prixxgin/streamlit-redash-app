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

@st.cache_data
def get_saved_queries():
    url = f"{REDASH_URL}/api/queries"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        st.error("Failed to fetch saved queries.")
        return []

st.title("📊 Redash Query Explorer")

queries = get_saved_queries()
if not queries:
    st.stop()

# Query selection
query_options = {q["name"]: q["id"] for q in queries}
query_name = st.selectbox("Select a Query", list(query_options.keys()))
selected_query_id = query_options[query_name]

if st.button("Run Query"):
    with st.spinner("Running query..."):
        exec_url = f"{REDASH_URL}/api/queries/{selected_query_id}/results"
        r = requests.get(exec_url, headers=headers)
        if r.status_code == 200:
            data = r.json()["query_result"]["data"]["rows"]
            df = pd.DataFrame(data)

            if df.empty:
                st.warning("No data returned from this query.")
            else:
                st.success("Query executed successfully!")
                st.dataframe(df)

                # --- Chart: Count per Granular Status ---
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
                    st.info("No 'granular_status' column found to plot.")

                # --- CSV Download ---
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Download CSV", csv, file_name="query_results.csv")
        else:
            st.error("Failed to run query.")
