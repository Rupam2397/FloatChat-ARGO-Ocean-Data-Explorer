from flask import Flask, request, jsonify, render_template

from data.argo_data import (
    temperature_summary,
    salinity_summary,
    dataset_summary,
    temperature_data,
    salinity_data,
    location_data
)


app = Flask(__name__)


# ==================================================
# HOME PAGE
# ==================================================

@app.route("/")
def home():
    return render_template("index.html")


# ==================================================
# ASK FLOATCHAT
# ==================================================

@app.route("/ask", methods=["POST"])
def ask():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "answer": "Please enter a question.",
            "type": "help"
        })

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question.",
            "type": "help"
        })

    q = question.lower()


    # ==================================================
    # TEMPERATURE
    # ==================================================

    if "temperature" in q or "temp" in q:

        result = temperature_summary()

        if "average" in q or "mean" in q:

            answer = (
                "🌡️ Average ARGO Temperature\n\n"
                f"{result['average']} °C"
            )

        elif (
            "minimum" in q
            or "lowest" in q
            or "min" in q
        ):

            answer = (
                "🌡️ Minimum ARGO Temperature\n\n"
                f"{result['minimum']} °C"
            )

        elif (
            "maximum" in q
            or "highest" in q
            or "max" in q
        ):

            answer = (
                "🌡️ Maximum ARGO Temperature\n\n"
                f"{result['maximum']} °C"
            )

        elif (
            "count" in q
            or "observations" in q
            or "records" in q
        ):

            answer = (
                "🌡️ Temperature Observations\n\n"
                f"{result['count']:,}"
            )

        else:

            answer = (
                "🌡️ ARGO Temperature Analysis\n\n"
                f"Average Temperature: {result['average']} °C\n"
                f"Minimum Temperature: {result['minimum']} °C\n"
                f"Maximum Temperature: {result['maximum']} °C\n"
                f"Observations: {result['count']:,}"
            )

        return jsonify({
            "answer": answer,
            "type": "temperature",
            "data": result,
            "visualization": temperature_data()
        })


    # ==================================================
    # SALINITY
    # ==================================================

    elif "salinity" in q or "salty" in q:

        result = salinity_summary()

        if "average" in q or "mean" in q:

            answer = (
                "💧 Average ARGO Salinity\n\n"
                f"{result['average']} PSU"
            )

        elif (
            "minimum" in q
            or "lowest" in q
            or "min" in q
        ):

            answer = (
                "💧 Minimum ARGO Salinity\n\n"
                f"{result['minimum']} PSU"
            )

        elif (
            "maximum" in q
            or "highest" in q
            or "max" in q
        ):

            answer = (
                "💧 Maximum ARGO Salinity\n\n"
                f"{result['maximum']} PSU"
            )

        elif (
            "count" in q
            or "observations" in q
            or "records" in q
        ):

            answer = (
                "💧 Salinity Observations\n\n"
                f"{result['count']:,}"
            )

        else:

            answer = (
                "💧 ARGO Salinity Analysis\n\n"
                f"Average Salinity: {result['average']} PSU\n"
                f"Minimum Salinity: {result['minimum']} PSU\n"
                f"Maximum Salinity: {result['maximum']} PSU\n"
                f"Observations: {result['count']:,}"
            )

        return jsonify({
            "answer": answer,
            "type": "salinity",
            "data": result,
            "visualization": salinity_data()
        })


    # ==================================================
    # FLOATS
    # ==================================================

    elif (
        "float" in q
        or "floats" in q
        or "platform" in q
    ):

        result = dataset_summary()

        answer = (
            "🛰️ ARGO Float Information\n\n"
            f"Number of unique ARGO floats: "
            f"{result['floats']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "floats",
            "data": result
        })


    # ==================================================
    # OBSERVATIONS
    # ==================================================

    elif (
        "observation" in q
        or "observations" in q
        or "records" in q
        or "data points" in q
    ):

        result = dataset_summary()

        answer = (
            "📊 ARGO Observations\n\n"
            f"Total observations: "
            f"{result['observations']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "observations",
            "data": result
        })


    # ==================================================
    # PRESSURE / DEPTH-RELATED QUESTIONS
    # ==================================================

    elif (
        "pressure" in q
        or "depth" in q
        or "deep" in q
    ):

        result = dataset_summary()

        if (
            "minimum" in q
            or "lowest" in q
            or "min" in q
        ):

            answer = (
                "🌊 Minimum ARGO Pressure\n\n"
                f"{result['pressure_min']} dbar"
            )

        elif (
            "maximum" in q
            or "highest" in q
            or "max" in q
            or "deepest" in q
        ):

            answer = (
                "🌊 Maximum ARGO Pressure\n\n"
                f"{result['pressure_max']} dbar"
            )

        else:

            answer = (
                "🌊 ARGO Pressure Range\n\n"
                f"Minimum Pressure: "
                f"{result['pressure_min']} dbar\n"
                f"Maximum Pressure: "
                f"{result['pressure_max']} dbar\n\n"
                "Note: PRES represents pressure in the ARGO "
                "dataset and is not treated as exact depth."
            )

        return jsonify({
            "answer": answer,
            "type": "pressure",
            "data": result
        })


    # ==================================================
    # LOCATION / MAP
    # ==================================================

    elif (
        "location" in q
        or "latitude" in q
        or "longitude" in q
        or "region" in q
        or "coverage" in q
        or "map" in q
    ):

        result = dataset_summary()

        if (
            "latitude" in q
            and "longitude" not in q
        ):

            answer = (
                "📍 ARGO Latitude Coverage\n\n"
                f"{result['latitude_min']}° "
                f"to {result['latitude_max']}°"
            )

        elif (
            "longitude" in q
            and "latitude" not in q
        ):

            answer = (
                "📍 ARGO Longitude Coverage\n\n"
                f"{result['longitude_min']}° "
                f"to {result['longitude_max']}°"
            )

        else:

            answer = (
                "📍 ARGO Geographic Coverage\n\n"
                f"Latitude: "
                f"{result['latitude_min']}° "
                f"to {result['latitude_max']}°\n"
                f"Longitude: "
                f"{result['longitude_min']}° "
                f"to {result['longitude_max']}°"
            )

        return jsonify({
            "answer": answer,
            "type": "location",
            "data": result,
            "visualization": location_data()
        })


    # ==================================================
    # GENERAL DATASET
    # ==================================================

    elif (
        "dataset" in q
        or "argo data" in q
        or "summary" in q
    ):

        result = dataset_summary()

        answer = (
            "🌊 FloatChat ARGO Dataset\n\n"
            f"Observations: "
            f"{result['observations']:,}\n"
            f"ARGO Floats: "
            f"{result['floats']:,}\n"
            f"Latitude: "
            f"{result['latitude_min']}° "
            f"to {result['latitude_max']}°\n"
            f"Longitude: "
            f"{result['longitude_min']}° "
            f"to {result['longitude_max']}°\n"
            f"Pressure: "
            f"{result['pressure_min']} "
            f"to {result['pressure_max']} dbar"
        )

        return jsonify({
            "answer": answer,
            "type": "dataset",
            "data": result
        })


    # ==================================================
    # HELP
    # ==================================================

    else:

        answer = (
            "🤖 I couldn't understand that ARGO question yet.\n\n"
            "Currently I can analyze:\n"
            "🌡️ Temperature\n"
            "💧 Salinity\n"
            "🌊 Pressure / depth-related data\n"
            "📍 Geographic coverage\n"
            "🛰️ ARGO floats\n"
            "📊 Observations\n\n"
            "Try asking:\n"
            "• What is the average temperature?\n"
            "• Show temperature data\n"
            "• What is the maximum salinity?\n"
            "• Show salinity data\n"
            "• How many ARGO floats are there?\n"
            "• How many observations are there?\n"
            "• What is the pressure range?\n"
            "• Show ARGO locations on map\n"
            "• Give me the dataset summary"
        )

        return jsonify({
            "answer": answer,
            "type": "help"
        })


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":
    app.run(debug=True)