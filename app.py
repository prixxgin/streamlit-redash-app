import streamlit as st
import pandas as pd
import gspread
import seaborn as sns
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials

st.set_page_config(page_title="📍 Location Workload Heatmap", layout="wide")
st.title("📍 Workload Volume by Location and Date")

# Authenticate using Streamlit secrets
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
client = gspread.authorize(credentials)

# Open the sheet
sheet_name = "MyData"  # Replace with your Google Sheet name
worksheet = client.open(sheet_name).worksheet("raw3")

# Load data into DataFrame
data = pd.DataFrame(worksheet.get_all_records())
data['Date'] = pd.to_datetime(data['Date'])

# Sidebar filters
st.sidebar.header("🔎 Filters")
task_types = data['Task Type'].unique()
selected_task = st.sidebar.selectbox("Select Task Type", options=task_types)

filtered_data = data[data['Task Type'] == selected_task]

# Pivot for heatmap
pivot_df = filtered_data.pivot_table(
    index='Location',
    columns='Date',
    values='Task Count',
    aggfunc='sum',
    fill_value=0
)

# Draw heatmap
st.subheader(f"📊 Heatmap for Task Type: {selected_task}")
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot_df, annot=True, fmt='d', cmap='YlGnBu', ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)
