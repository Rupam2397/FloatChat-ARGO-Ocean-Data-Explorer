import copernicusmarine
import numpy as np
from datetime import datetime, timezone


# ============================================================
# FLOATCHAT - COPERNICUS MARINE SERVICE
# ============================================================
#
# CURRENT:
#
#   Temperature
#   Salinity
#   Ocean currents
#   Current speed
#   Current direction
#   Latest/current available model data
#   Location-specific queries
#   Depth-specific queries
#
# ============================================================


# ============================================================
# DATASETS
# ============================================================

DATASETS = {

    "temperature":
        "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m",

    "salinity":
        "cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m",

    "currents":
        "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
}


# ============================================================
# CURRENT UTC TIME
# ============================================================

def get_current_utc_time():

    now = datetime.now(
        timezone.utc
    )

    now = now.replace(
        tzinfo=None
    )

    return np.datetime64(
        now
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_coordinates(
    latitude,
    longitude,
    depth
):

    try:

        latitude = float(latitude)
        longitude = float(longitude)
        depth = float(depth)

    except (TypeError, ValueError):

        return {
            "success": False,
            "error": (
                "Latitude, longitude and depth "
                "must be valid numbers."
            )
        }

    if not -90 <= latitude <= 90:

        return {
            "success": False,
            "error": (
                "Latitude must be "
                "between -90 and 90."
            )
        }

    if not -180 <= longitude <= 180:

        return {
            "success": False,
            "error": (
                "Longitude must be "
                "between -180 and 180."
            )
        }

    if depth < 0:

        return {
            "success": False,
            "error": (
                "Depth cannot be negative."
            )
        }

    return {

        "success": True,

        "latitude": latitude,

        "longitude": longitude,

        "depth": depth
    }


# ============================================================
# DEPTH RANGE
# ============================================================

def get_depth_range(depth):

    if depth == 0:

        minimum_depth = 0

        maximum_depth = 2

    else:

        minimum_depth = max(
            0,
            depth - 1
        )

        maximum_depth = (
            depth + 1
        )

    return (
        minimum_depth,
        maximum_depth
    )


# ============================================================
# SELECT OCEAN POINT
# ============================================================

def select_ocean_point(
    dataset,
    latitude,
    longitude,
    depth
):

    current_time = (
        get_current_utc_time()
    )

    latest = dataset.sel(

        time=current_time,

        method="nearest"
    )

    if depth == 0:

        point = latest.sel(

            latitude=latitude,

            longitude=longitude,

            method="nearest"

        ).isel(
            depth=0
        )

    else:

        point = latest.sel(

            latitude=latitude,

            longitude=longitude,

            depth=depth,

            method="nearest"
        )

    return point


# ============================================================
# EXTRACT GRID INFORMATION
# ============================================================

def extract_grid_information(
    point
):

    latitude = float(

        np.asarray(

            point[
                "latitude"
            ].values

        ).squeeze()
    )

    longitude = float(

        np.asarray(

            point[
                "longitude"
            ].values

        ).squeeze()
    )

    depth = float(

        np.asarray(

            point[
                "depth"
            ].values

        ).squeeze()
    )

    time = str(

        np.asarray(

            point[
                "time"
            ].values

        ).squeeze()
    )

    return (
        latitude,
        longitude,
        depth,
        time
    )


# ============================================================
# TEMPERATURE
# ============================================================

def get_ocean_temperature(
    latitude,
    longitude,
    depth=0
):

    try:

        validation = (
            validate_coordinates(
                latitude,
                longitude,
                depth
            )
        )

        if not validation[
            "success"
        ]:

            return validation

        latitude = validation[
            "latitude"
        ]

        longitude = validation[
            "longitude"
        ]

        depth = validation[
            "depth"
        ]

        print(
            "\n========================================"
        )

        print(
            "FLOATCHAT - OCEAN TEMPERATURE"
        )

        print(
            "========================================"
        )

        print(
            "Connecting to Copernicus Marine..."
        )

        print(
            "Latitude :",
            latitude
        )

        print(
            "Longitude:",
            longitude
        )

        print(
            "Depth    :",
            depth,
            "m"
        )

        box = 0.15

        minimum_depth, maximum_depth = (
            get_depth_range(
                depth
            )
        )

        dataset = (
            copernicusmarine.open_dataset(

                dataset_id=
                DATASETS[
                    "temperature"
                ],

                minimum_longitude=
                longitude - box,

                maximum_longitude=
                longitude + box,

                minimum_latitude=
                latitude - box,

                maximum_latitude=
                latitude + box,

                minimum_depth=
                minimum_depth,

                maximum_depth=
                maximum_depth
            )
        )

        print(
            "\nTemperature dataset opened successfully."
        )

        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth
            )
        )

        temperature = float(

            np.asarray(

                point[
                    "thetao"
                ].values

            ).squeeze()
        )

        if np.isnan(
            temperature
        ):

            return {

                "success": False,

                "error": (
                    "No valid ocean temperature "
                    "was found at this coordinate."
                )
            }

        (
            grid_latitude,
            grid_longitude,
            grid_depth,
            selected_time

        ) = extract_grid_information(
            point
        )

        return {

            "success": True,

            "variable":
                "temperature",

            "value":
                round(
                    temperature,
                    2
                ),

            "unit":
                "°C",

            "requested_location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "depth":
                    depth
            },

            "actual_grid_location": {

                "latitude":
                    grid_latitude,

                "longitude":
                    grid_longitude,

                "depth":
                    grid_depth
            },

            "time":
                selected_time,

            "source":
                "Copernicus Marine",

            "dataset":
                DATASETS[
                    "temperature"
                ],

            "data_type":
                "nearest available operational model time"
        }

    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ============================================================
# SALINITY
# ============================================================

def get_ocean_salinity(
    latitude,
    longitude,
    depth=0
):

    try:

        validation = (
            validate_coordinates(
                latitude,
                longitude,
                depth
            )
        )

        if not validation[
            "success"
        ]:

            return validation

        latitude = validation[
            "latitude"
        ]

        longitude = validation[
            "longitude"
        ]

        depth = validation[
            "depth"
        ]

        print(
            "\n========================================"
        )

        print(
            "FLOATCHAT - OCEAN SALINITY"
        )

        print(
            "========================================"
        )

        print(
            "Connecting to Copernicus Marine..."
        )

        print(
            "Latitude :",
            latitude
        )

        print(
            "Longitude:",
            longitude
        )

        print(
            "Depth    :",
            depth,
            "m"
        )

        box = 0.15

        minimum_depth, maximum_depth = (
            get_depth_range(
                depth
            )
        )

        dataset = (
            copernicusmarine.open_dataset(

                dataset_id=
                DATASETS[
                    "salinity"
                ],

                minimum_longitude=
                longitude - box,

                maximum_longitude=
                longitude + box,

                minimum_latitude=
                latitude - box,

                maximum_latitude=
                latitude + box,

                minimum_depth=
                minimum_depth,

                maximum_depth=
                maximum_depth
            )
        )

        print(
            "\nSalinity dataset opened successfully."
        )

        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth
            )
        )

        salinity = float(

            np.asarray(

                point[
                    "so"
                ].values

            ).squeeze()
        )

        if np.isnan(
            salinity
        ):

            return {

                "success": False,

                "error": (
                    "No valid ocean salinity "
                    "was found at this coordinate."
                )
            }

        (
            grid_latitude,
            grid_longitude,
            grid_depth,
            selected_time

        ) = extract_grid_information(
            point
        )

        return {

            "success": True,

            "variable":
                "salinity",

            "value":
                round(
                    salinity,
                    2
                ),

            "unit":
                "PSU",

            "requested_location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "depth":
                    depth
            },

            "actual_grid_location": {

                "latitude":
                    grid_latitude,

                "longitude":
                    grid_longitude,

                "depth":
                    grid_depth
            },

            "time":
                selected_time,

            "source":
                "Copernicus Marine",

            "dataset":
                DATASETS[
                    "salinity"
                ],

            "data_type":
                "nearest available operational model time"
        }

    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ============================================================
# OCEAN CURRENTS
# ============================================================

def get_ocean_currents(
    latitude,
    longitude,
    depth=0
):

    try:

        validation = (
            validate_coordinates(
                latitude,
                longitude,
                depth
            )
        )

        if not validation[
            "success"
        ]:

            return validation

        latitude = validation[
            "latitude"
        ]

        longitude = validation[
            "longitude"
        ]

        depth = validation[
            "depth"
        ]

        print(
            "\n========================================"
        )

        print(
            "FLOATCHAT - OCEAN CURRENTS"
        )

        print(
            "========================================"
        )

        print(
            "Connecting to Copernicus Marine..."
        )

        print(
            "Latitude :",
            latitude
        )

        print(
            "Longitude:",
            longitude
        )

        print(
            "Depth    :",
            depth,
            "m"
        )

        box = 0.15

        minimum_depth, maximum_depth = (
            get_depth_range(
                depth
            )
        )

        dataset = (
            copernicusmarine.open_dataset(

                dataset_id=
                DATASETS[
                    "currents"
                ],

                minimum_longitude=
                longitude - box,

                maximum_longitude=
                longitude + box,

                minimum_latitude=
                latitude - box,

                maximum_latitude=
                latitude + box,

                minimum_depth=
                minimum_depth,

                maximum_depth=
                maximum_depth
            )
        )

        print(
            "\nCurrent dataset opened successfully."
        )

        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth
            )
        )

        u_current = float(

            np.asarray(

                point[
                    "uo"
                ].values

            ).squeeze()
        )

        v_current = float(

            np.asarray(

                point[
                    "vo"
                ].values

            ).squeeze()
        )

        if (
            np.isnan(
                u_current
            )
            or
            np.isnan(
                v_current
            )
        ):

            return {

                "success": False,

                "error": (
                    "No valid ocean current "
                    "data was found at this coordinate."
                )
            }

        # ----------------------------------------------------
        # CURRENT SPEED
        #
        # speed = sqrt(u² + v²)
        # ----------------------------------------------------

        current_speed = np.sqrt(

            u_current ** 2

            +

            v_current ** 2
        )

        # ----------------------------------------------------
        # CURRENT DIRECTION
        #
        # Direction water is moving toward.
        #
        # 0   = North
        # 90  = East
        # 180 = South
        # 270 = West
        # ----------------------------------------------------

        direction_degrees = (

            np.degrees(

                np.arctan2(

                    u_current,

                    v_current
                )
            )

            + 360

        ) % 360

        compass_directions = [

            "N",

            "NE",

            "E",

            "SE",

            "S",

            "SW",

            "W",

            "NW"
        ]

        compass_index = int(

            (
                direction_degrees
                +
                22.5
            )

            // 45

        ) % 8

        compass_direction = (
            compass_directions[
                compass_index
            ]
        )

        (
            grid_latitude,
            grid_longitude,
            grid_depth,
            selected_time

        ) = extract_grid_information(
            point
        )

        return {

            "success":
                True,

            "variable":
                "ocean_currents",

            "eastward_current":
                round(
                    u_current,
                    3
                ),

            "northward_current":
                round(
                    v_current,
                    3
                ),

            "speed":
                round(
                    float(
                        current_speed
                    ),
                    3
                ),

            "speed_unit":
                "m/s",

            "direction_degrees":
                round(
                    float(
                        direction_degrees
                    ),
                    1
                ),

            "direction":
                compass_direction,

            "direction_description":
                "direction water is moving toward",

            "requested_location": {

                "latitude":
                    latitude,

                "longitude":
                    longitude,

                "depth":
                    depth
            },

            "actual_grid_location": {

                "latitude":
                    grid_latitude,

                "longitude":
                    grid_longitude,

                "depth":
                    grid_depth
            },

            "time":
                selected_time,

            "source":
                "Copernicus Marine",

            "dataset":
                DATASETS[
                    "currents"
                ],

            "data_type":
                "nearest available operational model time"
        }

    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ============================================================
# DISPLAY TEMPERATURE
# ============================================================

def display_temperature_result(
    result
):

    print(
        "\n========================================"
    )

    print(
        "TEMPERATURE RESULT"
    )

    print(
        "========================================"
    )

    if not result[
        "success"
    ]:

        print(
            "ERROR:",
            result["error"]
        )

        return

    print(
        "Temperature :",
        result["value"],
        result["unit"]
    )

    print(
        "Latitude    :",
        result[
            "actual_grid_location"
        ]["latitude"]
    )

    print(
        "Longitude   :",
        result[
            "actual_grid_location"
        ]["longitude"]
    )

    print(
        "Depth       :",
        result[
            "actual_grid_location"
        ]["depth"],
        "m"
    )

    print(
        "Time        :",
        result["time"]
    )

    print(
        "Source      :",
        result["source"]
    )


# ============================================================
# DISPLAY SALINITY
# ============================================================

def display_salinity_result(
    result
):

    print(
        "\n========================================"
    )

    print(
        "SALINITY RESULT"
    )

    print(
        "========================================"
    )

    if not result[
        "success"
    ]:

        print(
            "ERROR:",
            result["error"]
        )

        return

    print(
        "Salinity    :",
        result["value"],
        result["unit"]
    )

    print(
        "Latitude    :",
        result[
            "actual_grid_location"
        ]["latitude"]
    )

    print(
        "Longitude   :",
        result[
            "actual_grid_location"
        ]["longitude"]
    )

    print(
        "Depth       :",
        result[
            "actual_grid_location"
        ]["depth"],
        "m"
    )

    print(
        "Time        :",
        result["time"]
    )

    print(
        "Source      :",
        result["source"]
    )


# ============================================================
# DISPLAY CURRENTS
# ============================================================

def display_current_result(
    result
):

    print(
        "\n========================================"
    )

    print(
        "OCEAN CURRENT RESULT"
    )

    print(
        "========================================"
    )

    if not result[
        "success"
    ]:

        print(
            "ERROR:",
            result["error"]
        )

        return

    print(
        "Eastward U  :",
        result[
            "eastward_current"
        ],
        "m/s"
    )

    print(
        "Northward V :",
        result[
            "northward_current"
        ],
        "m/s"
    )

    print(
        "Speed       :",
        result["speed"],
        result["speed_unit"]
    )

    print(
        "Direction   :",
        result[
            "direction_degrees"
        ],
        "degrees",
        "("
        + result["direction"]
        + ")"
    )

    print(
        "Meaning     :",
        result[
            "direction_description"
        ]
    )

    print(
        "Latitude    :",
        result[
            "actual_grid_location"
        ]["latitude"]
    )

    print(
        "Longitude   :",
        result[
            "actual_grid_location"
        ]["longitude"]
    )

    print(
        "Depth       :",
        result[
            "actual_grid_location"
        ]["depth"],
        "m"
    )

    print(
        "Time        :",
        result["time"]
    )

    print(
        "Source      :",
        result["source"]
    )


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    test_latitude = 20.0

    test_longitude = 65.0

    test_depth = 0


    print(
        "\n########################################"
    )

    print(
        "TEST 1 - TEMPERATURE"
    )

    print(
        "########################################"
    )

    temperature = (
        get_ocean_temperature(

            test_latitude,

            test_longitude,

            test_depth
        )
    )

    display_temperature_result(
        temperature
    )


    print(
        "\n########################################"
    )

    print(
        "TEST 2 - SALINITY"
    )

    print(
        "########################################"
    )

    salinity = (
        get_ocean_salinity(

            test_latitude,

            test_longitude,

            test_depth
        )
    )

    display_salinity_result(
        salinity
    )


    print(
        "\n########################################"
    )

    print(
        "TEST 3 - CURRENTS"
    )

    print(
        "########################################"
    )

    currents = (
        get_ocean_currents(

            test_latitude,

            test_longitude,

            test_depth
        )
    )

    display_current_result(
        currents
    )