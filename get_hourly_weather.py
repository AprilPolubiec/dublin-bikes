import requests
import json
import datetime
import os
import sys
from web.db_utils import HourlyWeatherRow, insert_rows

latitude = 53.3498
longitude = -6.2672
W_HF_URI = "https://pro.openweathermap.org/data/2.5/forecast/hourly"
# Load API key from credentials file
script_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(script_dir, 'secure', 'credentials.json')
with open(credentials_path) as f:
    data = json.load(f)
    W_API = data["W_API"]
# Make the API request
response = requests.get(W_HF_URI, params={"units": "metric", "lat": latitude, "lon": longitude, "appid": W_API})
 # Check if request was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    hourly_rows = []
    for d in data["list"]:
        d_obj = {
            "forecast_date": datetime.datetime.fromtimestamp(d["dt"]),
            "humidity": d["main"]["humidity"],
            "feels_like": d["main"]["feels_like"],
            "pressure": d["main"]["pressure"],
            "pop": d["pop"],
            "temperature": d["main"]["temp"],
            # "uvi": d["main"]["uvi"], TODO: What is this?
            "weather_id": d["weather"][0]["id"],
            "wind_speed": d["wind"]["speed"],
            "wind_gust": d["wind"]["gust"],
        }
        if "rain" in d.keys():
            d_obj["rain_1h"] = d["rain"]["1h"]
        if "snow" in d.keys():
            d_obj["snow_1h"] = d["snow"]["1h"]
        hourly_rows.append(HourlyWeatherRow(d_obj))
    insert_rows(hourly_rows, HourlyWeatherRow.table)
else:
    print('Failed to retrieve weather data')