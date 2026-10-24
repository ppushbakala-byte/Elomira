
import requests


def get_route(start_lon, start_lat, end_lon, end_lat, profile="driving"):
    """Return road distance and estimated travel time from OSRM."""

    if profile not in {"driving", "cycling", "walking"}:
        return {"error": "Unsupported route profile."}

    # The public OSRM demo server supports driving routes only.
    # Do not label driving estimates as cycling or walking times.
    if profile != "driving":
        return {
            "error": (
                "Cycling and walking routes are not available "
                "from this driving-only OSRM endpoint."
            )
        }

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{start_lon},{start_lat};{end_lon},{end_lat}"
    )

    try:
        response = requests.get(
            url,
            params={"overview": "false"},
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

        if data.get("code") != "Ok" or not data.get("routes"):
            return {"error": "No driving route found."}

        route = data["routes"][0]

        return {
            "distance_km": round(route["distance"] / 1000, 2),
            "duration_min": round(route["duration"] / 60, 1),
            "profile": "driving",
            "source": "OSRM",
        }

    except (requests.RequestException, ValueError, KeyError, TypeError):
        return {"error": "Routing service is temporarily unavailable."}


if __name__ == "__main__":
    # Test route only — these coordinates are examples in Tirunelveli.
    result = get_route(
        start_lon=77.7322504,
        start_lat=8.6771767,
        end_lon=77.7285398,
        end_lat=8.6983518,
    )

    print("Elomira routing test:")
    print(result)
