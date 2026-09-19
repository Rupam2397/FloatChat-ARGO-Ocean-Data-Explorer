from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


# Development geocoder.
# Later, for public production deployment, we will replace/configure
# this with a production-appropriate geocoding service.
geolocator = Nominatim(
    user_agent="floatchat_ocean_platform"
)


def search_location(place_name):
    """
    Convert a place name into latitude and longitude.

    Example:
        "Chennai"
        "Maldives"
        "Tokyo"
        "Sydney"
        "Pacific Ocean"
        "Arabian Sea"
    """

    if not place_name or not place_name.strip():
        return {
            "success": False,
            "error": "Please enter a location."
        }

    try:
        location = geolocator.geocode(
            place_name.strip(),
            exactly_one=True,
            timeout=10
        )

        if location is None:
            return {
                "success": False,
                "error": f"Location '{place_name}' was not found."
            }

        return {
            "success": True,
            "query": place_name,
            "display_name": location.address,
            "latitude": float(location.latitude),
            "longitude": float(location.longitude)
        }

    except GeocoderTimedOut:
        return {
            "success": False,
            "error": "Location service timed out. Please try again."
        }

    except GeocoderServiceError as error:
        return {
            "success": False,
            "error": f"Location service error: {error}"
        }

    except Exception as error:
        return {
            "success": False,
            "error": f"Unexpected error: {error}"
        }


if __name__ == "__main__":

    test_locations = [
        "Chennai, India",
        "Tokyo, Japan",
        "Sydney, Australia",
        "Maldives",
        "Arabian Sea"
    ]

    for place in test_locations:

        print("\n-----------------------------")
        print("Searching:", place)

        result = search_location(place)

        if result["success"]:
            print("Found:", result["display_name"])
            print("Latitude:", result["latitude"])
            print("Longitude:", result["longitude"])
        else:
            print("Error:", result["error"])
            