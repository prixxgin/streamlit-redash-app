import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title("📊 Google Sheets Data Viewer")

# Define the scopes
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Load credentials from Streamlit secrets
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)

# Authorize the client
client = gspread.authorize(creds)

# Open the sheet
SHEET_NAME = "Your Sheet Name Here"  # Change this to your Google Sheet title
sheet = client.open(SHEET_NAME).sheet1

# Fetch all records
data = sheet.get_all_records()

# Display in Streamlit
st.write("📄 Sheet Contents:")
st.dataframe(data)
