import streamlit as st
import pandas as pd

# Sample guest list
guests = [
    {"name": "Anna Cruz", "table": 1},
    {"name": "Mark Santos", "table": 2},
    {"name": "Jenny Lopez", "table": 3},
    {"name": "Carlos Reyes", "table": 1},
    {"name": "Maria Gomez", "table": 2},
]

df = pd.DataFrame(guests)

st.title("🎉 Debut Table Finder")

# Search input
search_name = st.text_input("Enter your name:")

if search_name:
    # Case-insensitive partial match
    results = df[df["name"].str.contains(search_name, case=False, na=False)]
    
    if not results.empty:
        for _, row in results.iterrows():
            st.success(f"Hello **{row['name']}**, your table number is **{row['table']}** 🎂")
    else:
        st.warning("No match found. Please check your spelling.")
