import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from the .env file
load_dotenv()

# Retrieve values from environment variables
username = os.getenv("USERNAME")  # Username in Ordna eiendom
password = os.getenv("PASSWORD")  # Password in Ordna eiendom
client_id = os.getenv("CLIENT_ID_BUILDING_SIMPLE")  # API name provided by KA
client_secret = os.getenv("CLIENT_SECRET_BUILDING_SIMPLE")  # API password provided by KA
token_url = os.getenv("TOKEN_URL")  # Token URL provided by KA
data_url = os.getenv("DATA_URL_BUILDING_SIMPLE")  # Data URL provided by KA

# Authenticate and retrieve access token
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

response = requests.post(token_url, headers=headers, data=body)

if response.status_code == 200:
    response_data = response.json()
    access_token = response_data.get("access_token")
    print("Access token retrieved:", access_token)
else:
    print(f"Error retrieving token: {response.status_code}")
    print(response.json())
    exit()

# Set headers for the data request
data_headers = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/json"
}

# Initialize data retrieval
all_data = []
page_size = 200
page_number = 1

# Loop through paginated data until all pages are retrieved
while True:
    params = {
        "PageSize": page_size,
        "PageNumber": page_number
    }
    data_response = requests.get(data_url, headers=data_headers, params=params)
    
    if data_response.status_code == 200:
        data = data_response.json()
        
        # Add the retrieved data to the list
        all_data.extend(data)
        
        # Stop if fewer items were retrieved than the page size
        if len(data) < page_size:
            break
        else:
            page_number += 1
    else:
        print(f"Error retrieving data: {data_response.status_code}")
        print(data_response.json())
        break

folder_name = datetime.now().strftime("results/simple_churches")
os.makedirs(folder_name, exist_ok=True)

# Write the data to a JSON file
output_file = os.path.join(folder_name, "simple_churches.json")
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_data, file, indent=4, ensure_ascii=False)

print(f"All data has been saved to {output_file} in JSON format.")
print(f"Total number of records exported: {len(all_data)}")
