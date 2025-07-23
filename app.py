import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title('Google Sheets Dashboard')

st.write('This app connects to Google Sheets and displays data.')

# Use Streamlit secrets for credentials
if "gsheets" in st.secrets:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gsheets"], scope)
    client = gspread.authorize(creds)
    st.success('Connected to Google Sheets!')

    # Example: List all spreadsheets
    try:
        spreadsheet = client.open("Your Google Sheet Name")  # Replace with your actual sheet name
        st.write(f"Opened spreadsheet: {spreadsheet.title}")
        worksheet_list = spreadsheet.worksheets()
        st.write("Worksheets:", [ws.title for ws in worksheet_list])
    except Exception as e:
        st.error(f"Error opening spreadsheet: {e}")
else:
    st.warning('Google Sheets credentials not found in Streamlit secrets.') 
