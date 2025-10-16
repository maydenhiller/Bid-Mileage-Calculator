import streamlit as st
import pandas as pd
import requests

# Load Mapbox token from Streamlit secrets
MAPBOX_TOKEN = st.secrets["mapbox"]["token"]

# Hard-coded office coordinates (lat, lon) for Crescent, OK
# Replace with exact coordinates of your office if needed
OFFICE_COORDS = (35.8239, -97.5920)

# Calculate driving distance using Mapbox Directions API
def get_drive_distance(start, end):
    coords = f"{start[1]},{start[0]};{end[1]},{end[0]}"
    url = f"https://api.mapbox.com/directions/v5/mapbox/driving/{coords}"
    params = {
        "access_token": MAPBOX_TOKEN,
        "overview": "false",
        "geometries": "geojson"
    }
    response = requests.get(url, params=params).json()
    if "routes" not in response or not response["routes"]:
        return None
    meters = response["routes"][0]["distance"]
    miles = meters / 1609.344
    return round(miles, 2)

# Parse coordinate string "lat, lon"
def parse_coords(coord_str):
    coord_str = str(coord_str).replace("°", "").strip()
    lat, lon = map(float, coord_str.split(","))
    return lat, lon

# Streamlit UI
st.title("📍 Bid Mileage Calculator")

st.markdown("Enter coordinates manually OR upload a CSV/XLSX with columns: "
            "`Line Name`, `Launcher Coordinates`, `Receiver Coordinates`.")

launcher_input = st.text_area("Launcher Coordinates (e.g. 45.490665, -118.416460)")
receiver_input = st.text_area("Receiver Coordinates (e.g. 45.929377, -119.409545)")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

# Manual input logic
if launcher_input and receiver_input:
    try:
        launcher_coords = parse_coords(launcher_input)
        receiver_coords = parse_coords(receiver_input)

        dist_to_launcher = get_drive_distance(OFFICE_COORDS, launcher_coords)
        dist_to_receiver = get_drive_distance(OFFICE_COORDS, receiver_coords)

        if dist_to_launcher is None or dist_to_receiver is None:
            st.error("Could not calculate one or both distances.")
        else:
            furthest = max(dist_to_launcher, dist_to_receiver)
            st.success(f"🏁 Furthest Distance from Office: {furthest} miles")

    except Exception as e:
        st.error(f"Error parsing coordinates: {e}")

# File upload logic
if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        distances = []
        for _, row in df.iterrows():
            try:
                launcher = parse_coords(row["Launcher Coordinates"])
                receiver = parse_coords(row["Receiver Coordinates"])
                d1 = get_drive_distance(OFFICE_COORDS, launcher)
                d2 = get_drive_distance(OFFICE_COORDS, receiver)
                if d1 is None or d2 is None:
                    distances.append(None)
                else:
                    distances.append(max(d1, d2))
            except Exception:
                distances.append(None)

        df["Furthest Distance (mi)"] = distances
        st.dataframe(df)

        # Downloadable CSV
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download Results CSV",
                           data=csv_bytes,
                           file_name="bid_mileage.csv",
                           mime="text/csv")

    except Exception as e:
        st.error(f"File processing error: {e}")
