import requests
import pandas as pd
import streamlit as st

psgc = pd.read_csv("psgc_barangays.csv")

def get_barangay_code(lat, lon, api_key):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lon}&key={api_key}"
    res = requests.get(url).json()

    # Debug output to inspect what we got
    st.write("Raw API response:", res)

    # Defensive check — make sure keys exist
    if res.get('status') != 'OK':
        return {"error": f"API returned status: {res.get('status')}"}

    components = res['results'][0].get('address_components', [])
    brgy, city, province = None, None, None

    for c in components:
        types = c.get('types', [])
        if "sublocality_level_1" in types:
            brgy = c.get('long_name')
        elif "locality" in types:
            city = c.get('long_name')
        elif "administrative_area_level_2" in types:
            province = c.get('long_name')

    if not brgy:
        return {"error": "Barangay not found in address components."}

    match = psgc[
        (psgc['Barangay'].str.contains(brgy, case=False, na=False)) &
        (psgc['Municipality'].str.contains(city or "", case=False, na=False))
    ]

    if not match.empty:
        return match.iloc[0].to_dict()
    return {"error": "Barangay not found in PSGC table."}
