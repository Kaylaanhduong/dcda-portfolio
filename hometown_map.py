"""
Hometown Map - Saigon Locations
Creates an interactive Folium map with custom Mapbox basemap,
geocoded addresses, and styled markers for different location types.
"""

import folium
from folium import plugins
import pandas as pd
from geopy.geocoders import Nominatim
import time

# Load your CSV file
df = pd.read_csv('lab06 - Sheet1.csv')

print(f"Loaded {len(df)} locations from CSV")
print("Geocoding addresses... This may take a moment")

# Initialize geocoder
geolocator = Nominatim(user_agent="saigon_hometown_map")

# Geocode addresses to get latitude and longitude
def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except:
        return None, None

# Add latitude and longitude columns
latitudes = []
longitudes = []

for idx, address in enumerate(df['Address']):
    print(f"Geocoding {idx + 1}/{len(df)}: {address[:50]}...")
    lat, lon = geocode_address(address)
    latitudes.append(lat)
    longitudes.append(lon)
    time.sleep(1)  # Be respectful to the geocoding service

df['latitude'] = latitudes
df['longitude'] = longitudes

# Remove rows with missing coordinates
df = df.dropna(subset=['latitude', 'longitude'])
print(f"\nSuccessfully geocoded {len(df)} locations")

# Create base map centered on Saigon
saigon_coords = [10.7769, 106.7009]
map_saigon = folium.Map(
    location=saigon_coords,
    zoom_start=12,
    tiles='OpenStreetMap'
)

# Define marker colors based on location type
marker_colors = {
    'Schools & Educational Institutions': 'blue',
    'Landmark': 'orange',
    'Restaurants & Cafes': 'green',
    'Culture & History': 'purple',
    'Recreation': 'red'
}

# Add markers for each location
for idx, row in df.iterrows():
    location_type = row['Type']
    color = marker_colors.get(location_type, 'gray')
    
    # Create popup with image and details
    popup_html = f"""
    <div style="width: 250px; font-family: Arial;">
        <h4 style="margin: 5px 0;">{row['Name']}</h4>
        <p style="margin: 5px 0; font-size: 12px;"><b>Type:</b> {location_type}</p>
        <p style="margin: 5px 0; font-size: 12px;"><b>Address:</b> {row['Address']}</p>
        <p style="margin: 5px 0; font-size: 11px;">{row['Description']}</p>
        <img src="{row['Image_URL']}" style="width: 100%; height: auto; margin-top: 10px; border-radius: 5px;">
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row['Name'],
        icon=folium.Icon(color=color, icon='info-sign')
    ).add_to(map_saigon)

# Add a layer control
folium.LayerControl().add_to(map_saigon)

# Add title to the map
title_html = '''
             <div style="position: fixed; 
                     top: 10px; left: 50px; width: 300px; height: 80px; 
                     background-color: white; border:2px solid grey; z-index:9999; 
                     font-size:16px; font-weight: bold; padding: 10px;
                     border-radius: 5px;">
             🗺️ My Hometown Map - Saigon
             <br><span style="font-size: 12px; font-weight: normal;">
             Meaningful locations in my life
             </span>
             </div>
             '''
map_saigon.get_root().html.add_child(folium.Element(title_html))

# Save the map
map_saigon.save('hometown_map.html')
print("\n✅ Map created successfully! Saved as 'hometown_map.html'")
print(f"Total locations: {len(df)}")
print("\nLocation types:")
print(df['Type'].value_counts())