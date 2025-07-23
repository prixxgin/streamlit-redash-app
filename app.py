import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# --- Page config ---
st.set_page_config(page_title="📊 Google Sheets Live Dashboard", layout="wide")

# --- Title ---
st.title("📊 Google Sheets Live Dashboard")

# --- Set up Google Sheets API client ---
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    st.secrets["gsheets"],
    scope
)
client = gspread.authorize(creds)

# --- Open the Google Sheet and 'raw' worksheet tab ---
SHEET_URL = st.secrets["gsheets"]["sheet_url"]
spreadsheet = client.open_by_url(SHEET_URL)
worksheet = spreadsheet.worksheet("raw")  # 👈 Target sheet tab

# --- Load data from sheet into DataFrame ---
@st.cache_data(ttl=60)  # Refresh every 60 seconds
def load_data():
    data = worksheet.get_all_records()
    return pd.DataFrame(data)

df = load_data()

# --- Display Data ---
st.subheader("📄 Live Data from 'raw' Tab")
st.dataframe(df, use_container_width=True)

# --- Optional Chart (First Numeric Column Only) ---
numeric_cols = df.select_dtypes(include="number").columns.tolist()

if numeric_cols:
    st.subheader("📈 Line Chart (First Numeric Column)")
    st.line_chart(df[numeric_cols[0]])

# --- Footer ---
st.caption("🔁 Data updates every 60 seconds (when reloaded). Click Rerun to manually refresh.")
