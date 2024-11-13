import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve values from environment variables
username = os.getenv("USERNAME")  # Username in Ornda eiendom
password = os.getenv("PASSWORD")  # Password in Ordna eiendom
client_id = os.getenv("CLIENT_ID_GRAVEYARD")  # API name provided by KA
client_secret = os.getenv("CLIENT_SECRET_GRAVEYARD")  # API password provided by KA
token_url = os.getenv("TOKEN_URL")  # Request URL provided by KA
data_url = os.getenv("DATA_URL_GRAVEYARD")  # Request URL provided by KA

# Set headers and body for the authentication request
headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json"
}
body = {
    "grant_type": "password",
    "username": username,
    "password": password,
    "client_id": client_id,
    "client_secret": client_secret,
    "Force_Logout": "false"
}

# Request an access token
response = requests.post(token_url, headers=headers, data=body)

# Check if the access token request was successful
if response.status_code == 200:
    response_data = response.json()
    access_token = response_data.get("access_token")
    print("Access token retrieved:", access_token)
else:
    print(f"Error retrieving token: {response.status_code}")
    print(response.json())
    exit()

# Set headers for the data request, including the access token
data_headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

all_data = []
missing_coordinates = []
page_size = 200
page_number = 1

# Loop through paginated data until all pages are retrieved
while True:
    params = {
        "PageSize": page_size,
        "PageNumber": page_number
    }
    data_response = requests.get(data_url, headers=data_headers, params=params)
    
    # Check if data retrieval was successful
    if data_response.status_code == 200:
        data = data_response.json()
        features = data.get("features", [])
        
        # Process each feature, checking and swapping coordinates if they exist
        for feature in features:
            coordinates = feature.get("geometry", {}).get("coordinates", [])
            description = feature.get("properties", {}).get("Description", "No Description")
            
            if len(coordinates) == 2:  # Valid coordinates
                # Swap X and Y
                feature["geometry"]["coordinates"] = [coordinates[1], coordinates[0]]
                # Add feature to all_data
                all_data.append(feature)
            else:
                # Record graveyard with missing coordinates
                missing_coordinates.append({"Description": description})
        
        # Stop if fewer items were retrieved than the page size, indicating the last page
        if len(features) < page_size:
            break
        else:
            page_number += 1
    else:
        print(f"Error retrieving data: {data_response.status_code}")
        print(data_response.json())
        break

# Ensure results folder exists
os.makedirs("results", exist_ok=True)

# Wrap the collected features in a FeatureCollection for valid GeoJSON output
geojson_data = {
    "type": "FeatureCollection",
    "features": all_data
}

# Write the GeoJSON data with valid coordinates to the results folder
output_file = "results/all_data.geojson"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(geojson_data, file, indent=4, ensure_ascii=False)

# Write the data with missing coordinates to a separate file in the results folder
missing_output_file = "results/buildings_missing_coordinates.json"
with open(missing_output_file, "w", encoding="utf-8") as file:
    json.dump(missing_coordinates, file, indent=4, ensure_ascii=False)

# Print output summary
print(f"All data with coordinates saved to {output_file} in GeoJSON format.")
print(f"\nTotal number of features with coordinates: {len(all_data)}")
print(f"Total number of graveyards without coordinates: {len(missing_coordinates)}")
print(f"Graveyards without coordinates saved to {missing_output_file}.")
