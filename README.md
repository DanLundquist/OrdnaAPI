# Ordna Eiendom API and Cloudinary Data Processing

This repository contains Python scripts to authenticate, retrieve, and process data from the Ordna Eiendom API and Cloudinary.

## Files

### `OE_API_Graveyards_Modified.py`
- Authenticates with the Ordna Eiendom API to fetch graveyard data.
- Processes paginated responses, validates geometry, and exports data:
  - **GeoJSON output**: `results/graveyardResults/all_graveyard.geojson`
  - **Missing coordinates**: `results/graveyardResults/graveyards_missing_coordinates.json`

### `OE_API_Cloudinary.py`
- Retrieves data on churches from the Ordna Eiendom API and matches them with images in Cloudinary.
- Filters data for churches categorized as "Kirkebygg" with images available in Cloudinary.
- Outputs two files:
  - **All church data**: `results/cloudinaryResults/all_churches.geojson`
  - **Church data with images**: `results/cloudinaryResults/church_data_with_images.geojson`

### OE_API_Authenticate_And_Retrieve.py
- Authenticates with the Ordna Eiendom API using environment variables.
- Retrieves building data in paginated form from the API.
- Processes the retrieved data and exports it as a GeoJSON file.
  - **GeoJSON output**: Saves all data to results/churchResults/all_churches.geojson.
