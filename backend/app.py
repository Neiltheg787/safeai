import itertools
import os
import time

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(
    app,
    resources={
        r"/*": {
            "origins": ["http://localhost:3000"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    },
)

_request_counter = itertools.count(1)


def _mock_threats(request_number):
    """Return a scripted threat periodically so the dashboard remains demonstrable."""
    try:
        interval = max(0, int(os.getenv("MOCK_THREAT_EVERY", "10")))
    except ValueError:
        interval = 10

    force_threat = request.args.get("forceThreat") == "1"
    if not force_threat and (interval == 0 or request_number % interval != 0):
        return []

    return [
        {
            "bbox": [64, 64, 192, 192],
            "confidence": 0.92,
            "level": "HIGH",
            "type": "mock weapon",
            "timestamp": time.time(),
        }
    ]


@app.route("/detect", methods=["POST", "OPTIONS"])
@app.route("/api/detect", methods=["POST", "OPTIONS"])
def detect_threats():
    if request.method == "OPTIONS":
        return app.make_default_options_response()

    data = request.get_json(silent=True)
    if not data or not isinstance(data.get("image"), str):
        return jsonify({"error": "No image data provided"}), 400

    image_data = data["image"]
    processed_image = image_data.split(",", 1)[1] if "," in image_data else image_data
    request_number = next(_request_counter)

    return jsonify(
        {
            "demo_mode": True,
            "processed_image": processed_image,
            "threats": _mock_threats(request_number),
            "timestamp": time.time(),
        }
    )


@app.route("/health", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify(
        {
            "status": "healthy",
            "model_loaded": True,
            "device": "vercel-mock",
            "demo_mode": True,
            "timestamp": time.time(),
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8000")), debug=True)
