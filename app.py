from flask import Flask, request, jsonify, render_template

from data.argo_data import (
    temperature_summary,
    salinity_summary,
    dataset_summary
)

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()

    if not data:
        return jsonify({
            "answer": "Please enter a question."
        })

    question = data.get("question", "").strip()

    if not question:
        return jsonify({
            "answer": "Please enter a question."
        })

    q = question.lower()

    # ---------------------------------------
    # TEMPERATURE QUESTIONS
    # ---------------------------------------
    if "temperature" in q or "temp" in q:

        result = temperature_summary()

        answer = (
            f"🌡️ ARGO Temperature Analysis\n\n"
            f"Average Temperature: {result['average']} °C\n"
            f"Minimum Temperature: {result['minimum']} °C\n"
            f"Maximum Temperature: {result['maximum']} °C\n"
            f"Observations: {result['count']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "temperature",
            "data": result
        })

    # ---------------------------------------
    # SALINITY QUESTIONS
    # ---------------------------------------
    elif "salinity" in q or "salinity level" in q:

        result = salinity_summary()

        answer = (
            f"💧 ARGO Salinity Analysis\n\n"
            f"Average Salinity: {result['average']} PSU\n"
            f"Minimum Salinity: {result['minimum']} PSU\n"
            f"Maximum Salinity: {result['maximum']} PSU\n"
            f"Observations: {result['count']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "salinity",
            "data": result
        })

    # ---------------------------------------
    # FLOAT QUESTIONS
    # ---------------------------------------
    elif (
        "float" in q
        or "floats" in q
        or "platform" in q
    ):

        result = dataset_summary()

        answer = (
            f"📍 ARGO Float Information\n\n"
            f"Number of ARGO Floats: {result['floats']:,}\n"
            f"Total Observations: {result['observations']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "dataset",
            "data": result
        })

    # ---------------------------------------
    # OBSERVATION QUESTIONS
    # ---------------------------------------
    elif (
        "observation" in q
        or "observations" in q
        or "data points" in q
        or "records" in q
    ):

        result = dataset_summary()

        answer = (
            f"📊 ARGO Dataset Information\n\n"
            f"Total Observations: {result['observations']:,}\n"
            f"ARGO Floats: {result['floats']:,}"
        )

        return jsonify({
            "answer": answer,
            "type": "dataset",
            "data": result
        })

    # ---------------------------------------
    # DEPTH QUESTIONS
    # ---------------------------------------
    elif (
        "depth" in q
        or "deep" in q
        or "pressure" in q
    ):

        result = dataset_summary()

        answer = (
            f"🌊 ARGO Depth Information\n\n"
            f"Minimum Depth: {result['depth_min']} meters\n"
            f"Maximum Depth: {result['depth_max']} meters"
        )

        return jsonify({
            "answer": answer,
            "type": "depth",
            "data": result
        })

    # ---------------------------------------
    # LOCATION QUESTIONS
    # ---------------------------------------
    elif (
        "location" in q
        or "latitude" in q
        or "longitude" in q
        or "region" in q
    ):

        result = dataset_summary()

        answer = (
            f"📍 ARGO Geographic Coverage\n\n"
            f"Latitude: {result['latitude_min']}° "
            f"to {result['latitude_max']}°\n"
            f"Longitude: {result['longitude_min']}° "
            f"to {result['longitude_max']}°"
        )

        return jsonify({
            "answer": answer,
            "type": "location",
            "data": result
        })

    # ---------------------------------------
    # GENERAL DATASET QUESTION
    # ---------------------------------------
    elif (
        "dataset" in q
        or "data" in q
        or "argo" in q
    ):

        result = dataset_summary()

        answer = (
            f"🌊 FloatChat ARGO Dataset\n\n"
            f"Observations: {result['observations']:,}\n"
            f"ARGO Floats: {result['floats']:,}\n"
            f"Latitude Range: {result['latitude_min']}° "
            f"to {result['latitude_max']}°\n"
            f"Longitude Range: {result['longitude_min']}° "
            f"to {result['longitude_max']}°\n"
            f"Depth Range: {result['depth_min']} "
            f"to {result['depth_max']} meters"
        )

        return jsonify({
            "answer": answer,
            "type": "dataset",
            "data": result
        })

    # ---------------------------------------
    # UNKNOWN QUESTION
    # ---------------------------------------
    else:

        answer = (
            "🤖 I can currently analyze ARGO ocean data related to:\n\n"
            "🌡️ Temperature\n"
            "💧 Salinity\n"
            "📍 Location\n"
            "🌊 Depth\n"
            "🛰️ ARGO Floats\n"
            "📊 Observations\n\n"
            "Try asking something like:\n"
            "\"What is the average temperature?\""
        )

        return jsonify({
            "answer": answer,
            "type": "help"
        })


if __name__ == "__main__":
    app.run(debug=True)
    