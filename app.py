from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("OPENWEATHER_API_KEY")  # set this in your environment or .env

def fetch_current_weather(city, api_key):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def fetch_forecast(city, api_key):
    # 5 day / 3 hour forecast
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {"q": city, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

def parse_current(data):
    return {
        "city": data.get("name"),
        "country": data.get("sys", {}).get("country"),
        "description": data.get("weather", [{}])[0].get("description", "").capitalize(),
        "temp": data.get("main", {}).get("temp"),
        "feels_like": data.get("main", {}).get("feels_like"),
        "humidity": data.get("main", {}).get("humidity"),
        "pressure": data.get("main", {}).get("pressure"),
        "wind_speed": data.get("wind", {}).get("speed"),
        "icon": data.get("weather", [{}])[0].get("icon")
    }

def parse_forecast(data, max_points=24):
    items = []
    for entry in data.get("list", [])[:max_points]:
        dt_obj = datetime.strptime(entry.get("dt_txt"), "%Y-%m-%d %H:%M:%S")
        formatted = dt_obj.strftime("%a %I %p")  # Thu 03 PM
        items.append({
            "dt": entry.get("dt"),
            "dt_txt": formatted,
            "temp": float(entry.get("main", {}).get("temp", 0)),
            "feels_like": float(entry.get("main", {}).get("feels_like", 0)),
            "humidity": int(entry.get("main", {}).get("humidity", 0)),
            "weather": entry.get("weather", [{}])[0].get("description", "").capitalize(),
            "icon": entry.get("weather", [{}])[0].get("icon")
        })
    return items

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    current = None
    forecast = None
    city = None

    if request.method == "POST":
        city = request.form.get("city", "").strip()
        if not city:
            error = "Please enter a city name."
        else:
            api_key = API_KEY
            if not api_key:
                error = "Missing API key. Set OPENWEATHER_API_KEY environment variable."
            else:
                try:
                    cur_data = fetch_current_weather(city, api_key)
                    fc_data = fetch_forecast(city, api_key)
                    # OpenWeather may return cod != 200 inside JSON; check
                    if str(cur_data.get("cod")) not in ("200", "200.0"):
                        error = f"API error: {cur_data.get('message', 'Unknown')}"
                    elif str(fc_data.get("cod")) not in ("200", "200.0"):
                        error = f"API error: {fc_data.get('message', 'Unknown')}"
                    else:
                        current = parse_current(cur_data)
                        forecast = parse_forecast(fc_data)
                        city = f"{current.get('city')},{current.get('country')}" if current.get('country') else current.get('city')
                except requests.exceptions.HTTPError as e:
                    # try to extract message from response if available
                    try:
                        msg = e.response.json().get("message", str(e))
                    except Exception:
                        msg = str(e)
                    error = f"HTTP error: {msg}"
                except requests.exceptions.Timeout:
                    error = "Request timed out. Try again."
                except requests.exceptions.RequestException as e:
                    error = f"Network error: {e}"
                except Exception as e:
                    error = f"Unexpected error: {e}"

    return render_template("index.html", city=city, current=current, forecast=forecast, error=error)

if __name__ == "__main__":
    # For development only. Use a proper WSGI server in production.
    app.run(debug=True, host="0.0.0.0", port=5000)
from flask import jsonify

@app.route("/api/weather", methods=["GET"])
def api_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "Please provide a city"}), 400

    try:
        cur_data = fetch_current_weather(city, API_KEY)
        fc_data = fetch_forecast(city, API_KEY)

        current = parse_current(cur_data)
        forecast = parse_forecast(fc_data)

        return jsonify({
            "city": current.get("city"),
            "country": current.get("country"),
            "current": current,
            "forecast": forecast
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500