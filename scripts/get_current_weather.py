import requests
import json
import datetime
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from web.db_utils import CurrentWeatherRow, insert_row

latitude = 53.3498
longitude = -6.2672
W_C_URI = "https://api.openweathermap.org/data/2.5/weather"
# Load API key from credentials file
with open("secure/credentials.json") as f:
    data = json.load(f)
    W_API = data["W_API"]
# Make the API request
response = requests.get(W_C_URI, params={"units": "metric", "lat": latitude, "lon": longitude, "appid": W_API})

if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    current_row = CurrentWeatherRow({
        "forecast_date": datetime.datetime.fromtimestamp(data["dt"]),
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        # TODO: better validation on datetimes
        "sunrise": datetime.datetime.fromtimestamp(data["sys"]["sunrise"]),
        "sunset": datetime.datetime.fromtimestamp(data["sys"]["sunset"]),
        "temperature": data["main"]["temp"],
        "weather_id": data["weather"][0]["id"],
        "wind_speed": data["wind"]["speed"],
        "wind_gust": 0.0,
        "wind_1h": 0.0,
        "rain_1h": 0.0,
        "uvi": 0.0
    })
    insert_row(current_row, CurrentWeatherRow.table)
else:
    print('Failed to retrieve weather data')
