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


# @app.route("/tandsAvailable_avg_data/<int:StationId>")
# @functools.lru_cache(maxsize=128)
# def StandsAvailable_avg_data(StationId):
#     engine = ""

#     # Establish a connection to the database using the engine's connect method
#     with engine.connect() as connection:
#         # Execute an SQL query to fetch all columns from the Availability table for a specific StationId
#         # and load the result into a DataFrame
#         df = pd.read_sql_query(f"select * from Availability where StationId = {StationId} ;", connection)
#         # Explicitly close the database connection (though it's automatically managed by the with context)
#         connection.close()

#         # Remove duplicate rows based on all columns, keeping only the first occurrence
#         df = df.drop_duplicates(keep='first')
#         # Convert the 'LastUpdated' column to datetime format for easier manipulation
#         df['LastUpdated'] = pd.to_datetime(df['LastUpdated'])
#         # Set the 'LastUpdated' column as the index of the DataFrame for time series analysis
#         df = df.set_index('LastUpdated')
#         # Resample the time series data into 10-minute bins and calculate the mean for each bin
#         df = df.resample('10T').mean()
#         # Group the data by hour of the day and calculate the average values for each group
#         df = df.groupby(df.index.hour).mean()
#         # Convert the 'available_bikes' column of the DataFrame into a JSON string with "split" orientation
#         result = df['StandsAvailable'].to_json(orient="split")
#         # Parse the JSON string back into a Python dictionary
#         parsed = loads(result)
#         # Convert the dictionary into a pretty-printed JSON string and return it
#         return dumps(parsed, indent=4)


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
