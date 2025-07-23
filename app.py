import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials

st.title('Google Sheets Dashboard')

st.write('This app connects to Google Sheets and displays data.')

# Instructions for user to upload credentials
st.info('Upload your Google Service Account JSON credentials to connect to Google Sheets.')

uploaded_file = st.file_uploader('Upload credentials JSON', type='json')

if uploaded_file:
    # Use the uploaded credentials to connect to Google Sheets
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        eval(uploaded_file.getvalue().decode()), scope)
    client = gspread.authorize(creds)
    st.success('Connected to Google Sheets!')
    # Example: List all spreadsheets
    spreadsheets = client.openall()
    st.write('Your spreadsheets:')
    for sheet in spreadsheets:
        st.write(sheet.title)
else:
    st.warning('Please upload your credentials JSON to proceed.') 
