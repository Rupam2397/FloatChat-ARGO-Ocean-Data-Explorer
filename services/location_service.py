from geopy.geocoders import Nominatim
from geopy.exc import GeocoderServiceError, GeocoderTimedOut


# ============================================================
# FLOATCHAT - GLOBAL LOCATION SERVICE
# ============================================================
#
# Purpose:
#
# Convert a place name into latitude and longitude.
#
# Example:
#
# Maldives
#      ↓
# Latitude  = 3.72
# Longitude = 73.22
#
# ============================================================


geolocator = Nominatim(
    user_agent="floatchat_ocean_platform"
)


# ============================================================
# SEARCH LOCATION
# ============================================================

def search_location(place_name):
    """
    Search any world location and return coordinates.
    """

    try:

        if not place_name:
            return {
                "success": False,
                "error": "Please enter a location."
            }

        place_name = str(place_name).strip()

        if not place_name:
            return {
                "success": False,
                "error": "Please enter a valid location."
            }

        print("\nSearching:", place_name)

        location = geolocator.geocode(
            place_name,
            timeout=10
        )

        if location is None:

            return {
                "success": False,
                "error": (
                    "Location could not be found: "
                    + place_name
                )
            }

        return {

            "success": True,

            "query": place_name,

            "display_name": location.address,

            "latitude": float(
                location.latitude
            ),

            "longitude": float(
                location.longitude
            )
        }

    except GeocoderTimedOut:

        return {
            "success": False,
            "error": (
                "Location search timed out. "
                "Please try again."
            )
        }

    except GeocoderServiceError as error:

        return {
            "success": False,
            "error": (
                "Location service error: "
                + str(error)
            )
        }

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_locations = [
        "Chennai, India",
        "Tokyo, Japan",
        "Sydney, Australia",
        "Maldives",
        "Arabian Sea"
    ]

    for place in test_locations:

        print("\n========================================")

        result = search_location(place)

        if result["success"]:

            print(
                "Found:",
                result["display_name"]
            )

            print(
                "Latitude:",
                result["latitude"]
            )

            print(
                "Longitude:",
                result["longitude"]
            )

        else:

            print(
                "ERROR:",
                result["error"]
            )