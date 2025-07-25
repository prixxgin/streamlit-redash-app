import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

st.title('📊 Google Sheets Dashboard')
st.write('This app connects to Google Sheets and displays data from the "raw" sheet.')

# Use Streamlit secrets for credentials
if "gsheets" in st.secrets:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
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

        # Convert possible numeric columns
        df = df.apply(pd.to_numeric, errors='ignore')

        # Multi-select column selection
        selected_columns = st.multiselect(
            "🔽 Select one or more columns to display:",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if selected_columns:
            selected_df = df[selected_columns]
            st.subheader("📄 Selected Columns View")
            st.dataframe(selected_df, use_container_width=True, hide_index=True)

            # Aggregation using the first selected column
            first_col = selected_columns[0]
            st.subheader(f"🧮 Sum View (Grouped by '{first_col}')")

            # Identify numeric columns to sum (excluding the group column)
            numeric_cols = selected_df.select_dtypes(include='number').columns.tolist()
            numeric_cols = [col for col in numeric_cols if col != first_col]

            if numeric_cols:
                sum_df = selected_df.groupby(first_col)[numeric_cols].sum().reset_index()
                st.dataframe(sum_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ No numeric columns selected for summing.")
        else:
            st.info("☝️ Please select at least one column to view the data.")
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
