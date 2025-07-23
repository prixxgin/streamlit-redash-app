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
        
        # Get all data
        data = worksheet.get_all_values()
        df = pd.DataFrame(data)

        # Use the first row as column headers and remove it from data
        df.columns = df.iloc[0]
        df = df[1:].reset_index(drop=True)

        st.subheader("📄 Sheet: raw (without row & column numbers)")
        st.dataframe(df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
