import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="📊 Live GSheet Dashboard", layout="wide")

# --- Auto refresh every 60 seconds ---
st_autorefresh(interval=60 * 1000, key="auto_refresh")

# --- Title
st.title("📊 Google Sheets Live Dashboard")

# --- Setup GSheet credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
client = gspread.authorize(creds)

# --- Open the 'raw' sheet tab
SHEET_URL = st.secrets["gsheets"]["sheet_url"]
spreadsheet = client.open_by_url(SHEET_URL)
worksheet = spreadsheet.worksheet("raw")  # 👈 Use the 'raw' tab

# --- Convert to DataFrame
@st.cache_data(ttl=60)  # Refreshes every 60 seconds
def load_data():
    records = worksheet.get_all_records()
    return pd.DataFrame(records)

df = load_data()

# --- Display
st.subheader("📄 Sheet Data (raw tab)")
st.dataframe(df, use_container_width=True)

# --- Optional Chart
if not df.empty:
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if numeric_cols:
        st.subheader("📈 Chart (first numeric column)")
        st.line_chart(df[numeric_cols[0]])

st.caption("⏱️ Auto
