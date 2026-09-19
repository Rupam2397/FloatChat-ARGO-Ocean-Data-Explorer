import copernicusmarine
import numpy as np

from datetime import (
    datetime,
    timezone,
    timedelta
)


# ==========================================================
# FLOATCHAT - COPERNICUS MARINE SERVICE
# ==========================================================

DATASETS = {

    "temperature":
        "cmems_mod_glo_phy-thetao_anfc_0.083deg_P1D-m",

    "salinity":
        "cmems_mod_glo_phy-so_anfc_0.083deg_P1D-m",

    "currents":
        "cmems_mod_glo_phy-cur_anfc_0.083deg_P1D-m",
}


# ==========================================================
# CURRENT UTC TIME
# ==========================================================

def get_current_utc_time():

    now = datetime.now(
        timezone.utc
    )

    return now.replace(
        tzinfo=None
    )


# ==========================================================
# NORMALIZE TARGET TIME
# ==========================================================

def normalize_target_time(
    target_time=None
):

    if target_time is None:

        return get_current_utc_time()


    if isinstance(
        target_time,
        np.datetime64
    ):

        text = str(
            target_time
        )

        return datetime.fromisoformat(
            text.replace(
                "Z",
                ""
            )
        )


    if isinstance(
        target_time,
        datetime
    ):

        if target_time.tzinfo:

            target_time = (
                target_time
                .astimezone(
                    timezone.utc
                )
                .replace(
                    tzinfo=None
                )
            )

        return target_time


    if isinstance(
        target_time,
        str
    ):

        text = (
            target_time
            .strip()
            .replace(
                "Z",
                ""
            )
        )

        try:

            return datetime.fromisoformat(
                text
            )

        except ValueError:

            try:

                return datetime.strptime(
                    text,
                    "%Y-%m-%d"
                )

            except ValueError:

                raise ValueError(
                    "Invalid target date/time."
                )


    raise ValueError(
        "Unsupported target date/time."
    )


# ==========================================================
# TIME WINDOW
# ==========================================================

def get_time_window(
    target_time=None
):

    target = normalize_target_time(
        target_time
    )

    # Daily products are being used.
    # Open a small interval around the requested day.

    day_start = target.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )

    day_end = day_start + timedelta(
        hours=23,
        minutes=59,
        seconds=59
    )

    return (
        target,
        day_start,
        day_end
    )


# ==========================================================
# VALIDATION
# ==========================================================

def validate_coordinates(
    latitude,
    longitude,
    depth
):

    try:

        latitude = float(
            latitude
        )

        longitude = float(
            longitude
        )

        depth = float(
            depth
        )

    except (
        TypeError,
        ValueError
    ):

        return {

            "success": False,

            "error":
                "Latitude, longitude and depth "
                "must be valid numbers."
        }


    if not -90 <= latitude <= 90:

        return {

            "success": False,

            "error":
                "Latitude must be between "
                "-90 and 90."
        }


    if not -180 <= longitude <= 180:

        return {

            "success": False,

            "error":
                "Longitude must be between "
                "-180 and 180."
        }


    if depth < 0:

        return {

            "success": False,

            "error":
                "Depth cannot be negative."
        }


    return {

        "success": True,

        "latitude": latitude,

        "longitude": longitude,

        "depth": depth
    }


# ==========================================================
# DEPTH RANGE
# ==========================================================

def get_depth_range(
    depth
):

    if depth == 0:

        # Shallowest Copernicus model level is
        # approximately 0.494 m.

        return (
            0,
            2
        )


    return (

        max(
            0,
            depth - 1
        ),

        depth + 1
    )


# ==========================================================
# OPEN DATASET
# ==========================================================

def open_ocean_dataset(
    variable,
    latitude,
    longitude,
    depth,
    target_time=None
):

    target, start_time, end_time = (
        get_time_window(
            target_time
        )
    )


    minimum_depth, maximum_depth = (
        get_depth_range(
            depth
        )
    )


    box = 0.15


    dataset = (
        copernicusmarine.open_dataset(

            dataset_id=
                DATASETS[
                    variable
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
                maximum_depth,

            start_datetime=
                start_time,

            end_datetime=
                end_time,

            coordinates_selection_method=
                "nearest"
        )
    )


    return (
        dataset,
        target
    )


# ==========================================================
# SELECT OCEAN POINT
# ==========================================================

def select_ocean_point(
    dataset,
    latitude,
    longitude,
    depth,
    target_time=None
):

    target = normalize_target_time(
        target_time
    )


    target_np = np.datetime64(
        target
    )


    selected_time = dataset.sel(

        time=target_np,

        method="nearest"
    )


    if depth == 0:

        point = selected_time.sel(

            latitude=latitude,

            longitude=longitude,

            method="nearest"

        ).isel(
            depth=0
        )


    else:

        point = selected_time.sel(

            latitude=latitude,

            longitude=longitude,

            depth=depth,

            method="nearest"
        )


    return point


# ==========================================================
# EXTRACT GRID INFORMATION
# ==========================================================

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


# ==========================================================
# TEMPERATURE
# ==========================================================

def get_ocean_temperature(
    latitude,
    longitude,
    depth=0,
    target_time=None
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


        dataset, target = (
            open_ocean_dataset(

                "temperature",

                latitude,

                longitude,

                depth,

                target_time
            )
        )


        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth,

                target
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

                "error":
                    "No valid ocean temperature "
                    "was found at this coordinate "
                    "for the requested date."
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

            "success":
                True,

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

            "requested_time":
                target.isoformat(),

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
                "operational ocean model"
        }


    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ==========================================================
# SALINITY
# ==========================================================

def get_ocean_salinity(
    latitude,
    longitude,
    depth=0,
    target_time=None
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


        dataset, target = (
            open_ocean_dataset(

                "salinity",

                latitude,

                longitude,

                depth,

                target_time
            )
        )


        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth,

                target
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

                "error":
                    "No valid ocean salinity "
                    "was found at this coordinate "
                    "for the requested date."
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

            "success":
                True,

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

            "requested_time":
                target.isoformat(),

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
                "operational ocean model"
        }


    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ==========================================================
# OCEAN CURRENTS
# ==========================================================

def get_ocean_currents(
    latitude,
    longitude,
    depth=0,
    target_time=None
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


        dataset, target = (
            open_ocean_dataset(

                "currents",

                latitude,

                longitude,

                depth,

                target_time
            )
        )


        point = (
            select_ocean_point(

                dataset,

                latitude,

                longitude,

                depth,

                target
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

                "error":
                    "No valid ocean-current data "
                    "was found at this coordinate "
                    "for the requested date."
            }


        # --------------------------------------------------
        # CURRENT SPEED
        # --------------------------------------------------

        current_speed = np.sqrt(

            u_current ** 2

            +

            v_current ** 2
        )


        # --------------------------------------------------
        # DIRECTION WATER IS MOVING TOWARD
        # --------------------------------------------------

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

            "requested_time":
                target.isoformat(),

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
                "operational ocean model"
        }


    except Exception as error:

        return {

            "success": False,

            "error":
                str(error)
        }


# ==========================================================
# DIRECT TEST
# ==========================================================

if __name__ == "__main__":

    test_latitude = 3.7203503

    test_longitude = 73.2244152

    test_depth = 0


    today = (
        get_current_utc_time()
        .replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )
    )


    tomorrow = (
        today
        +
        timedelta(
            days=1
        )
    )


    print(
        "\nTODAY TEST:",
        today
    )


    today_temperature = (
        get_ocean_temperature(

            test_latitude,

            test_longitude,

            test_depth,

            today
        )
    )


    print(
        today_temperature
    )


    print(
        "\nTOMORROW TEST:",
        tomorrow
    )


    tomorrow_temperature = (
        get_ocean_temperature(

            test_latitude,

            test_longitude,

            test_depth,

            tomorrow
        )
    )


    print(
        tomorrow_temperature
    )