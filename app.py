import streamlit as st
import requests

# Fixed office location
OFFICE_ADDRESS = "28630 East 760 Road Crescent Ok 73028"
MAPBOX_TOKEN = "YOUR_MAPBOX_ACCESS_TOKEN"

# Geocode office address to coordinates
@st.cache_data
def geocode_address(address):
    url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{address}.json"
    params = {"access_token": MAPBOX_TOKEN}
    response = requests.get(url, params=params).json()
    coords = response["features"][0]["geometry"]["coordinates"]
    return coords[1], coords[0]  # lat, lon

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
    meters = response["routes"][0]["distance"]
    miles = meters / 1609.344
    return round(miles, 2)

# Parse coordinate string
def parse_coords(coord_str):
    coord_str = coord_str.replace("°", "").strip()
    lat, lon = map(float, coord_str.split(","))
    return lat, lon

# UI
st.title("📍 Bid Mileage Calculator")

launcher_input = st.text_area("Launcher Coordinates (e.g. 45.490665°, -118.416460°)")
receiver_input = st.text_area("Receiver Coordinates (e.g. 45.929377°, -119.409545°)")
tracker_count = st.number_input("Number of Trackers", min_value=1, step=1)

if st.button("Calculate Mileage"):
    try:
        office_coords = geocode_address(OFFICE_ADDRESS)
        launcher_coords = parse_coords(launcher_input)
        receiver_coords = parse_coords(receiver_input)

        dist_to_launcher = get_drive_distance(office_coords, launcher_coords)
        dist_to_receiver = get_drive_distance(office_coords, receiver_coords)

        furthest = max(dist_to_launcher, dist_to_receiver)
        total_mileage = round(furthest * tracker_count, 2)

        st.success(f"🏁 Furthest Distance: {furthest} miles")
        st.info(f"📦 Total Bid Mileage: {total_mileage} miles")

    except Exception as e:
        st.error(f"Error: {e}")
