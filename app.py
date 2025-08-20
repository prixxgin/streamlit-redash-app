import streamlit as st
import subprocess
import sys
import platform
import pandas as pd

st.title("🛠️ GeoPython Environment Setup Checker")

# Python version
st.subheader("Python Version")
st.write(sys.version)

# Platform info
st.subheader("Platform")
st.write(platform.platform())

# Installed packages
st.subheader("Installed Packages")
result = subprocess.run([sys.executable, "-m", "pip", "list"], capture_output=True, text=True)
packages = [line.split() for line in result.stdout.splitlines()[2:]]
df = pd.DataFrame(packages, columns=["Package", "Version"])
st.dataframe(df)

# Check critical packages
st.subheader("Environment Validation")
required = {
    "numpy": "1.26.4",
    "geopandas": "0.10.2",
    "shapely": "2.0.3",
    "pyproj": "3.6.1",
    "Fiona": "1.9.5",
    "GDAL": "3.8.4",
    "Rtree": "1.2.0",
    "basemap": "1.3.8"
}

for pkg, ver in required.items():
    match = df[df["Package"].str.lower() == pkg.lower()]
    if not match.empty and match["Version"].values[0] == ver:
        st.success(f"{pkg} ✅ {ver}")
    else:
        st.error(f"{pkg} ❌ (Expected {ver})")
