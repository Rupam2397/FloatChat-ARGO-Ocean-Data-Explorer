import copernicusmarine
import numpy as np
from datetime import datetime, timezone


# ============================================================
# FLOATCHAT - COPERNICUS MARINE SERVICE
# ============================================================
# Purpose:
#   Fetch real global ocean data from Copernicus Marine.
#
# Current capability:
#   - Global ocean temperature
#   - Latest/current available data
#   - Location-specific data
#   - Depth-specific data
#
# Next:
#   - Salinity
#   - Ocean currents
#   - Past historical data
#   - Future forecast
# ============================================================


# ============================================================
# COPERNICUS MARINE DATASET IDS
# ============================================================

DATASETS = {
    "temperature": "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m",
    "salinity": "cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m",
    "currents": "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
}


# ============================================================
# HELPER: CURRENT UTC TIME
# ============================================================

def get_current_utc_time():
    """
    Return current UTC time as numpy datetime64.
    """

    now = datetime.now(timezone.utc)

    # Remove timezone information because xarray/numpy dataset
    # coordinates are normally timezone-naive UTC timestamps.
    now = now.replace(tzinfo=None)

    return np.datetime64(now)


# ============================================================
# GET OCEAN TEMPERATURE
# ============================================================

def get_ocean_temperature(latitude, longitude, depth=0):
    """
    Get latest/current available ocean temperature from
    Copernicus Marine near the requested coordinates.

    Parameters
    ----------
    latitude : float
        Latitude between -90 and 90.

    longitude : float
        Longitude between -180 and 180.

    depth : float
        Requested depth in metres.
        depth=0 means surface / shallowest model level.

    Returns
    -------
    dict
        Ocean temperature information.
    """

    try:

        # ----------------------------------------------------
        # Validate coordinates
        # ----------------------------------------------------

        latitude = float(latitude)
        longitude = float(longitude)
        depth = float(depth)

        if latitude < -90 or latitude > 90:
            return {
                "success": False,
                "error": "Latitude must be between -90 and 90."
            }

        if longitude < -180 or longitude > 180:
            return {
                "success": False,
                "error": "Longitude must be between -180 and 180."
            }

        if depth < 0:
            return {
                "success": False,
                "error": "Depth cannot be negative."
            }

        print("\n========================================")
        print("FLOATCHAT - COPERNICUS MARINE")
        print("========================================")

        print("Connecting to Copernicus Marine...")
        print("Latitude :", latitude)
        print("Longitude:", longitude)
        print("Depth    :", depth, "m")

        # ----------------------------------------------------
        # Geographic search box
        # ----------------------------------------------------
        # Use a small box around the requested location.
        # We do NOT download the entire global ocean.
        # ----------------------------------------------------

        box = 0.15

        minimum_longitude = longitude - box
        maximum_longitude = longitude + box

        minimum_latitude = latitude - box
        maximum_latitude = latitude + box

        # ----------------------------------------------------
        # Surface depth handling
        # ----------------------------------------------------
        # Copernicus does not necessarily have an exact
        # depth coordinate of 0 m.
        #
        # For surface requests we allow the shallowest
        # available model layer to be selected.
        # ----------------------------------------------------

        if depth == 0:
            minimum_depth = 0
            maximum_depth = 2
        else:
            minimum_depth = max(0, depth - 1)
            maximum_depth = depth + 1

        # ----------------------------------------------------
        # Open remote Copernicus dataset
        # ----------------------------------------------------

        dataset = copernicusmarine.open_dataset(
            dataset_id=DATASETS["temperature"],

            minimum_longitude=minimum_longitude,
            maximum_longitude=maximum_longitude,

            minimum_latitude=minimum_latitude,
            maximum_latitude=maximum_latitude,

            minimum_depth=minimum_depth,
            maximum_depth=maximum_depth,
        )

        print("\nDataset opened successfully.")

        # ----------------------------------------------------
        # Select CURRENT / LATEST AVAILABLE time
        # ----------------------------------------------------
        #
        # IMPORTANT:
        #
        # Do NOT use:
        #
        # dataset.isel(time=-1)
        #
        # because the final time may be a future forecast.
        #
        # Instead select the dataset timestamp nearest
        # to the current UTC time.
        # ----------------------------------------------------

        current_time = get_current_utc_time()

        latest = dataset.sel(
            time=current_time,
            method="nearest"
        )

        # ----------------------------------------------------
        # Select nearest location
        # ----------------------------------------------------

        if depth == 0:

            # Surface = shallowest available model depth

            point = latest.sel(
                latitude=latitude,
                longitude=longitude,
                method="nearest"
            ).isel(depth=0)

        else:

            point = latest.sel(
                latitude=latitude,
                longitude=longitude,
                depth=depth,
                method="nearest"
            )

        # ----------------------------------------------------
        # Extract temperature
        # ----------------------------------------------------

        temperature = point["thetao"].values

        temperature = float(
            np.asarray(temperature).squeeze()
        )

        # ----------------------------------------------------
        # Check missing / land value
        # ----------------------------------------------------

        if np.isnan(temperature):

            return {
                "success": False,
                "error": (
                    "No valid ocean temperature was found at "
                    "this coordinate. The location may be on land "
                    "or outside a valid ocean grid cell."
                )
            }

        # ----------------------------------------------------
        # Extract actual Copernicus grid coordinates
        # ----------------------------------------------------

        selected_latitude = float(
            np.asarray(point["latitude"].values).squeeze()
        )

        selected_longitude = float(
            np.asarray(point["longitude"].values).squeeze()
        )

        selected_depth = float(
            np.asarray(point["depth"].values).squeeze()
        )

        selected_time = str(
            np.asarray(point["time"].values).squeeze()
        )

        # ----------------------------------------------------
        # Build response
        # ----------------------------------------------------

        result = {

            "success": True,

            "variable": "temperature",

            "value": round(temperature, 2),

            "unit": "°C",

            "requested_location": {
                "latitude": latitude,
                "longitude": longitude,
                "depth": depth
            },

            "actual_grid_location": {
                "latitude": selected_latitude,
                "longitude": selected_longitude,
                "depth": selected_depth
            },

            "time": selected_time,

            "source": "Copernicus Marine",

            "dataset": DATASETS["temperature"],

            "data_type": "latest analysis / nearest available time"
        }

        return result

    except Exception as error:

        return {
            "success": False,
            "error": str(error)
        }


# ============================================================
# DISPLAY RESULT
# ============================================================

def display_temperature_result(result):

    print("\n========================================")
    print("FLOATCHAT REAL OCEAN DATA TEST")
    print("========================================")

    if not result["success"]:

        print("ERROR:")
        print(result["error"])

        return

    print(
        "Temperature :",
        result["value"],
        result["unit"]
    )

    print(
        "Latitude    :",
        result["actual_grid_location"]["latitude"]
    )

    print(
        "Longitude   :",
        result["actual_grid_location"]["longitude"]
    )

    print(
        "Depth       :",
        result["actual_grid_location"]["depth"],
        "m"
    )

    print(
        "Time        :",
        result["time"]
    )

    print(
        "Data Type   :",
        result["data_type"]
    )

    print(
        "Source      :",
        result["source"]
    )

    print(
        "Dataset     :",
        result["dataset"]
    )


# ============================================================
# TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # Test location:
    # Arabian Sea
    #
    # Later this will NOT be hard-coded.
    # location_service.py will dynamically provide
    # coordinates from the user's search.
    # --------------------------------------------------------

    test_latitude = 20.0
    test_longitude = 65.0
    test_depth = 0

    result = get_ocean_temperature(
        latitude=test_latitude,
        longitude=test_longitude,
        depth=test_depth
    )

    display_temperature_result(result)
    