import requests
import json
import datetime
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from web.db_utils import DailyWeatherRow, insert_rows

latitude = 53.3498
longitude = -6.2672
W_DF_URI = "https://pro.openweathermap.org/data/2.5/forecast/daily"
# Load API key from credentials file
with open("secure/credentials.json") as f:
    data = json.load(f)
    W_API = data["W_API"]
# Make the API request
response = requests.get(W_DF_URI, params={"units": "metric", "cnt": "16", "lat": latitude, "lon": longitude, "appid": W_API})
 # Check if request was successful

# Check if request was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    daily_rows = []
    for d in data["list"]:
        d_obj = {
            "forecast_date": datetime.datetime.fromtimestamp(d["dt"]),
            "humidity": d["humidity"],
            "pressure": d["pressure"],
            "pop": d["pop"],
            "temperature_max": d["temp"]["max"],
            "temperature_min": d["temp"]["min"],
            # "uvi": d["uvi"], TODO: What is this?
            "weather_id": d["weather"][0]["id"],
            "wind_speed": d["speed"],
            "wind_gust": d["gust"],
        }
        if "rain" in d.keys():
            d_obj["rain"] = d["rain"]
        if "snow" in d.keys():
            d_obj["snow"] = d["snow"]
        daily_rows.append(DailyWeatherRow(d_obj))
    insert_rows(daily_rows, DailyWeatherRow.table)
else:
    print('Failed to retrieve weather data')
