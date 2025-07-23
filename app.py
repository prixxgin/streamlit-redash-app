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
        # Open the spreadsheet and specific worksheet
        spreadsheet = client.open("MyData")  # Replace with your spreadsheet name
        worksheet = spreadsheet.worksheet("raw")  # Replace with your sheet/tab name
        
        # Get all values and convert to DataFrame
        data = worksheet.get_all_values()
        df = pd.DataFrame(data[1:], columns=data[0])  # Use first row as header
        
        st.subheader("📄 Sheet: raw")
        st.dataframe(df)  # Display as interactive table
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
