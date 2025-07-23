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
    spreadsheets = client.openall()
    st.write('Your spreadsheets:')
    for sheet in spreadsheets:
        st.write(sheet.title)
else:
    st.warning('Google Sheets credentials not found in Streamlit secrets.') 
