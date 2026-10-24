import math
import requests
from routing_test import get_route
import streamlit as st

st.set_page_config(page_title="Elomira", page_icon="🌍", layout="centered")

st.title("🌍 Elomira")
st.subheader("Explore Smarter. Go Safer.")
st.write(
    "Explore outdoor activities using location, weather and air-quality data."
)

ACTIVITIES = [
    "Running / Jogging",
    "Cycling",
    "Golf",
    "Recreational Cricket",
    "Outdoor Football",
    "Outdoor Tennis",
    "Hiking / Nature Walk",
    "Picnic / Park Outing",
    "Outdoor Event / Gathering",
    "Outdoor Photography",
]


def calculate_distance(point_a, point_b):
    earth_radius = 6371000

    lat1 = math.radians(point_a["latitude"])
    lat2 = math.radians(point_b["latitude"])
    lat_difference = lat2 - lat1
    lon_difference = math.radians(
        point_b["longitude"] - point_a["longitude"]
    )

    a = (
        math.sin(lat_difference / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(lon_difference / 2) ** 2
    )

    return 2 * earth_radius * math.atan2(
        math.sqrt(a), math.sqrt(1 - a)
    )



def get_elevations(locations):
    url = "https://api.open-elevation.com/api/v1/lookup"

    params = {
        "locations": "|".join(
            f"{point['latitude']},{point['longitude']}"
            for point in locations
        )
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=30,
        )
        response.raise_for_status()

        results = response.json().get("results", [])

        if len(results) != len(locations):
            return None

        return [item["elevation"] for item in results]

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return None



def calculate_slope(distance_metres, elevation_change):
    if distance_metres <= 0:
        return None

    return abs(elevation_change) / distance_metres * 100






def assess_conditions(temperature, precipitation, wind_speed, aqi):
    warnings = []

    if temperature is not None and temperature >= 38:
        warnings.append(
            "High temperature: consider postponing strenuous outdoor "
            "activity and seeking shade."
        )

    if precipitation is not None and precipitation >= 2:
        warnings.append(
            "Precipitation is reported for the current period. "
            "Check local weather and rain alerts before going out."
        )

    if wind_speed is not None and wind_speed >= 30:
        warnings.append(
            "Strong winds: use caution during outdoor sports and cycling."
        )

    if aqi is not None and aqi > 100:
        warnings.append(
            "Elevated US AQI: consider reducing prolonged or strenuous "
            "outdoor activity, especially for sensitive people."
        )

    if warnings:
        return "Review conditions before going", warnings

    return "No major warning detected by these basic rules", [
        "Check local alerts and your personal needs before heading out."
    ]

# Keep Elomira readings available across Streamlit reruns
if "elomira_data" not in st.session_state:
    st.session_state.elomira_data = {
        "temperature": None,
        "humidity": None,
        "precipitation": None,
        "wind_speed": None,
        "aqi": None,
        "pm25": None,
        "pm10": None,
        "latitude": None,
        "longitude": None,
    }

location = st.text_input("Enter your city or location", "Tirunelveli")
activity = st.selectbox("Choose an outdoor activity", ACTIVITIES)

if st.button("Check Conditions") or st.session_state.get("conditions_checked", False):
    st.session_state.conditions_checked = True
    if not location.strip():
        st.error("Please enter a location.")
    else:
        try:
            geo_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={
                    "name": location.strip(),
                    "count": 1,
                    "language": "en",
                    "format": "json",
                },
                timeout=15,
            )
            geo_response.raise_for_status()
            results = geo_response.json().get("results", [])

            if not results:
                st.error("Location not found. Try another city.")
            else:
                place = results[0]
                latitude = place["latitude"]
                longitude = place["longitude"]

                st.header(
                    f"{place['name']}, {place.get('country', '')}"
                )
                st.write(f"**Selected activity:** {activity}")

                weather_response = requests.get(
                    "https://api.open-meteo.com/v1/forecast",
                    params={
                        "latitude": latitude,
                        "longitude": longitude,
                        "current": (
                            "temperature_2m,relative_humidity_2m,"
                            "precipitation,wind_speed_10m"
                        ),
                        "timezone": "auto",
                    },
                    timeout=15,
                )
                weather_response.raise_for_status()
                weather = weather_response.json().get("current", {})

                temperature = weather.get("temperature_2m")
                humidity = weather.get("relative_humidity_2m")
                precipitation = weather.get("precipitation")
                wind_speed = weather.get("wind_speed_10m")
                st.session_state.elomira_data["temperature"] = temperature
                st.session_state.elomira_data["humidity"] = humidity
                st.session_state.elomira_data["precipitation"] = precipitation
                st.session_state.elomira_data["wind_speed"] = wind_speed
                st.session_state.elomira_data["latitude"] = latitude
                st.session_state.elomira_data["longitude"] = longitude
               
                st.subheader("🌦️ Weather")
                c1, c2 = st.columns(2)
                c1.metric(
                    "Temperature",
                    f"{temperature} °C"
                    if temperature is not None else "Unavailable",
                )
                c2.metric(
                    "Humidity",
                    f"{humidity}%"
                    if humidity is not None else "Unavailable",
                )
                c1.metric(
                    "Precipitation",
                    f"{precipitation} mm"
                    if precipitation is not None else "Unavailable",
                )
                c2.metric(
                    "Wind speed",
                    f"{wind_speed} km/h"
                    if wind_speed is not None else "Unavailable",
                )

                aqi = None
                st.subheader("🌿 Air Quality")

                try:
                    air_response = requests.get(
                        "https://air-quality-api.open-meteo.com/v1/air-quality",
                        params={
                            "latitude": latitude,
                            "longitude": longitude,
                            "current": "us_aqi,pm2_5,pm10",
                            "timezone": "auto",
                        },
                        timeout=15,
                    )
                    air_response.raise_for_status()
                    air = air_response.json().get("current", {})

                    aqi = air.get("us_aqi")
                    pm25 = air.get("pm2_5")
                    pm10 = air.get("pm10")
                    st.session_state.elomira_data["aqi"] = aqi
                    st.session_state.elomira_data["pm25"] = pm25
                    st.session_state.elomira_data["pm10"] = pm10

                    a1, a2 = st.columns(2)
                    a1.metric(
                        "US AQI",
                        str(aqi) if aqi is not None else "Unavailable",
                    )
                    a2.metric(
                        "PM2.5",
                        f"{pm25} µg/m³"
                        if pm25 is not None else "Unavailable",
                    )
                    st.metric(
                        "PM10",
                        f"{pm10} µg/m³"
                        if pm10 is not None else "Unavailable",
                    )

                    st.caption(
                        "Air-quality values are model-based estimates, "
                        "not necessarily measurements from a nearby station."
                    )
                    if aqi is not None:
                        if aqi <= 50:
                           aqi_category = "Good"
                        elif aqi <= 100:
                           aqi_category = "Moderate"
                        elif aqi <= 150:
                           aqi_category = "Unhealthy for Sensitive Groups"
                        elif aqi <= 200:
                           aqi_category = "Unhealthy"
                        elif aqi <= 300:
                           aqi_category = "Very Unhealthy"
                        else:
                           aqi_category = "Hazardous"

                        st.write(f"**US AQI Category:** {aqi_category}")
                except (requests.RequestException, ValueError):
                    st.warning("Air-quality data is temporarily unavailable.")

                st.subheader("🧭 Safety Assessment")
                status, warnings = assess_conditions(
                    temperature, precipitation, wind_speed, aqi
                )
                st.write(f"**Assessment:** {status}")

                for warning in warnings:
                    st.warning(warning)

                st.caption(
                    "Basic screening only, not an official warning system. "
                    "Check local alerts and site conditions. Missing data "
                    "does not mean conditions are safe."
                )
                st.markdown("**Checks covered**")
                st.write(
                    "- Temperature: warning if 38°C or higher."
                )
                st.write(
                    "- Precipitation: warning if 2 mm or higher."
                )
                st.write(
                    "- Wind speed: warning if 30 km/h or higher."
                )
                st.write(
                    "- US AQI: warning if above 100."
                )

                st.caption(
                    "These are basic screening thresholds, not universal "
                    "safety limits or official warnings. Some hazards may "
                    "not be checked, and missing data does not mean conditions "
                    "are safe. Check official local alerts and site conditions."
                )

                st.subheader("🌅 Daylight Information")

                try:
                    daylight_response = requests.get(
                        "https://api.open-meteo.com/v1/forecast",
                        params={
                            "latitude": latitude,
                            "longitude": longitude,
                            "daily": "sunrise,sunset",
                            "forecast_days": 1,
                            "timezone": "auto",
                        },
                        timeout=15,
                    )
                    daylight_response.raise_for_status()

                    daylight = daylight_response.json().get("daily", {})
                    sunrise_values = daylight.get("sunrise", [])
                    sunset_values = daylight.get("sunset", [])

                    if sunrise_values and sunset_values:
                        st.write(f"**Sunrise:** {sunrise_values[0]}")
                        st.write(f"**Sunset:** {sunset_values[0]}")
                        st.caption(
                            "Times are provided by Open-Meteo for the "
                            "selected location's local timezone."
                        )
                    else:
                        st.warning("Daylight times are unavailable.")

                except (requests.RequestException, ValueError):
                    st.warning(
                        "Daylight information is temporarily unavailable."
                    )

                st.subheader("⛰️ Terrain Information")

                terrain_points = [
                    {"latitude": latitude, "longitude": longitude},
                    {
                        "latitude": latitude + 0.004,
                        "longitude": longitude + 0.003,
                    },
                    {
                        "latitude": latitude + 0.008,
                        "longitude": longitude + 0.006,
                    },
                ]

                with st.spinner("Retrieving elevation data..."):
                    elevations = get_elevations(terrain_points)

                if elevations is None:
                    st.warning(
                        "Terrain data is temporarily unavailable. "
                        "Other Elomira features can still be used."
                    )
                else:
                    st.metric(
                        "Elevation at selected location",
                        f"{elevations[0]:.1f} metres"
                    )

                    for index in range(len(terrain_points) - 1):
                        distance = calculate_distance(
                            terrain_points[index],
                            terrain_points[index + 1],
                        )

                        elevation_change = (
                            elevations[index + 1] - elevations[index]
                        )

                        slope = calculate_slope(
                            distance, elevation_change
                        )

                        st.write(f"**Terrain segment {index + 1}**")
                        st.write(
                            f"Elevation change: {elevation_change:.2f} metres"
                        )

                        if slope is not None:
                            st.write(f"Approximate slope: {slope:.2f}%")
                

                st.subheader("📍 Nearby Places")

                place_type = st.selectbox(
                    "Choose a place type",
                    [
                        "Parks",
                        "Sports facilities",
                        "Restaurants",
                        "Hospitals",
                        "Tourist attractions",
                    ],
                )

                place_queries = {
                    "Parks": "park",
                    "Sports facilities": "sports centre",
                    "Restaurants": "restaurant",
                    "Hospitals": "hospital",
                    "Tourist attractions": "tourist attraction",
                }

                if st.button("Find Nearby Places"):
                    try:
                        with st.spinner("Searching nearby places..."):
                            place_response = requests.get(
                                "https://nominatim.openstreetmap.org/search",
                                params={
                                    "q": (
                                        place_queries[place_type]
                                        + " near "
                                        + str(latitude)
                                        + ","
                                        + str(longitude)
                                    ),
                                    "format": "jsonv2",
                                    "limit": 5,
                                },
                                headers={
                                    "User-Agent": "ElomiraGeoAI/1.0"
                                },
                                timeout=15,
                            )
                            place_response.raise_for_status()
                            nearby_places = place_response.json()

                        if nearby_places:
                            for place in nearby_places:
                                st.write(
                                    "**"
                                    + place.get("name", "Unnamed place")
                                    + "**"
                                )
                                st.caption(place.get("display_name", ""))

                                try:
                                    place_lat = float(place["lat"])
                                    place_lon = float(place["lon"])

                                    route = get_route(
                                        start_lon=float(longitude),
                                        start_lat=float(latitude),
                                        end_lon=place_lon,
                                        end_lat=place_lat,
                                    )

                                    if "error" not in route:
                                        st.caption(
                                            f"Road distance: {route['distance_km']} km | "
                                            f"Estimated driving time: "
                                            f"{route['duration_min']} minutes"
                                        )
                                    else:
                                        st.caption(
                                            "Road distance and driving time are unavailable."
                                        )

                                except (KeyError, ValueError, TypeError):
                                    st.caption(
                                        "Road distance and driving time are unavailable."
                                    )
                        else:
                            st.info(
                                "No places found. Try another place type."
                            )
                    except (
                        requests.RequestException,
                        ValueError,
                        TypeError,
                    ):
                        st.warning(
                            "Nearby-place search is temporarily unavailable. "
                            "Please try again later."
                        ) 
                
        except requests.RequestException:
            st.error(
                "Could not connect to a data service. Check your internet "
                "connection and try again."
            )
        except (KeyError, ValueError, TypeError):
            st.exception(Exception("Unexpected data received. Check the traceback in the Command Prompt for the exact cause."))

# Restore the latest readings for the AI section
saved_data = st.session_state.elomira_data

temperature = saved_data.get("temperature")
humidity = saved_data.get("humidity")
precipitation = saved_data.get("precipitation")
wind_speed = saved_data.get("wind_speed")
aqi = saved_data.get("aqi")
pm25 = saved_data.get("pm25")
pm10 = saved_data.get("pm10")

st.divider()
st.header("🤖 Ask Elomira AI")

user_question = st.text_input(
    "What would you like to know about your outdoor activity?",
    placeholder="e.g. Is it a good time to go cycling?"
)

if st.button("Ask Elomira AI"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Elomira AI is thinking..."):
            try:
                response = requests.post(
                    "http://localhost:11434/api/chat",
                    json={
                        "model": "qwen2.5:1.5b",
                        "messages": [
                            {
                                "role": "system",
                                "content": (
                                    "You are Elomira, a GeoAI outdoor activity assistant. "
                                    "Give clear, practical advice in simple English. "
                                    "Understand the user's exact question, requested activity, "
                                    "location, date, time and distance limit. "
                                    "Answer the specific question, not just general safety advice. "
                                    "When relevant, explain: recommendation, best supported time, "
                                    "suitable places, what to prepare, what to watch for, and "
                                    "when to delay, change location or avoid the activity. "
                                    "Use only weather, air-quality, daylight, terrain, place and "
                                    "distance data actually supplied to you. "
                                    "Never invent live readings, forecasts, venues, distances, "
                                    "routes, travel times, alerts or daylight times. "
                                    "If essential data is missing, clearly state what is unavailable "
                                    "and give only advice supported by the available information. "
                                    "Use the supplied US AQI category without changing it. "
                                    "US AQI 0-50 is Good; 51-100 is Moderate; "
                                    "101-150 is Unhealthy for Sensitive Groups; "
                                    "151-200 is Unhealthy; 201-300 is Very Unhealthy; "
                                    "above 300 is Hazardous. "
                                    "Do not describe Moderate AQI as Good or risk-free. "
                                    "Do not guarantee that conditions are safe. "
                                    "Consider activity-specific risks, including heat, humidity, "
                                    "rain, wind, air quality, terrain, traffic and daylight "
                                    "when relevant and when data is available. "
                                    "For asthma or older adults, give cautious general guidance "
                                    "without making medical claims. "
                                    "Do not claim a best time unless the supplied forecast, "
                                    "requested time and relevant daylight information support it."
                                )
                            },
                            {
                                "role": "user",
                                "content": (
    f"Location: {location}\n"
    f"Selected activity: {activity}\n"
    f"Temperature: {temperature} °C\n"
    f"Humidity: {humidity}%\n"
    f"Precipitation: {precipitation} mm\n"
    f"Wind speed: {wind_speed} km/h\n"
    f"US AQI: {aqi} (Category: {'Good' if aqi is not None and aqi <= 50 else 'Moderate' if aqi is not None and aqi <= 100 else 'Unhealthy for Sensitive Groups' if aqi is not None and aqi <= 150 else 'Unhealthy' if aqi is not None and aqi <= 200 else 'Very Unhealthy' if aqi is not None and aqi <= 300 else 'Hazardous' if aqi is not None else 'Unavailable'})\n"
    f"PM2.5: {pm25} µg/m³\n"
    f"PM10: {pm10} µg/m³\n\n"
    f"User question: {user_question}\n\n"
    "Use these readings to answer. If a value is None, "
    "say it is unavailable. Do not invent live data. "
    "Give practical advice for the selected activity."
)
                            }
                        ],
                        "stream": False
                    },
                    timeout=120
                )
                response.raise_for_status()
                answer = response.json()["message"]["content"]
                st.markdown("### Elomira's Answer")
                st.write(answer)

            except requests.exceptions.RequestException as error:
                st.error(
                    "Could not connect to the AI. "
                    "Make sure Ollama is running."
                )
                st.caption(str(error))
