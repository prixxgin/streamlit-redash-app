import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("📊 Google Sheets Data Viewer")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
client = gspread.authorize(creds)

# ✅ Sheet name must match exactly what you see in Google Sheets
SHEET_NAME = "raw"

try:
    sheet = client.open(SHEET_NAME).sheet1
    data = sheet.get_all_records()
    st.dataframe(data)
except Exception as e:
    st.error(f"❌ Error: {e}")
