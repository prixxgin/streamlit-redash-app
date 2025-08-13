import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="ASN Pickup Checker", layout="wide")
st.title("📦 ASN Pickup Checker")

# Downloadable template
template_df = pd.DataFrame({
    "week": [1, 1, 2, 2],
    "pickup_hub_name": ["Manila ASN Hub", "Quezon City", "Cebu Hub", "Cebu ASN Point"]
})

csv_template = template_df.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download CSV Template",
    data=csv_template,
    file_name="pickups_template.csv",
    mime="text/csv"
)

# File uploader
uploaded_file = st.file_uploader("Upload pickups.csv", type=["csv"])

if uploaded_file:
    # Read uploaded CSV
    df = pd.read_csv(uploaded_file)

    # Ensure required columns exist
    if "week" in df.columns and "pickup_hub_name" in df.columns:
        # Create helper flag
        df["has_asn"] = df["pickup_hub_name"].str.contains("ASN", case=False, na=False)

        # Identify weeks containing ASN
        weeks_with_asn = df.loc[df["has_asn"], "week"].unique()

        # Create ASN PICKUP column
        df["ASN PICKUP"] = df["week"].apply(lambda w: "Yes" if w in weeks_with_asn else "No")

        # Drop helper column
        df.drop(columns=["has_asn"], inplace=True)

        # Display results
        st.subheader("Processed Data")
        st.dataframe(df)

        # Prepare downloadable output
        output = BytesIO()
        df.to_csv(output, index=False)
        st.download_button(
            label="💾 Download Processed CSV",
            data=output.getvalue(),
            file_name="pickups_with_asn.csv",
            mime="text/csv"
        )
    else:
        st.error("CSV must contain 'week' and 'pickup_hub_name' columns.")
