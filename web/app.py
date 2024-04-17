from flask import Flask, render_template, request, make_response
import db_utils as db_utils
import os
import json
import pickle
import datetime


# from prediction import predict_bike_availability

app = Flask(__name__)


@app.route("/")
def root():
    """ Root endpoint - renders frontend
    """
    try:
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "secure/credentials.json",
        )
        f = open(file_path)
        data = json.load(f)
        api_key = data["GOOGLE_MAPS_KEY"]
        return render_template("index.html", apiKey=api_key)
    except Exception as e:
        return f"Failed to load page: {e}", 500


@app.route("/stations")
def get_stations():
    try:
        stations = db_utils.get_stations()
        return stations, 200
    except Exception as e:
        return f"failed to get stations: {e}", 500

# TODO
# @app.errorhandler(404)
# def not_found(error):
#     return render_template('error.html'), 404

@app.route("/stations/<int:station_id>")
def get_station(station_id):
    try:
        station = db_utils.get_station(station_id)
        return station, 200
    except Exception as e:
        return f"failed to get station: {e}", 500

@app.route("/predicted-availabilities")
# @functools.lru_cache(maxsize=128)
def get_predicted_availabilities():
    """Gets predicted availabilities for all bikes on a given date
    
    Args:
    Query params:
        date_timestamp: timestamp to use for prediction in seconds
    Returns:
        500: if failed to query data or run prediction
        200: if prediction successful
    """
    try:
        prediction_date = request.args.get("date_timestamp", type=float)
    except Exception as e:
        return f"Invalid date: {e}", 400
    if prediction_date == None:
        return "Missing arg: date_timestamp", 400
    # Get the forecast for the date & time
    try:
        forecast = db_utils.get_weather_forecast(prediction_date)
        print("Retrieved weather forecast: ", forecast)
    except Exception as e:
        return f"Failed to get weather forecast: {e}", 500

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
    res = {"forecast": forecast, "stands": {}, "bikes": {}}
    try:
        stations = db_utils.get_stations()
    except Exception as e:
        return f"Failed to retrieve stations: ", e
    
    failed_predictions = []
    for station in stations:
        try:
            pkl_filename = f"model_{station['Id']}.pkl"
            with open(f"../models/stands-and-bikes/{pkl_filename}", "rb") as file:
                model = pickle.load(file)

            prediction = model.predict(x_values)
            res["stands"][station["Id"]] = str(round(prediction[0][0]))
            res["bikes"][station["Id"]] = str(round(prediction[0][1]))
        except Exception as e:
            failed_predictions.append({station['Id']: e})
    if len(failed_predictions) > 0:
        return f"Failed to run prediction for stations {failed_predictions}", 500
    
    return res, 200

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
    """Gets average number of stands and number of bikes available over the last 30 days
        for the given station.
    
    Returns:
        500: if failed to query data or run prediction
        200: if prediction successful
    """
    try:
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
    except Exception as e:
        return f"Failed to get historical availability: {e}", 500
    
    return {"bikes": bikes, "stands": stands}, 200


@app.route("/availability")
def get_availabilities():
    """Gets current availability data for all stations.

    Returns:
        list: List containing the availability record for each station
    """
    try:
        availabilities = db_utils.get_availabilities()
        return availabilities, 200
    except Exception as e:
        return f"Failed to get availability: {e}", 500


@app.route("/current-weather")
def get_current_weather():
    """Gets the current weather forecast

    Returns:
        list: Most recent current weather
    """
    try:
        current_weather = db_utils.get_current_weather()
        return current_weather, 200
    except Exception as e:
        return f"Failed to get current weather: {e}", 500


# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True, port=8000)