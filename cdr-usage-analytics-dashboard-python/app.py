#!/usr/bin/env python3
"""CDR Usage Analytics Dashboard — pull Call Detail Records, build usage analytics with cost breakdowns and trend analysis."""
import os, json, time, requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify
load_dotenv()
app = Flask(__name__)
TELNYX_API_KEY = os.getenv("TELNYX_API_KEY")
API = "https://api.telnyx.com/v2"
headers = {"Authorization": f"Bearer {TELNYX_API_KEY}", "Content-Type": "application/json"}

@app.route("/cdrs", methods=["GET"])
def get_cdrs():
    start = request.args.get("start_date", time.strftime("%Y-%m-%d", time.gmtime(time.time() - 86400)))
    end = request.args.get("end_date", time.strftime("%Y-%m-%d"))
    page_size = request.args.get("page_size", "25")
    try:
        resp = requests.get(f"{API}/reports/cdrs", headers=headers,
            params={"filter[start_date]": start, "filter[end_date]": end,
                "page[size]": page_size}, timeout=15)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics/summary", methods=["GET"])
def usage_summary():
    start = request.args.get("start_date", time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400)))
    end = request.args.get("end_date", time.strftime("%Y-%m-%d"))
    try:
        resp = requests.get(f"{API}/reports/cdrs", headers=headers,
            params={"filter[start_date]": start, "filter[end_date]": end, "page[size]": 250}, timeout=30)
        cdrs = resp.json().get("data", [])
        total_calls = len(cdrs)
        total_duration = sum(float(c.get("duration_secs", 0)) for c in cdrs)
        total_cost = sum(float(c.get("cost", 0)) for c in cdrs)
        by_direction = {"inbound": 0, "outbound": 0}
        by_type = {}
        for c in cdrs:
            d = c.get("direction", "unknown")
            by_direction[d] = by_direction.get(d, 0) + 1
            t = c.get("call_type", "unknown")
            by_type[t] = by_type.get(t, 0) + 1
        avg_duration = total_duration / max(total_calls, 1)
        avg_cost = total_cost / max(total_calls, 1)
        return jsonify({"period": {"start": start, "end": end},
            "total_calls": total_calls, "total_duration_mins": round(total_duration / 60, 1),
            "total_cost_usd": round(total_cost, 2),
            "avg_duration_secs": round(avg_duration, 1), "avg_cost_usd": round(avg_cost, 4),
            "by_direction": by_direction, "by_type": by_type}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics/top-numbers", methods=["GET"])
def top_numbers():
    try:
        resp = requests.get(f"{API}/reports/cdrs", headers=headers,
            params={"filter[start_date]": time.strftime("%Y-%m-%d", time.gmtime(time.time() - 7 * 86400)),
                "page[size]": 250}, timeout=30)
        cdrs = resp.json().get("data", [])
        number_counts = {}
        for c in cdrs:
            num = c.get("from", "")
            number_counts[num] = number_counts.get(num, 0) + 1
        top = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        return jsonify({"top_numbers": [{"number": n, "calls": c} for n, c in top]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/analytics/daily", methods=["GET"])
def daily_breakdown():
    days = int(request.args.get("days", 7))
    daily = []
    for i in range(days):
        date = time.strftime("%Y-%m-%d", time.gmtime(time.time() - i * 86400))
        try:
            resp = requests.get(f"{API}/reports/cdrs", headers=headers,
                params={"filter[start_date]": date, "filter[end_date]": date, "page[size]": 250}, timeout=15)
            cdrs = resp.json().get("data", [])
            daily.append({"date": date, "calls": len(cdrs),
                "cost": round(sum(float(c.get("cost", 0)) for c in cdrs), 2)})
        except Exception:
            daily.append({"date": date, "calls": 0, "cost": 0})
    return jsonify({"daily": daily}), 200

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
