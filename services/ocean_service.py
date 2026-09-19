# ============================================================
# FLOATCHAT - GLOBAL OCEAN SERVICE
# ============================================================
#
# User:
#   "Maldives"
#
#           ↓
#
# location_service.py
#
#           ↓
#
# Latitude + Longitude
#
#           ↓
#
# copernicus_service.py
#
#           ↓
#
# Temperature
# Salinity
# Ocean currents
#
# ============================================================


from location_service import search_location

from copernicus_service import (
    get_ocean_temperature,
    get_ocean_salinity,
    get_ocean_currents
)


# ============================================================
# GET COMPLETE OCEAN CONDITIONS
# ============================================================

def get_ocean_conditions(
    place_name,
    depth=0
):

    print(
        "\n========================================"
    )

    print(
        "FLOATCHAT GLOBAL OCEAN SEARCH"
    )

    print(
        "========================================"
    )

    print(
        "Searching location:",
        place_name
    )

    # ========================================================
    # STEP 1
    # FIND LOCATION
    # ========================================================

    location = search_location(
        place_name
    )

    if not location[
        "success"
    ]:

        return {

            "success": False,

            "error":
                location.get(

                    "error",

                    "Location could not be found."
                )
        }

    latitude = location[
        "latitude"
    ]

    longitude = location[
        "longitude"
    ]

    print(
        "\nLocation found:"
    )

    print(
        location[
            "display_name"
        ]
    )

    print(
        "Latitude :",
        latitude
    )

    print(
        "Longitude:",
        longitude
    )


    # ========================================================
    # STEP 2
    # TEMPERATURE
    # ========================================================

    temperature = (
        get_ocean_temperature(

            latitude=latitude,

            longitude=longitude,

            depth=depth
        )
    )


    # ========================================================
    # STEP 3
    # SALINITY
    # ========================================================

    salinity = (
        get_ocean_salinity(

            latitude=latitude,

            longitude=longitude,

            depth=depth
        )
    )


    # ========================================================
    # STEP 4
    # OCEAN CURRENTS
    # ========================================================

    currents = (
        get_ocean_currents(

            latitude=latitude,

            longitude=longitude,

            depth=depth
        )
    )


    # ========================================================
    # COMBINED RESULT
    # ========================================================

    return {

        "success": True,

        "place":
            place_name,

        "location": {

            "display_name":
                location[
                    "display_name"
                ],

            "latitude":
                latitude,

            "longitude":
                longitude
        },

        "requested_depth":
            depth,

        "temperature":
            temperature,

        "salinity":
            salinity,

        "currents":
            currents
    }


# ============================================================
# DISPLAY COMPLETE RESULT
# ============================================================

def display_ocean_conditions(
    result
):

    print(
        "\n\n========================================"
    )

    print(
        "FLOATCHAT OCEAN CONDITIONS"
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


    # ========================================================
    # LOCATION
    # ========================================================

    print(
        "Place       :",
        result["place"]
    )

    print(
        "Location    :",
        result[
            "location"
        ][
            "display_name"
        ]
    )

    print(
        "Latitude    :",
        result[
            "location"
        ][
            "latitude"
        ]
    )

    print(
        "Longitude   :",
        result[
            "location"
        ][
            "longitude"
        ]
    )

    print(
        "Depth       :",
        result[
            "requested_depth"
        ],
        "m"
    )

    print(
        "----------------------------------------"
    )


    # ========================================================
    # TEMPERATURE
    # ========================================================

    temperature = result[
        "temperature"
    ]

    if temperature[
        "success"
    ]:

        print(
            "Temperature :",
            temperature[
                "value"
            ],
            temperature[
                "unit"
            ]
        )

        print(
            "Temp Time   :",
            temperature[
                "time"
            ]
        )

    else:

        print(
            "Temperature : UNAVAILABLE"
        )

        print(
            "Reason      :",
            temperature[
                "error"
            ]
        )


    # ========================================================
    # SALINITY
    # ========================================================

    salinity = result[
        "salinity"
    ]

    if salinity[
        "success"
    ]:

        print(
            "Salinity    :",
            salinity[
                "value"
            ],
            salinity[
                "unit"
            ]
        )

        print(
            "Salt Time   :",
            salinity[
                "time"
            ]
        )

    else:

        print(
            "Salinity    : UNAVAILABLE"
        )

        print(
            "Reason      :",
            salinity[
                "error"
            ]
        )


    # ========================================================
    # CURRENTS
    # ========================================================

    currents = result[
        "currents"
    ]

    if currents[
        "success"
    ]:

        print(
            "Current U   :",
            currents[
                "eastward_current"
            ],
            "m/s"
        )

        print(
            "Current V   :",
            currents[
                "northward_current"
            ],
            "m/s"
        )

        print(
            "Speed       :",
            currents[
                "speed"
            ],
            currents[
                "speed_unit"
            ]
        )

        print(
            "Direction   :",
            currents[
                "direction_degrees"
            ],
            "degrees",
            "("
            + currents[
                "direction"
            ]
            + ")"
        )

        print(
            "Current Time:",
            currents[
                "time"
            ]
        )

    else:

        print(
            "Currents    : UNAVAILABLE"
        )

        print(
            "Reason      :",
            currents[
                "error"
            ]
        )


    print(
        "----------------------------------------"
    )

    print(
        "Source      : Copernicus Marine"
    )

    print(
        "========================================"
    )


# ============================================================
# TEST PROGRAM
# ============================================================

if __name__ == "__main__":

    # Change this to test another location.

    test_place = "Maldives"

    test_depth = 0


    result = (
        get_ocean_conditions(

            place_name=
                test_place,

            depth=
                test_depth
        )
    )


    display_ocean_conditions(
        result
    )