"""
Hometown Map - Saigon Locations
Creates an interactive Folium map with custom Mapbox basemap,
geocoded addresses, and styled markers for different location types.
"""

import folium
from folium import plugins
import pandas as pd
import requests
import time

# Mapbox credentials
MAPBOX_ACCESS_TOKEN = "pk.eyJ1Ijoia2F5bGFhbmhkdW9uZyIsImEiOiJjbWx0cXJoZnIwMzduM2duNXRxbWgzYXRqIn0.pDLb-dh5YY3pO4C4LUqW6g"
MAPBOX_STYLE_ID = "mapbox://styles/kaylaanhduong/cmm8dfrh0000w01qr9d2e9ac8"

# Load your CSV file
df = pd.read_csv('lab06 - Sheet1.csv')

print(f"Loaded {len(df)} locations from CSV")
print("Geocoding addresses using Mapbox... This may take a moment")

# Geocode addresses to get latitude and longitude using Mapbox API
def geocode_address_mapbox(address):
    try:
        url = f'https://api.mapbox.com/search/geocode/v6/forward'
        params = {
            'q': address,
            'access_token': MAPBOX_ACCESS_TOKEN,
            'limit': 1
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('features') and len(data['features']) > 0:
                coords = data['features'][0]['geometry']['coordinates']
                return coords[1], coords[0]  # Return lat, lon
        return None, None
    except Exception as e:
        print(f"Error geocoding: {e}")
        return None, None

# Add latitude and longitude columns
latitudes = []
longitudes = []

for idx, address in enumerate(df['Address']):
    print(f"Geocoding {idx + 1}/{len(df)}: {address[:50]}...")
    lat, lon = geocode_address_mapbox(address)
    latitudes.append(lat)
    longitudes.append(lon)
    time.sleep(0.5)  # Be respectful to the geocoding service

df['latitude'] = latitudes
df['longitude'] = longitudes

# Remove rows with missing coordinates
df_mapped = df.dropna(subset=['latitude', 'longitude'])
print(f"\nSuccessfully geocoded {len(df_mapped)} locations out of {len(df)}")

if len(df_mapped) == 0:
    print("Error: No locations were geocoded. Please check your addresses or API token.")
    exit(1)

# Create base map centered on Saigon using Mapbox
saigon_coords = [10.7769, 106.7009]
map_saigon = folium.Map(
    location=saigon_coords,
    zoom_start=12,
    tiles=None  # We'll add custom tiles below
)

# Add Mapbox tile layer using Raster Tiles API
folium.TileLayer(
    tiles=f"https://api.mapbox.com/v4/kaylaanhduong.cmm8dfrh0000w01qr9d2e9ac8/{{z}}/{{x}}/{{y}}.jpg?access_token={MAPBOX_ACCESS_TOKEN}",
    attr='<a href="https://www.mapbox.com/about/maps/" target="_blank">&copy; Mapbox</a>',
    name='Mapbox Custom Style',
    overlay=False,
    control=True,
    max_zoom=18
).add_to(map_saigon)

# Define marker colors based on location type
marker_colors = {
    'Schools & Educational Institutions': 'blue',
    'Landmark': 'orange',
    'Restaurants & Cafes': 'green',
    'Culture & History': 'purple',
    'Recreation': 'red'
}

# Add markers for each location
for idx, row in df_mapped.iterrows():
    location_type = row['Type']
    color = marker_colors.get(location_type, 'gray')
    
    # Create popup with image and details
    popup_html = f"""
    <div style="width: 280px; font-family: Arial; color: #333;">
        <h4 style="margin: 5px 0; color: #2c3e50;">{row['Name']}</h4>
        <p style="margin: 5px 0; font-size: 12px;"><b>Type:</b> {location_type}</p>
        <p style="margin: 5px 0; font-size: 12px;"><b>Address:</b> {row['Address']}</p>
        <p style="margin: 5px 0; font-size: 11px; line-height: 1.4;">{row['Description']}</p>
        <img src="{row['Image_URL']}" style="width: 100%; height: auto; margin-top: 10px; border-radius: 5px; border: 1px solid #ddd;">
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=row['Name'],
        icon=folium.Icon(color=color, icon='info-sign', prefix='fa')
    ).add_to(map_saigon)

# Add a layer control
folium.LayerControl().add_to(map_saigon)

# Add title to the map
title_html = '''
             <div style="position: fixed; 
                     top: 10px; left: 50px; width: 300px; height: 90px; 
                     background-color: white; border: 2px solid #2c3e50; 
                     z-index: 9999; font-size: 16px; font-weight: bold; 
                     padding: 12px; border-radius: 8px;
                     box-shadow: 0 2px 6px rgba(0,0,0,0.15);">
             🗺️ My Hometown Map - Saigon
             <br><span style="font-size: 12px; font-weight: normal; color: #555;">
             Meaningful locations in my life
             <br>Click markers to see details
             </span>
             </div>
             '''
map_saigon.get_root().html.add_child(folium.Element(title_html))

# Save the map
map_saigon.save('hometown_map.html')
print("\n✅ Map created successfully! Saved as 'hometown_map.html'")
print(f"Total locations displayed: {len(df_mapped)}")
print("\nLocation types:")
print(df_mapped['Type'].value_counts())