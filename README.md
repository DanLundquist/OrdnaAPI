# Ordna Eiendom API and Cloudinary Data Processing

This repository contains Python scripts to authenticate, retrieve, and process data from the Ordna Eiendom API and Cloudinary.

## Files

### `Churches/OrdnaAPIExample.py`
- Authenticates with the Ordna Eiendom API to fetch church data.
- Processes paginated responses and exports data as a GeoJSON file.

### `Cloudinary/OE_API_CloudinaryTest.py`
- Retrieves church data from the Ordna Eiendom API and matches them with images in Cloudinary.
- Outputs two files: all church data and church data with images. (caching image urls)

### `Graveyard/OE_API_Graveyards_Modified.py`
- Authenticates with the Ordna Eiendom API to fetch graveyard data.
- Processes paginated responses, validates geometry, and exports data as GeoJSON files.

### `Simple church/simpleChurchExample.py`
- Authenticates with the Ordna Eiendom API to fetch simple church data.
- Processes paginated responses and exports data as a JSON file.

### `Simple graveyard/simpleGraveyardExample.py`
- Authenticates with the Ordna Eiendom API to fetch simple graveyard data.
- Processes paginated responses and exports data as a JSON file.

## Environment Variables

The values required for authentication and data retrieval are stored in the `.env` file. These values are not included in the repository. 
You will receive them once you log into [ordna.planiasky.no](https://ordna.planiasky.no) with the account provided by KA.
