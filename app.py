import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("📊 Google Sheets Data Viewer")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ✅ Load credentials from secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)

# ✅ Authorize client
client = gspread.authorize(creds)

# ✅ Open your sheet
SHEET_NAME = "raw"  # 👈 use the **tab name** in your spreadsheet
sheet = client.open(SHEET_NAME).sheet1

# ✅ Read and show data
data = sheet.get_all_records()
st.write("📄 Sheet Contents:")
st.dataframe(data)
