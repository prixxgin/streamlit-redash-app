import streamlit as st
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
import plotly.express as px

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

        # Use first row as header
        df.columns = df.iloc[0]
        df = df.drop(df.index[0]).reset_index(drop=True)

        # Convert numeric-like columns
        df = df.apply(pd.to_numeric, errors='ignore')

        # Select columns to display
        selected_columns = st.multiselect(
            "🔽 Select columns to display:",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if selected_columns:
            selected_df = df[selected_columns]
            st.subheader("📄 Selected Columns View")
            st.dataframe(selected_df, use_container_width=True, hide_index=True)

            # ✅ MULTI group-by selection
            group_by_cols = st.multiselect(
                "📌 Choose one or more columns to group by:",
                options=df.columns.tolist()
            )

            # Columns to sum — all available
            sum_columns = st.multiselect(
                "➕ Select one or more columns to sum:",
                options=[col for col in df.columns if col not in group_by_cols]
            )

            if group_by_cols and sum_columns:
                # Validate sum columns are numeric
                non_numeric_cols = [
                    col for col in sum_columns
                    if not pd.api.types.is_numeric_dtype(df[col])
                ]

                if non_numeric_cols:
                    st.error(
                        f"❌ The following columns are not numeric and cannot be summed: {', '.join(non_numeric_cols)}"
                    )
                else:
                    st.subheader(f"🧮 Sum View (Grouped by {', '.join(group_by_cols)})")
                    sum_df = df.groupby(group_by_cols)[sum_columns].sum().reset_index()
                    st.dataframe(sum_df, use_container_width=True, hide_index=True)

                    # ✅ Charting options
                    st.subheader("📊 Graph Representation")

                    chart_type = st.selectbox(
                        "📍 Choose a chart type:",
                        ["Bar", "Line", "Area", "Scatter"]
                    )

                    x_axis = st.selectbox(
                        "➡️ Select X-axis (must be one of the group-by columns):",
                        options=group_by_cols
                    )

                    y_axis = st.selectbox(
                        "⬆️ Select Y-axis (must be one of the summed columns):",
                        options=sum_columns
                    )

                    # Render chart based on selection
                    if chart_type == "Bar":
                        fig = px.bar(sum_df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")
                    elif chart_type == "Line":
                        fig = px.line(sum_df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")
                    elif chart_type == "Area":
                        fig = px.area(sum_df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")
                    elif chart_type == "Scatter":
                        fig = px.scatter(sum_df, x=x_axis, y=y_axis, title=f"{chart_type} Chart")

                    st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("ℹ️ Please select at least one column to group by and one column to sum.")
        else:
            st.info("☝️ Please select at least one column to view the data.")
    except Exception as e:
        st.error(f"❌ Error reading spreadsheet: {e}")
else:
    st.warning('⚠️ Google Sheets credentials not found in Streamlit secrets.')
