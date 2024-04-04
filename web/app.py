from flask import Flask, render_template, request, jsonify
from . import db_utils as db_utils
import os
import json
import pickle
import datetime

# from prediction import predict_bike_availability

app = Flask(__name__)


@app.route("/")
def root():
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "secure/credentials.json",
    )
    f = open(file_path)
    data = json.load(f)
    api_key = data["GOOGLE_MAPS_KEY"]
    return render_template("index.html", apiKey=api_key)


@app.route("/stations")
def get_stations():
    stations = db_utils.get_stations()
    return stations


@app.route("/stations/<int:station_id>")
def get_station(station_id):
    db_utils.get_station(station_id)


@app.route("/predicted-availability/<int:station_id>")
# @functools.lru_cache(maxsize=128)
def get_predicted_availability(station_id):
    prediction_date = request.args.get("date_timestamp", type=float)
    # Get the forecast for the date & time
    try:
        forecast = db_utils.get_weather_forecast(prediction_date)
        print("forecast: ", forecast)
    except Exception as e:
        print("failed: ", e)
        return e, 400

    pkl_filename = f"model_{station_id}.pkl"
    with open(f"../models/linear-v1/{pkl_filename}", "rb") as file:
        model = pickle.load(file)
    # Pull the features out of the forecast
    FEATURE_COLUMNS = [
        "FeelsLike",
        "Humidity",
        "Pressure",
        "Temperature",
        "day",
        "month",
        "hour",
        "is_weekday",
        "minute",
        "cold_weather",
        "windy_weather",
    ]

    feels_like = forecast["FeelsLike"]
    humidity = forecast["Humidity"]
    pressure = forecast["Pressure"]
    temperature = forecast["Temperature"]

    day = datetime.datetime.fromtimestamp(prediction_date).day
    month = datetime.datetime.fromtimestamp(prediction_date).month
    hour = datetime.datetime.fromtimestamp(prediction_date).hour
    minute = datetime.datetime.fromtimestamp(prediction_date).minute
    is_weekday = 1 if day >= 0 and day <= 4 else 0
    cold_weather = 1 if forecast["Temperature"] < 5 else 0
    windy_weather = 1 if forecast["WindSpeed"] > 8 else 0
    x_values = [
        [
            feels_like,
            humidity,
            pressure,
            temperature,
            day,
            month,
            hour,
            is_weekday,
            minute,
            cold_weather,
            windy_weather,
        ]
    ]
    prediction = model.predict(x_values)
    print("Prediction: ", prediction)
    print("[0]: ", prediction[0])
    return {
        "station_id": station_id,
        "availability": str(round(prediction[0])),
        "forecast": forecast,
    }


@app.route("/predicted-availabilities")
# @functools.lru_cache(maxsize=128)
def get_predicted_availabilities():
    prediction_date = request.args.get("date_timestamp", type=float)
    # Get the forecast for the date & time
    try:
        forecast = db_utils.get_weather_forecast(prediction_date)
        print("forecast: ", forecast)
    except Exception as e:
        print("failed: ", e)
        return e, 400

    feels_like = forecast["FeelsLike"]
    humidity = forecast["Humidity"]
    pressure = forecast["Pressure"]
    temperature = forecast["Temperature"]

    day = datetime.datetime.fromtimestamp(prediction_date).day
    month = datetime.datetime.fromtimestamp(prediction_date).month
    hour = datetime.datetime.fromtimestamp(prediction_date).hour
    minute = datetime.datetime.fromtimestamp(prediction_date).minute
    is_weekday = 1 if day >= 0 and day <= 4 else 0
    cold_weather = 1 if forecast["Temperature"] < 5 else 0
    windy_weather = 1 if forecast["WindSpeed"] > 8 else 0
    x_values = [
        [
            feels_like,
            humidity,
            pressure,
            temperature,
            day,
            month,
            hour,
            is_weekday,
            minute,
            cold_weather,
            windy_weather,
        ]
    ]
    res = {"forecast": forecast, "stand_predictions": {}, "bike_predictions": {}}

    stations = db_utils.get_stations()
    for station in stations:
        pkl_filename = f"model_{station['Id']}.pkl"
        with open(f"../models/stands-and-bikes/{pkl_filename}", "rb") as file:
            model = pickle.load(file)

        prediction = model.predict(x_values)
        res["stand_predictions"][station["Id"]] = str(round(prediction[0][0]))
        res["bike_predictions"][station["Id"]] = str(round(prediction[0][1]))
    return res


# Utility function
def to_date(date_str):
    try:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
        return dt
    except:
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt


@app.route("/historical-availability/<int:station_id>")
def get_historical_availabilities(station_id):
    historical_availability = db_utils.get_historical_availabilities(station_id, 30)

    stands = {  # By hour
        "hours": {},
        # By day
        "days": {
            0: [],  # MON
            1: [],  # TUE
            2: [],  # WED
            3: [],  # THURS
            4: [],  # FRI
            5: [],  # SAT
            6: [],  # SUN
        },
    }
    bikes = {  # By hour
        "hours": {},
        # By day
        "days": {
            0: [],  # MON
            1: [],  # TUE
            2: [],  # WED
            3: [],  # THURS
            4: [],  # FRI
            5: [],  # SAT
            6: [],  # SUN
        },
    }
    for a in historical_availability:
        date = to_date(a["LastUpdated"])
        day_of_week = date.weekday()
        hour = to_date(a["LastUpdated"]).hour

        stands["days"][day_of_week].append(a["StandsAvailable"])
        if hour not in stands["hours"].keys():
            stands["hours"][hour] = []
        stands["hours"][hour].append(a["StandsAvailable"])

        if a["MechanicalBikesAvailable"] == None or a["ElectricBikesAvailable"] == None:
            continue
        bikes["days"][day_of_week].append(
            a["MechanicalBikesAvailable"] + a["ElectricBikesAvailable"]
        )
        if hour not in bikes["hours"].keys():
            bikes["hours"][hour] = []
        bikes["hours"][hour].append(a["MechanicalBikesAvailable"] + a["ElectricBikesAvailable"])

    for key in bikes["days"].keys():
        avg = sum(bikes["days"][key]) / len(bikes["days"][key])
        bikes["days"][key] = avg
    
    for key in stands["days"].keys():
        avg = sum(stands["days"][key]) / len(stands["days"][key])
        stands["days"][key] = avg

    for key in bikes["hours"].keys():
        avg = sum(bikes["hours"][key]) / len(bikes["hours"][key])
        bikes["hours"][key] = avg
    
    for key in stands["hours"].keys():
        avg = sum(stands["hours"][key]) / len(stands["hours"][key])
        stands["hours"][key] = avg
    
    return {"bikes": bikes, "stands": stands}


@app.route("/availability")
def get_availabilities():
    availabilities = db_utils.get_availabilities()
    return availabilities


@app.route("/current-weather")
def get_current_weather():
    current_weather = db_utils.get_current_weather()
    return current_weather


# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)
