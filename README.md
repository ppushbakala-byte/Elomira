# Elomira — GeoAI Outdoor Assistant

Elomira is a geospatial AI assistant designed to help users make informed outdoor activity decisions using weather, air quality, daylight, terrain and nearby-place information.

## Features

- Weather information using Open-Meteo
- Air-quality information, including AQI and particulate matter
- Sunrise, sunset and daylight information
- Elevation and terrain information
- Nearby-place search using OpenStreetMap/Nominatim
- Road distance and estimated driving time using OSRM
- AI-generated responses using Qwen2.5 1.5B through Ollama

## Technology Stack

- Python
- Streamlit
- Qwen2.5 1.5B via Ollama
- Open-Meteo APIs
- OpenStreetMap Nominatim
- OSRM routing service

## Run Locally

1. Install Python.
2. Install Ollama and download the model:

   `ollama pull qwen2.5:1.5b`

3. Install the required Python packages used by the application.
4. Start Ollama.
5. Run the application:

   `streamlit run app_daylight_terrain_working_fixed.py`

## Data and Limitations

Weather and air-quality values depend on the external data providers and may be model-based estimates rather than measurements from a nearby station. Road distances and travel times are estimates and can change with traffic and road conditions. Elomira is not an official emergency-warning service.

## Project Status

Prototype developed for the GeoAI Hackathon 2026.

## Credits

- Open-Meteo
- OpenStreetMap and Nominatim
- OSRM
- Qwen2.5
- Streamlit
