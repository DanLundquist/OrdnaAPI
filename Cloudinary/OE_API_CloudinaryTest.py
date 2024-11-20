import requests
import json
import os
from dotenv import load_dotenv
from cloudinary.api import resources
import cloudinary
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables from the .env file
load_dotenv()

# Retrieve values from environment variables for Ordna Eiendom and Cloudinary
username = os.getenv("USERNAME_TEST")  # Username in Ornda eiendom
password = os.getenv("PASSWORD_TEST")  # Password in Ordna eiendom
client_id = os.getenv("CLIENT_ID_BUILDING")  # API name provided by KA
client_secret = os.getenv("CLIENT_SECRET_BUILDING")  # API password provided by KA
token_url = os.getenv("TOKEN_URL_TEST")  # Request URL provided by KA
data_url = os.getenv("DATA_URL_BUILDING_TEST")  # Request URL provided by KA

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"), #Cloud name provided by KA
    api_key=os.getenv("CLOUDINARY_API_KEY"), #API Key provided by KA
    api_secret=os.getenv("CLOUDINARY_API_SECRET") #API Secret provided by KA
)

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
if response.status_code == 200:
    access_token = response.json().get("access_token")
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

# Load cache or create an empty one
CACHE_FILE = "results/cache/cloudinary_image_cache.json"
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r") as f:
        image_cache = json.load(f)
else:
    image_cache = {}

# Function to fetch images for a given folder (matching HistoricalBuildingCode)
def fetch_images(historical_building_code):
    # Check if images are already cached
    if historical_building_code in image_cache:
        print("Using cached images.")
        return image_cache[historical_building_code]

    folder_path = f"Plania/{historical_building_code}"
    try:
        # Fetch resources only in the specific folder path
        image_resources = resources(prefix=folder_path, type="upload", max_results=500)
        # Filter to include only images exactly in the `folder_path`
        image_urls = [
            resource["secure_url"]
            for resource in image_resources["resources"]
            if resource.get("folder") == folder_path
        ]

        # Save result to cache
        image_cache[historical_building_code] = image_urls

        # Update cache file
        with open(CACHE_FILE, "w") as f:
            json.dump(image_cache, f, indent=4)

        return image_urls
    except Exception as e:
        print(f"Error fetching images for {historical_building_code}: {e}")
        return []

# Retrieve list of resources within "Plania" from Cloudinary, filtering for folders
try:
    plania_resources_response = resources(prefix="Plania/", type="upload", max_results=500)
    # Extract folder names by taking unique paths up to each folder name level
    available_folders = {resource['folder'].split('/')[-1] for resource in plania_resources_response['resources']}
    print(f"Available folders in 'Plania': {available_folders}")
except Exception as e:
    print(f"Error retrieving folders from Cloudinary: {e}")
    available_folders = set()  # If there's an error, set to empty

# Initialize lists and counters
all_data = []
church_data_with_images = []
page_size = 200
page_number = 1

# Process features
while True:
    params = {
        "PageSize": page_size,
        "PageNumber": page_number
    }
    data_response = requests.get(data_url, headers=data_headers, params=params, timeout=10)
    
    if data_response.status_code == 200:
        data = data_response.json()
        features = data.get("features", [])
        
        # Filter features to only those in "Kirkebygg" category with folders in Cloudinary
        kirkebygg_features = [
            feature for feature in features
            if feature.get("properties", {}).get("BuildingCategory") == "Kirkebygg" and
               feature.get("properties", {}).get("HistoricalBuildingCode") in available_folders
        ]
        
        # Fetch images only for features with a corresponding folder
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_feature = {
                executor.submit(fetch_images, feature["properties"]["HistoricalBuildingCode"]): feature
                for feature in kirkebygg_features
            }
            
            for future in as_completed(future_to_feature):
                feature = future_to_feature[future]
                historical_building_code = feature["properties"]["HistoricalBuildingCode"]
                
                try:
                    image_urls = future.result()
                    if image_urls:
                        feature["properties"]["image_urls"] = image_urls
                        church_data_with_images.append(feature)
                    else:
                        print(f"No images found for {historical_building_code} in Cloudinary.")
                except Exception as e:
                    print(f"Error processing feature for {historical_building_code}: {e}")

        # Add all retrieved features to all_data
        all_data.extend(features)

        # Stop if fewer items were retrieved than the page size, indicating the last page
        if len(features) < page_size:
            break
        else:
            page_number += 1
    else:
        print(f"Error retrieving data: {data_response.status_code}")
        print(data_response.json())
        break

# Save the GeoJSON results
geojson_data = {
    "type": "FeatureCollection",
    "features": all_data
}

os.makedirs("results", exist_ok=True)
output_file = "results/cloudinaryResults/all_churches.geojson"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(geojson_data, file, indent=4, ensure_ascii=False)
print(f"All data has been saved to {output_file} in GeoJSON format.")

if church_data_with_images:
    image_output_file = "results/cloudinaryResults/church_data_with_images.geojson"
    with open(image_output_file, "w", encoding="utf-8") as file:
        json.dump({"type": "FeatureCollection", "features": church_data_with_images}, file, indent=4, ensure_ascii=False)
    print(f"Data with image URLs has been saved to {image_output_file}")
else:
    print("No data with images was found, so no output file with images was created.")

print(f"\nTotal entries processed: {len(all_data)}")
print(f"Entries with images found: {len(church_data_with_images)}")
