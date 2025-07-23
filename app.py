import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.title('📊 Google Sheets Dashboard')
st.write('This app connects to Google Sheets and displays data from the "raw" sheet.')

# Use Streamlit secrets for credentials
if "gsheets" in st.secrets:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["gsheets"], scope)
    client = gspread.authorize(creds)
    st.success('✅ Connected to Google Sheets!')

    try:
        # Open the spreadsheet and worksheet
        spreadsheet = client.open("MyData")
        worksheet = spreadsheet.worksheet("raw")
        
        # Get all data from the sheet (including duplicate headers)
        data = worksheet.get_all_values()
        df = pd.DataFrame(data)  # Do not use headers

        st.subheader("📄 Sheet: raw (with original headers)")
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
