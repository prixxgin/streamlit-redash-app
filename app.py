import streamlit as st
import pandas as pd
import gspread
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from oauth2client.service_account import ServiceAccountCredentials

# Streamlit page config
st.set_page_config(page_title="📍 Location Workload Heatmap", layout="wide")
st.title("📍 Workload Volume by Location and Date")

# === 🔐 Google Sheets Authentication ===
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gsheets"], scope)
client = gspread.authorize(credentials)

# === 📄 Load Data from Google Sheets ===
sheet_name = "MyData"  # Change to your actual sheet name
worksheet = client.open(sheet_name).worksheet("raw3")  # Change to correct tab name
data = pd.DataFrame(worksheet.get_all_records())

# === 🧹 Data Preparation ===
try:
    data['Date'] = pd.to_datetime(data['Date'])
except Exception as e:
    st.error(f"❌ Date parsing error: {e}")
    st.stop()

# Check required columns
required_cols = {'Date', 'Location', 'Task Type', 'Task Count'}
if not required_cols.issubset(data.columns):
    st.error(f"Missing required columns. Expected: {required_cols}")
    st.stop()

# === 🧭 Sidebar Filters ===
st.sidebar.header("🔎 Filters")
task_types = sorted(data['Task Type'].dropna().unique())
selected_task = st.sidebar.selectbox("Select Task Type", options=task_types)

# === 🔍 Filtered Data ===
filtered_data = data[data['Task Type'] == selected_task]

# === 📊 Pivot Table for Heatmap ===
pivot_df = filtered_data.pivot_table(
    index='Location',
    columns='Date',
    values='Task Count',
    aggfunc='sum',
    fill_value=0
)

# === 🔥 Draw Heatmap ===
st.subheader(f"📊 Heatmap for Task Type: {selected_task}")
fig, ax = plt.subplots(figsize=(12, 6))
sns.heatmap(pivot_df, annot=True, fmt='d', cmap='YlGnBu', ax=ax, linewidths=.5, linecolor='gray')
plt.xticks(rotation=45)
plt.ylabel("Location")
plt.xlabel("Date")
st.pyplot(fig)
