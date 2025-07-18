import streamlit as st
import pandas as pd
import requests
import altair as alt  # 🔁 Add this import

# --- Load secrets from .streamlit/secrets.toml ---
REDASH_URL = st.secrets["redash"]["url"]
API_KEY = st.secrets["redash"]["api_key"]

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
            st.success("Query successful!")
            st.dataframe(df)

            # 🔻 Chart Section (Optional: Only render if numeric columns exist)
            numeric_columns = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_columns:
                x_axis = st.selectbox("Choose X-axis", df.columns)
                y_axis = st.selectbox("Choose Y-axis", numeric_columns)
                chart = alt.Chart(df).mark_bar().encode(
                    x=alt.X(x_axis, sort="-y"),
                    y=y_axis,
                    tooltip=[x_axis, y_axis]
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("No numeric data to plot.")

            # CSV Export
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download as CSV", csv, file_name="result.csv")
        else:
            st.error("Query execution failed.")
