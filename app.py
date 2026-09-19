# ==========================================================
# FLOATCHAT
# AI-Powered Global Ocean Intelligence Platform
# ==========================================================

from flask import Flask, render_template, request, jsonify

import re

from datetime import (
    datetime,
    timezone,
    timedelta
)


# ==========================================================
# ARGO DATA FUNCTIONS
# ==========================================================

from data.argo_data import (
    temperature_summary,
    salinity_summary,
    dataset_summary,
    temperature_data,
    salinity_data,
    location_data
)


# ==========================================================
# GLOBAL OCEAN SERVICES
# ==========================================================

from services.location_service import search_location

from services.copernicus_service import (
    get_ocean_temperature,
    get_ocean_salinity,
    get_ocean_currents
)


# ==========================================================
# FLASK APP
# ==========================================================

app = Flask(__name__)


# ==========================================================
# HOME
# ==========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# ==========================================================
# HELPER: EXTRACT DEPTH
# ==========================================================

def extract_depth(question):

    if not question:

        return 0.0


    patterns = [

        r"\bat\s+(\d+(?:\.\d+)?)\s*m\b",

        r"\bat\s+(\d+(?:\.\d+)?)\s*meter\b",

        r"\bat\s+(\d+(?:\.\d+)?)\s*meters\b",

        r"\b(\d+(?:\.\d+)?)\s*m\s+deep\b",

        r"\b(\d+(?:\.\d+)?)\s*meters?\s+deep\b"
    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            question,
            re.IGNORECASE
        )

        if match:

            try:

                return float(
                    match.group(1)
                )

            except ValueError:

                return 0.0


    return 0.0


# ==========================================================
# HELPER: BUILD TEMPORAL INFORMATION
# ==========================================================

def build_temporal_info(
    target,
    today
):

    target = target.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0
    )


    if target.date() > today.date():

        temporal_mode = "forecast"

        temporal_label = "Ocean Forecast"


    elif target.date() < today.date():

        temporal_mode = "past"

        temporal_label = "Past Ocean Conditions"


    else:

        temporal_mode = "current"

        temporal_label = "Current Ocean Conditions"


    return {

        "target_time":
            target,

        "requested_date":
            target.strftime(
                "%Y-%m-%d"
            ),

        "temporal_mode":
            temporal_mode,

        "temporal_label":
            temporal_label
    }


# ==========================================================
# HELPER: EXTRACT REQUESTED DATE / TIME
# ==========================================================

def extract_requested_time(question):

    now = datetime.now(
        timezone.utc
    )


    today = now.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
        tzinfo=None
    )


    default_result = {

        "target_time":
            today,

        "requested_date":
            today.strftime(
                "%Y-%m-%d"
            ),

        "temporal_mode":
            "current",

        "temporal_label":
            "Current Ocean Conditions"
    }


    if not question:

        return default_result


    q = question.lower().strip()


    # ------------------------------------------------------
    # TOMORROW
    # ------------------------------------------------------

    if re.search(
        r"\btomorrow\b",
        q
    ):

        target = today + timedelta(
            days=1
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # YESTERDAY
    # ------------------------------------------------------

    if re.search(
        r"\byesterday\b",
        q
    ):

        target = today - timedelta(
            days=1
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # IN N DAYS
    # ------------------------------------------------------

    match = re.search(
        r"\bin\s+(\d+)\s+days?\b",
        q
    )

    if match:

        days = int(
            match.group(1)
        )

        target = today + timedelta(
            days=days
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # NEXT N DAYS
    # ------------------------------------------------------

    match = re.search(
        r"\bnext\s+(\d+)\s+days?\b",
        q
    )

    if match:

        days = int(
            match.group(1)
        )

        target = today + timedelta(
            days=days
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # N DAYS AGO
    # ------------------------------------------------------

    match = re.search(
        r"\b(\d+)\s+days?\s+ago\b",
        q
    )

    if match:

        days = int(
            match.group(1)
        )

        target = today - timedelta(
            days=days
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # LAST N DAYS
    # ------------------------------------------------------

    match = re.search(
        r"\blast\s+(\d+)\s+days?\b",
        q
    )

    if match:

        days = int(
            match.group(1)
        )

        target = today - timedelta(
            days=days
        )

        return build_temporal_info(
            target,
            today
        )


    # ------------------------------------------------------
    # YYYY-MM-DD
    # ------------------------------------------------------

    match = re.search(
        r"\bon\s+(\d{4}-\d{2}-\d{2})\b",
        q
    )

    if match:

        try:

            target = datetime.strptime(
                match.group(1),
                "%Y-%m-%d"
            )

            return build_temporal_info(
                target,
                today
            )

        except ValueError:

            pass


    # ------------------------------------------------------
    # DD/MM/YYYY
    # ------------------------------------------------------

    match = re.search(
        r"\bon\s+(\d{1,2}/\d{1,2}/\d{4})\b",
        q
    )

    if match:

        try:

            target = datetime.strptime(
                match.group(1),
                "%d/%m/%Y"
            )

            return build_temporal_info(
                target,
                today
            )

        except ValueError:

            pass


    # ------------------------------------------------------
    # DD-MM-YYYY
    # ------------------------------------------------------

    match = re.search(
        r"\bon\s+(\d{1,2}-\d{1,2}-\d{4})\b",
        q
    )

    if match:

        try:

            target = datetime.strptime(
                match.group(1),
                "%d-%m-%Y"
            )

            return build_temporal_info(
                target,
                today
            )

        except ValueError:

            pass


    # ------------------------------------------------------
    # TODAY / NOW / CURRENT / LATEST
    # ------------------------------------------------------

    return default_result


# ==========================================================
# HELPER: EXTRACT PLACE
# ==========================================================

def extract_place(question):

    if not question:

        return None


    text = question.strip()


    patterns = [

        r"\bnear\s+(.+)$",

        r"\bin\s+(.+)$",

        r"\baround\s+(.+)$",

        r"\bat\s+(.+)$",

        r"\bof\s+(.+)$",

        r"\bfor\s+(.+)$"
    ]


    place = None


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if match:

            place = (
                match
                .group(1)
                .strip()
            )

            break


    if not place:

        return None


    # ------------------------------------------------------
    # REMOVE DEPTH
    # ------------------------------------------------------

    place = re.sub(
        r"\bat\s+\d+(?:\.\d+)?\s*(?:m|meter|meters)\b",
        "",
        place,
        flags=re.IGNORECASE
    )


    place = re.sub(
        r"\b\d+(?:\.\d+)?\s*(?:m|meter|meters)\s+deep\b",
        "",
        place,
        flags=re.IGNORECASE
    )


    # ------------------------------------------------------
    # REMOVE TIME WORDS
    # ------------------------------------------------------

    time_patterns = [

        r"\bright now\b",

        r"\bthis morning\b",

        r"\bthis afternoon\b",

        r"\bthis evening\b",

        r"\btoday\b",

        r"\bnow\b",

        r"\bcurrently\b",

        r"\blatest\b",

        r"\bcurrent\b",

        r"\btomorrow\b",

        r"\byesterday\b",

        r"\btonight\b",

        r"\bnext day\b",

        r"\bnext week\b",

        r"\bnext month\b",

        r"\blast day\b",

        r"\blast week\b",

        r"\blast month\b",

        r"\b\d+\s*days?\s+ago\b",

        r"\bin\s+\d+\s*days?\b",

        r"\bnext\s+\d+\s*days?\b",

        r"\blast\s+\d+\s*days?\b"
    ]


    for time_pattern in time_patterns:

        place = re.sub(
            time_pattern,
            "",
            place,
            flags=re.IGNORECASE
        )


    # ------------------------------------------------------
    # REMOVE DATES
    # ------------------------------------------------------

    place = re.sub(
        r"\bon\s+\d{1,2}[/-]\d{1,2}[/-]\d{4}\b",
        "",
        place,
        flags=re.IGNORECASE
    )


    place = re.sub(
        r"\bon\s+\d{4}-\d{2}-\d{2}\b",
        "",
        place,
        flags=re.IGNORECASE
    )


    # ------------------------------------------------------
    # CLEAN LOCATION
    # ------------------------------------------------------

    place = re.sub(
        r"[?!.,]+$",
        "",
        place
    )


    place = re.sub(
        r"\s+",
        " ",
        place
    )


    place = place.strip(
        " ,.-"
    )


    if not place:

        return None


    return place


# ==========================================================
# HELPER: DETECT GLOBAL OCEAN QUESTION
# ==========================================================

def is_global_ocean_question(question):

    if not question:

        return False


    q = question.lower()


    ocean_terms = [

        "ocean",

        "sea",

        "marine",

        "current",

        "temperature",

        "salinity",

        "water"
    ]


    location_terms = [

        " near ",

        " in ",

        " around ",

        " at ",

        " of ",

        " for "
    ]


    has_ocean_term = any(
        term in q
        for term in ocean_terms
    )


    has_location_term = any(
        term in q
        for term in location_terms
    )


    return (
        has_ocean_term
        and
        has_location_term
    )


# ==========================================================
# HELPER: DATA TYPE LABEL
# ==========================================================

def get_data_type_label(
    temporal_mode
):

    if temporal_mode == "forecast":

        return "Operational Forecast"


    if temporal_mode == "past":

        return "Operational Analysis"


    return "Operational Ocean Model"


# ==========================================================
# HELPER: GLOBAL OCEAN QUERY
# ==========================================================

def handle_global_ocean_query(question):

    # ------------------------------------------------------
    # EXTRACT LOCATION
    # ------------------------------------------------------

    place = extract_place(
        question
    )


    if not place:

        return jsonify(
            {
                "answer":
                    "❌ I could not identify a location.\n\n"
                    "Try a question such as:\n"
                    "Ocean conditions in Maldives",

                "type":
                    "error"
            }
        )


    # ------------------------------------------------------
    # GEOCODE
    # ------------------------------------------------------

    location = search_location(
        place
    )


    if (
        not location
        or
        not location.get(
            "success"
        )
    ):

        error_message = (

            location.get(
                "error",
                f"Location could not be found: {place}"
            )

            if location

            else

            f"Location could not be found: {place}"
        )


        return jsonify(
            {
                "answer":
                    "❌ Location could not be found.\n\n"
                    f"Search: {place}\n\n"
                    f"{error_message}",

                "type":
                    "error",

                "search":
                    place
            }
        )


    # ------------------------------------------------------
    # COORDINATES
    # ------------------------------------------------------

    latitude = float(
        location[
            "latitude"
        ]
    )


    longitude = float(
        location[
            "longitude"
        ]
    )


    # ------------------------------------------------------
    # DEPTH
    # ------------------------------------------------------

    depth = extract_depth(
        question
    )


    # ------------------------------------------------------
    # DATE / TIME
    # ------------------------------------------------------

    time_info = extract_requested_time(
        question
    )


    target_time = time_info[
        "target_time"
    ]


    requested_date = time_info[
        "requested_date"
    ]


    temporal_mode = time_info[
        "temporal_mode"
    ]


    temporal_label = time_info[
        "temporal_label"
    ]


    data_type = get_data_type_label(
        temporal_mode
    )


    q = question.lower()


    # ======================================================
    # CURRENT / CURRENTS ONLY
    # ======================================================

    if (
        (
            "current" in q
            or
            "currents" in q
        )
        and
        "temperature" not in q
        and
        "salinity" not in q
        and
        "condition" not in q
    ):

        currents = get_ocean_currents(
            latitude,
            longitude,
            depth,
            target_time
        )


        if currents.get(
            "success"
        ):

            answer = (

                "🌊 Ocean Current\n\n"

                f"📍 Location: {place}\n"

                f"Latitude: {latitude:.4f}°\n"

                f"Longitude: {longitude:.4f}°\n\n"

                f"📅 Requested Date: "
                f"{requested_date}\n"

                f"Mode: {temporal_label}\n\n"

                f"Current Speed: "
                f"{currents.get('speed')} "
                f"{currents.get('speed_unit')}\n"

                f"Current Direction: "
                f"{currents.get('direction_degrees')}° "
                f"({currents.get('direction')})\n\n"

                f"Data Time: "
                f"{currents.get('time')}\n"

                f"Source: Copernicus Marine\n"

                f"Type: {data_type}"
            )

        else:

            answer = (

                "❌ Ocean-current data could not "
                f"be retrieved for {place}.\n\n"

                f"Requested Date: "
                f"{requested_date}\n\n"

                f"{currents.get('error', '')}"
            )


        return jsonify(
            {
                "answer":
                    answer,

                "type":
                    "ocean_current",

                "location":
                    location,

                "requested_place":
                    place,

                "requested_depth":
                    depth,

                "requested_date":
                    requested_date,

                "temporal_mode":
                    temporal_mode,

                "temporal_label":
                    temporal_label,

                "currents":
                    currents,

                "source":
                    "Copernicus Marine",

                "data_type":
                    data_type
            }
        )


    # ======================================================
    # TEMPERATURE ONLY
    # ======================================================

    if (
        "temperature" in q
        and
        "salinity" not in q
        and
        "current" not in q
        and
        "condition" not in q
    ):

        temperature = get_ocean_temperature(
            latitude,
            longitude,
            depth,
            target_time
        )


        if temperature.get(
            "success"
        ):

            answer = (

                "🌡️ Ocean Temperature\n\n"

                f"📍 Location: {place}\n"

                f"Latitude: {latitude:.4f}°\n"

                f"Longitude: {longitude:.4f}°\n\n"

                f"📅 Requested Date: "
                f"{requested_date}\n"

                f"Mode: {temporal_label}\n\n"

                f"Temperature: "
                f"{temperature.get('value')} "
                f"{temperature.get('unit')}\n\n"

                f"Data Time: "
                f"{temperature.get('time')}\n"

                f"Source: Copernicus Marine\n"

                f"Type: {data_type}"
            )

        else:

            answer = (

                "❌ Temperature data could not "
                f"be retrieved for {place}.\n\n"

                f"Requested Date: "
                f"{requested_date}\n\n"

                f"{temperature.get('error', '')}"
            )


        return jsonify(
            {
                "answer":
                    answer,

                "type":
                    "ocean_temperature",

                "location":
                    location,

                "requested_place":
                    place,

                "requested_depth":
                    depth,

                "requested_date":
                    requested_date,

                "temporal_mode":
                    temporal_mode,

                "temporal_label":
                    temporal_label,

                "temperature":
                    temperature,

                "source":
                    "Copernicus Marine",

                "data_type":
                    data_type
            }
        )


    # ======================================================
    # SALINITY ONLY
    # ======================================================

    if (
        "salinity" in q
        and
        "temperature" not in q
        and
        "current" not in q
        and
        "condition" not in q
    ):

        salinity = get_ocean_salinity(
            latitude,
            longitude,
            depth,
            target_time
        )


        if salinity.get(
            "success"
        ):

            answer = (

                "💧 Ocean Salinity\n\n"

                f"📍 Location: {place}\n"

                f"Latitude: {latitude:.4f}°\n"

                f"Longitude: {longitude:.4f}°\n\n"

                f"📅 Requested Date: "
                f"{requested_date}\n"

                f"Mode: {temporal_label}\n\n"

                f"Salinity: "
                f"{salinity.get('value')} "
                f"{salinity.get('unit')}\n\n"

                f"Data Time: "
                f"{salinity.get('time')}\n"

                f"Source: Copernicus Marine\n"

                f"Type: {data_type}"
            )

        else:

            answer = (

                "❌ Salinity data could not "
                f"be retrieved for {place}.\n\n"

                f"Requested Date: "
                f"{requested_date}\n\n"

                f"{salinity.get('error', '')}"
            )


        return jsonify(
            {
                "answer":
                    answer,

                "type":
                    "ocean_salinity",

                "location":
                    location,

                "requested_place":
                    place,

                "requested_depth":
                    depth,

                "requested_date":
                    requested_date,

                "temporal_mode":
                    temporal_mode,

                "temporal_label":
                    temporal_label,

                "salinity":
                    salinity,

                "source":
                    "Copernicus Marine",

                "data_type":
                    data_type
            }
        )


    # ======================================================
    # COMPLETE OCEAN CONDITIONS
    # ======================================================

    temperature = get_ocean_temperature(
        latitude,
        longitude,
        depth,
        target_time
    )


    salinity = get_ocean_salinity(
        latitude,
        longitude,
        depth,
        target_time
    )


    currents = get_ocean_currents(
        latitude,
        longitude,
        depth,
        target_time
    )


    # ------------------------------------------------------
    # BUILD TEXT RESPONSE
    # ------------------------------------------------------

    answer_lines = [

        f"🌊 {temporal_label}",

        "",

        f"📍 Location: {place}",

        f"Latitude: {latitude:.4f}°",

        f"Longitude: {longitude:.4f}°",

        "",

        f"📅 Requested Date: "
        f"{requested_date}",

        f"Mode: {data_type}",

        ""
    ]


    if temperature.get(
        "success"
    ):

        answer_lines.append(

            "🌡️ Temperature: "
            f"{temperature.get('value')} "
            f"{temperature.get('unit')}"
        )


    if salinity.get(
        "success"
    ):

        answer_lines.append(

            "💧 Salinity: "
            f"{salinity.get('value')} "
            f"{salinity.get('unit')}"
        )


    if currents.get(
        "success"
    ):

        answer_lines.append(

            "🌊 Current Speed: "
            f"{currents.get('speed')} "
            f"{currents.get('speed_unit')}"
        )


        answer_lines.append(

            "🧭 Current Direction: "
            f"{currents.get('direction_degrees')}° "
            f"({currents.get('direction')})"
        )


    # ------------------------------------------------------
    # DATA TIME
    # ------------------------------------------------------

    data_time = None


    if temperature.get(
        "success"
    ):

        data_time = temperature.get(
            "time"
        )


    elif salinity.get(
        "success"
    ):

        data_time = salinity.get(
            "time"
        )


    elif currents.get(
        "success"
    ):

        data_time = currents.get(
            "time"
        )


    if data_time:

        answer_lines.extend(
            [
                "",

                f"🕐 Model Data Time: "
                f"{data_time}"
            ]
        )


    # ------------------------------------------------------
    # ERRORS IF ALL DATA FAILED
    # ------------------------------------------------------

    successful_results = [

        temperature.get(
            "success"
        ),

        salinity.get(
            "success"
        ),

        currents.get(
            "success"
        )
    ]


    if not any(
        successful_results
    ):

        answer_lines.extend(
            [
                "",

                "❌ No operational ocean data "
                "was available for the requested "
                "location/date.",

                "",

                "Temperature: "
                + temperature.get(
                    "error",
                    "Unavailable"
                ),

                "Salinity: "
                + salinity.get(
                    "error",
                    "Unavailable"
                ),

                "Currents: "
                + currents.get(
                    "error",
                    "Unavailable"
                )
            ]
        )


    answer_lines.extend(
        [
            "",

            "Source: Copernicus Marine",

            f"Type: {data_type}"
        ]
    )


    answer = "\n".join(
        answer_lines
    )


    # ------------------------------------------------------
    # RETURN DASHBOARD DATA
    # ------------------------------------------------------

    return jsonify(
        {
            "answer":
                answer,

            "type":
                "ocean_conditions",

            "location":
                location,

            "requested_place":
                place,

            "requested_depth":
                depth,

            "requested_date":
                requested_date,

            "temporal_mode":
                temporal_mode,

            "temporal_label":
                temporal_label,

            "temperature":
                temperature,

            "salinity":
                salinity,

            "currents":
                currents,

            "source":
                "Copernicus Marine",

            "data_type":
                data_type
        }
    )


# ==========================================================
# ASK ROUTE
# ==========================================================

@app.route(
    "/ask",
    methods=["POST"]
)
def ask():

    try:

        data = request.get_json(
            silent=True
        ) or {}


        question = (
            data
            .get(
                "question",
                ""
            )
            .strip()
        )


        if not question:

            return jsonify(
                {
                    "answer":
                        "Please enter a question.",

                    "type":
                        "error"
                }
            )


        q = question.lower()


        # ==================================================
        # GLOBAL OCEAN ROUTER
        # ==================================================

        if is_global_ocean_question(
            question
        ):

            return handle_global_ocean_query(
                question
            )


        # ==================================================
        # ARGO TEMPERATURE
        # ==================================================

        if (
            "temperature" in q
            or
            "temp" in q
        ):

            summary = temperature_summary()


            answer = (

                "🌡️ ARGO Temperature Analysis\n\n"

                f"Average Temperature: "
                f"{summary['average']:.2f} °C\n"

                f"Minimum Temperature: "
                f"{summary['minimum']:.2f} °C\n"

                f"Maximum Temperature: "
                f"{summary['maximum']:.2f} °C"
            )


            visual_data = temperature_data(
                limit=1000
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "temperature",

                    "visualization":
                        visual_data
                }
            )


        # ==================================================
        # ARGO SALINITY
        # ==================================================

        if (
            "salinity" in q
            or
            "salt" in q
        ):

            summary = salinity_summary()


            answer = (

                "💧 ARGO Salinity Analysis\n\n"

                f"Average Salinity: "
                f"{summary['average']:.2f} PSU\n"

                f"Minimum Salinity: "
                f"{summary['minimum']:.2f} PSU\n"

                f"Maximum Salinity: "
                f"{summary['maximum']:.2f} PSU"
            )


            visual_data = salinity_data(
                limit=1000
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "salinity",

                    "visualization":
                        visual_data
                }
            )


        # ==================================================
        # NUMBER OF FLOATS
        # ==================================================

        if (
            "float" in q
            or
            "floats" in q
        ):

            summary = dataset_summary()


            number_of_floats = (

                summary.get(
                    "floats"
                )

                or

                summary.get(
                    "unique_floats"
                )

                or

                summary.get(
                    "number_of_floats"
                )

                or

                133
            )


            answer = (

                "🛰️ ARGO Floats\n\n"

                "The current ARGO dataset contains "

                f"{number_of_floats} "

                "unique profiling floats."
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "floats"
                }
            )


        # ==================================================
        # OBSERVATIONS
        # ==================================================

        if (
            "observation" in q
            or
            "observations" in q
            or
            "records" in q
        ):

            summary = dataset_summary()


            observations = (

                summary.get(
                    "observations"
                )

                or

                summary.get(
                    "number_of_observations"
                )

                or

                summary.get(
                    "records"
                )

                or

                101238
            )


            answer = (

                "📊 ARGO Observations\n\n"

                "The current ARGO dataset contains "

                f"{observations:,} "

                "observation records."
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "observations"
                }
            )


        # ==================================================
        # PRESSURE / DEPTH
        # ==================================================

        if (
            "pressure" in q
            or
            "depth" in q
        ):

            summary = dataset_summary()


            minimum_pressure = (

                summary.get(
                    "pressure_min"
                )

                or

                summary.get(
                    "minimum_pressure"
                )

                or

                0.0
            )


            maximum_pressure = (

                summary.get(
                    "pressure_max"
                )

                or

                summary.get(
                    "maximum_pressure"
                )

                or

                1000.44
            )


            answer = (

                "🌊 ARGO Pressure / Depth Range\n\n"

                f"Minimum Pressure: "
                f"{float(minimum_pressure):.2f} dbar\n"

                f"Maximum Pressure: "
                f"{float(maximum_pressure):.2f} dbar\n\n"

                "Pressure in oceanographic profiles "
                "is commonly used as an approximation "
                "for depth."
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "pressure"
                }
            )


        # ==================================================
        # ARGO LOCATION / MAP
        # ==================================================

        if (
            "location" in q
            or
            "map" in q
            or
            "coverage" in q
            or
            "where" in q
        ):

            visual_data = location_data(
                limit=1000
            )


            answer = (

                "📍 ARGO Geographic Coverage\n\n"

                "The current local ARGO dataset covers "
                "part of the Indian Ocean.\n\n"

                "Approximate dataset coverage:\n"

                "Latitude: -10° to 20°\n"

                "Longitude: 60° to 90°.\n\n"

                "The map below shows sampled ARGO "
                "observation locations."
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "location",

                    "visualization":
                        visual_data
                }
            )


        # ==================================================
        # DATASET SUMMARY
        # ==================================================

        if (
            "dataset" in q
            or
            "summary" in q
            or
            "data summary" in q
        ):

            summary = dataset_summary()


            answer = (

                "📊 ARGO Dataset Summary\n\n"

                "Current local ARGO dataset:\n"

                "• Region: Indian Ocean\n"

                "• Approx. Latitude: -10° to 20°\n"

                "• Approx. Longitude: 60° to 90°\n"

                "• Pressure: 0 to about 1000 dbar\n"

                "• Period: January-February 2025\n"

                "• Observations: 101,238\n"

                "• Unique floats: 133\n\n"

                "This dataset is used for the ARGO "
                "observation-analysis features of FloatChat."
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "dataset",

                    "data":
                        summary
                }
            )


        # ==================================================
        # HELP
        # ==================================================

        if (
            "help" in q
            or
            "what can you do" in q
            or
            "how to use" in q
        ):

            answer = (

                "🌊 FloatChat Help\n\n"

                "Global Ocean:\n"

                "• Ocean conditions in Maldives today\n"

                "• Ocean conditions in Maldives tomorrow\n"

                "• Ocean conditions in Maldives yesterday\n"

                "• Temperature near Arabian Sea tomorrow\n"

                "• Salinity in Indian Ocean today\n"

                "• Ocean current near Maldives tomorrow\n"

                "• Temperature in Bay of Bengal "
                "at 100 m tomorrow\n"

                "• Ocean conditions in Maldives "
                "on 2026-09-20\n\n"

                "ARGO Observations:\n"

                "• What is the average temperature?\n"

                "• What is the maximum salinity?\n"

                "• How many ARGO floats are there?\n"

                "• How many observations are there?\n"

                "• Show ARGO locations on map\n"

                "• Show dataset summary"
            )


            return jsonify(
                {
                    "answer":
                        answer,

                    "type":
                        "help"
                }
            )


        # ==================================================
        # DEFAULT
        # ==================================================

        answer = (

            "🤖 I could not fully understand "
            "that question.\n\n"

            "Try:\n\n"

            "• Ocean conditions in Maldives today\n"

            "• Ocean conditions in Maldives tomorrow\n"

            "• Temperature near Arabian Sea tomorrow\n"

            "• Salinity in Bay of Bengal\n"

            "• Ocean current near Maldives\n"

            "• What is the average temperature?\n"

            "• Show ARGO locations on map\n"

            "• Show dataset summary"
        )


        return jsonify(
            {
                "answer":
                    answer,

                "type":
                    "help"
            }
        )


    # ======================================================
    # SERVER ERROR
    # ======================================================

    except Exception as error:

        print(
            "FloatChat /ask error:",
            error
        )


        return jsonify(
            {
                "answer":
                    "❌ FloatChat encountered an error "
                    "while processing the request.\n\n"
                    f"Error: {str(error)}",

                "type":
                    "error"
            }
        ), 500


# ==========================================================
# RUN APPLICATION
# ==========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )