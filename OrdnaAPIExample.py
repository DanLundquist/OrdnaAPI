# This file is meant as an example of how to authenticate and retrieve data from Ordna Eiendom.
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve values from environment variables
username = os.getenv("USERNAME") #Username in Ornda eiendom
password = os.getenv("PASSWORD") #Password in Ordna eiendom
client_id = os.getenv("CLIENT_ID") #API name provided by KA
client_secret = os.getenv("CLIENT_SECRET") #API password provided by KA
token_url = os.getenv("TOKEN_URL") #Request URL provided by KA
data_url = os.getenv("DATA_URL") #Request URL provided by KA

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
        
        # Add the retrieved features to the list
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

# Write all data to a JSON file
output_file = "all_data.json"
with open(output_file, "w", encoding="utf-8") as file:
    json.dump(all_data, file, indent=4, ensure_ascii=False)

print(f"All data has been saved to {output_file}")

# Print the total count of features retrieved
print(f"\nTotal number of features exported: {len(all_data)}")
