import streamlit as st
import pandas as pd
from io import BytesIO

st.title("📦 ASN Pickup Week Checker")

# 📄 Downloadable CSV Template
template_data = {
    "pickup_week": ["7/20/2025"],
    "pickup_hub_id": [1051],
    "pickup_hub_name": ["FM Pasay"],
    "shipper_id": [5867715],
    "shipper_name": ["G-XChange Inc.(GCash)"],
    "Total_orders": [14437],
    "Week": [30]
}
template_df = pd.DataFrame(template_data)
template_buffer = BytesIO()
template_df.to_csv(template_buffer, index=False)
st.download_button(
    label="⬇ Download CSV Template",
    data=template_buffer.getvalue(),
    file_name="pickups_template.csv",
    mime="text/csv"
)

# 📤 File Upload
uploaded_file = st.file_uploader("Upload your pickups.csv", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)

    # ✅ Add ASN Pickup Column
    df["has_asn"] = df["pickup_hub_name"].str.contains("ASN", case=False, na=False)
    weeks_with_asn = df.loc[df["has_asn"], "Week"].unique()
    df["ASN PICKUP"] = df["Week"].isin(weeks_with_asn).astype(int)

    st.subheader("Processed Data")
    st.dataframe(df)

    # 📥 Download processed file
    output_buffer = BytesIO()
    df.to_csv(output_buffer, index=False)
    st.download_button(
        label="⬇ Download Processed CSV",
        data=output_buffer.getvalue(),
        file_name="processed_pickups.csv",
        mime="text/csv"
    )
