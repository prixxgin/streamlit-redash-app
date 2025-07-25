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

        # Column selection
        selected_columns = st.multiselect(
            "🔽 Select columns to display:",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if selected_columns:
            selected_df = df[selected_columns]
            st.subheader("📄 Selected Columns View")
            st.dataframe(selected_df, use_container_width=True, hide_index=True)

            # Choose group-by column
            group_by_col = st.selectbox(
                "📌 Choose column to group by:",
                options=selected_columns,
                index=0
            )

            # Choose which columns to sum
            numeric_options = selected_df.select_dtypes(include='number').columns.tolist()
            sum_columns = st.multiselect(
                "➕ Select numeric columns to sum:",
                options=[col for col in numeric_options if col != group_by_col]
            )

            if sum_columns:
                st.subheader(f"🧮 Sum View (Grouped by '{group_by_col}')")
                sum_df = selected_df.groupby(group_by_col)[sum_columns].sum().reset_index()
                st.dataframe(sum_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Please select at least one numeric column to sum.")
        else:
            st.info("☝️ Please select at least one column to view the data.")
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
