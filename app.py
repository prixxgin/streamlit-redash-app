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

        # Use the first row as header
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)

        # Ensure proper data types (convert numeric columns if possible)
        df = df.apply(pd.to_numeric, errors='ignore')

        # Multi-select dropdown with column headers
        selected_columns = st.multiselect(
            "🔽 Select one or more columns to display:",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if selected_columns:
            st.subheader("📄 Selected Columns View")
            st.dataframe(df[selected_columns], use_container_width=True, hide_index=True)

            # Aggregation based on the first column
            first_col = df.columns[0]
            st.subheader(f"🧮 Aggregated View (Grouped by '{first_col}')")

            # Example aggregation: count of rows per group + mean for numeric columns
            aggregated_df = df.groupby(first_col).agg(['count', 'mean']).reset_index()

            st.dataframe(aggregated_df, use_container_width=True, hide_index=True)
        else:
            st.info("☝️ Please select at least one column to view the data.")
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
