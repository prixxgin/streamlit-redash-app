import streamlit as st
import pandas as pd
from fastkml import kml
from shapely.geometry import Point, Polygon

# Placeholder for KML data
barangay_polygons = []

def load_barangay_kml(kml_file_path):
    """Loads barangay boundary data from a KML file."""
    global barangay_polygons
    barangay_polygons = []
    with open(kml_file_path, 'rb') as kml_file:
        doc = kml.KML()
        doc.from_string(kml_file.read())
        
        # Assuming a simple KML structure with one Document and Placemarks directly under it
        for feature in doc.features():
            if isinstance(feature, kml.Document):
                for sub_feature in feature.features():
                    if isinstance(sub_feature, kml.Placemark):
                        if sub_feature.geometry is not None and sub_feature.geometry.geom_type == 'Polygon':
                            # Convert KML polygon to shapely Polygon
                            coords = list(sub_feature.geometry.exterior.coords)
                            polygon = Polygon(coords)
                            barangay_polygons.append({
                                'name': sub_feature.name,
                                'polygon': polygon,
                                # You might need to adjust this based on where 'barangay_code' is in your KML
                                'barangay_code': sub_feature.name # Placeholder, adjust as needed
                            })
            elif isinstance(feature, kml.Placemark):
                if feature.geometry is not None and feature.geometry.geom_type == 'Polygon':
                    coords = list(feature.geometry.exterior.coords)
                    polygon = Polygon(coords)
                    barangay_polygons.append({
                        'name': feature.name,
                        'polygon': polygon,
                        'barangay_code': feature.name # Placeholder, adjust as needed
                    })
    return barangay_polygons

def get_barangay_code(latitude, longitude):
    """Matches lat/long to a barangay polygon and returns the barangay code."""
    point = Point(longitude, latitude) # Shapely Point expects (longitude, latitude)
    for barangay in barangay_polygons:
        if barangay['polygon'].contains(point):
            return barangay['barangay_code']
    return "Not Found"

def process_csv(df):
    """Processes the input DataFrame and appends the barangay_code column."""
    df['barangay_code'] = df.apply(lambda row: get_barangay_code(row['latitude'], row['longitude']), axis=1)
    return df

st.title("Barangay Code Lookup from Lat/Long")

st.sidebar.header("Upload KML Data")
kml_file = st.sidebar.file_uploader("Upload KML File", type=["kml"])

if kml_file is not None:
    # Save the uploaded KML file temporarily
    with open("uploaded_barangay.kml", "wb") as f:
        f.write(kml_file.getbuffer())
    
    st.sidebar.success("KML file uploaded successfully!")
    
    # Load KML data
    try:
        load_barangay_kml("uploaded_barangay.kml")
        st.sidebar.write(f"Loaded {len(barangay_polygons)} barangay polygons.")
    except Exception as e:
        st.sidebar.error(f"Error loading KML: {e}")

st.header("Upload CSV File")
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write("Original CSV Preview:", df.head())

    if st.button("Process CSV"):
        if not barangay_polygons:
            st.error("Please upload and load KML data first.")
        else:
            with st.spinner('Processing CSV...'):
                enriched_df = process_csv(df.copy())
                st.success("CSV processed successfully!")
                st.write("Enriched CSV Preview:", enriched_df.head())

                csv_output = enriched_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Enriched CSV",
                    data=csv_output,
                    file_name="output_with_barangay.csv",
                    mime="text/csv",
                )
else:
    st.info("Upload a CSV file to begin.")
