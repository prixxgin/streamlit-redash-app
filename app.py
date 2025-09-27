import streamlit as st
import pandas as pd

# Sample guest list
guests = [
    {"name": "BLESILDA LUMAQUE ", "table": 1},
    {"name": "MARK ANGELO LUMAQUE", "table": 1},
    {"name": "MARVIE LUMAQUE", "table": 1},
    {"name": "MITCHELL  SUAREZ", "table": 1},
    {"name": "SOFIA GABRIEL SUAREZ", "table": 1},
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
