import requests
import json
import datetime
from web.db_utils import CurrentWeatherRow, HourlyWeatherRow, DailyWeatherRow, insert_row, insert_rows

def get_weather():
    city = 'Dublin'
    latitude = 53.3498
    longitude = -6.2672
    W_C_URI = "https://api.openweathermap.org/data/2.5/weather"
    W_HF_URI = "https://pro.openweathermap.org/data/2.5/forecast/hourly"
    W_DF_URI = "https://pro.openweathermap.org/data/2.5/forecast/daily"
    # Load API key from credentials file
    with open("secure/credentials.json") as f:
        data = json.load(f)
        W_API = data["W_API"]
    # Make the API request
    # opencall_response = requests.get("https://api.openweathermap.org/data/3.0/onecall", params={"units": "metric", "lat": latitude, "lon": longitude, "appid": W_API, "exclude": ["minutely", "alerts"]})
    current_response = requests.get(W_C_URI, params={"units": "metric", "lat": latitude, "lon": longitude, "appid": W_API})
    hourly_response = requests.get(W_HF_URI, params={"units": "metric", "lat": latitude, "lon": longitude, "appid": W_API})
    daily_response = requests.get(W_DF_URI, params={"units": "metric", "cnt": "16", "lat": latitude, "lon": longitude, "appid": W_API})

    # Check if request was successful
    if current_response.status_code == 200:
        # Parse JSON response
        data = current_response.json()
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

    # Check if request was successful
    if hourly_response.status_code == 200:
        # Parse JSON response
        data = hourly_response.json()
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
    
    # Check if request was successful
    if daily_response.status_code == 200:
        # Parse JSON response
        data = daily_response.json()
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


get_weather()