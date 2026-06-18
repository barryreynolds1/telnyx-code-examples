#!/usr/bin/env python3
"""Bulk Number Validation & Cleaner — validate and clean phone number lists via Telnyx Number Lookup API."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}
validation_jobs = []

@app.route("/validate", methods=["POST"])
def validate_numbers():
    data = request.get_json()
    if not data:
        return jsonify({"error": "invalid request body"}), 400
    numbers = data.get("numbers", [])
    if not numbers:
        return jsonify({"error": "numbers list required"}), 400
    job_id = f"JOB-{int(time.time())}"
    results = {"valid": [], "invalid": [], "mobile": [], "landline": [], "voip": [], "errors": []}
    for num in numbers[:100]:
        try:
            resp = requests.get(f"{API}/number_lookup/{num}", headers=headers, timeout=10)
            if resp.ok:
                info = resp.json().get("data", {})
                entry = {"number": num, "valid": info.get("valid", False),
                    "carrier": info.get("carrier", {}).get("name"),
                    "type": info.get("carrier", {}).get("type"),
                    "country": info.get("country_code"),
                    "national_format": info.get("national_format")}
                if info.get("valid"):
                    results["valid"].append(entry)
                    carrier_type = info.get("carrier", {}).get("type", "")
                    if carrier_type == "mobile":
                        results["mobile"].append(num)
                    elif carrier_type == "landline":
                        results["landline"].append(num)
                    elif carrier_type == "voip":
                        results["voip"].append(num)
                else:
                    results["invalid"].append(entry)
            else:
                results["errors"].append({"number": num, "error": "lookup_failed"})
        except Exception:
            results["errors"].append({"number": num, "error": "timeout"})
    summary = {"job_id": job_id, "total": len(numbers[:100]),
        "valid": len(results["valid"]), "invalid": len(results["invalid"]),
        "mobile": len(results["mobile"]), "landline": len(results["landline"]),
        "voip": len(results["voip"]), "errors": len(results["errors"]),
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ")}
    job = {"summary": summary, "results": results}
    validation_jobs.append(job)
    return jsonify(job), 200

@app.route("/validate/single/<number>", methods=["GET"])
def validate_single(number):
    try:
        resp = requests.get(f"{API}/number_lookup/{number}", headers=headers, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/jobs", methods=["GET"])
def list_jobs():
    summaries = [j["summary"] for j in validation_jobs[-20:]]
    return jsonify({"jobs": summaries}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "jobs": len(validation_jobs)}), 200

if __name__ == "__main__":
    app.run(debug=False, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "5000")))
