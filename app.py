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
        spreadsheet = client.open("MyData")
        worksheet = spreadsheet.worksheet("raw")

        data = worksheet.get_all_values()
        df = pd.DataFrame(data)

        # Use first row as header
        df.columns = df.iloc[0]
        df = df.drop(df.index[0])

        # Let user pick which columns to show
        selected_columns = st.multiselect(
            "🧩 Select columns to display:",
            options=df.columns.tolist(),
            default=df.columns.tolist()  # preselect all by default
        )

        # Filter the dataframe based on selection
        filtered_df = df[selected_columns]

        st.subheader("📄 Filtered Sheet View")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
