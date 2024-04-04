from flask import Flask, render_template, request, jsonify
from . import db_utils as db_utils
import os
import json
# from prediction import predict_bike_availability

app = Flask(__name__)

@app.route('/')
def root():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure/credentials.json")
    f = open(file_path)
    data = json.load(f)
    api_key = data["GOOGLE_MAPS_KEY"]
    return render_template('index.html', apiKey=api_key)

@app.route('/stations')
def get_stations():
    stations = db_utils.get_stations()
    return stations

@app.route('/stations/<int:station_id>')
def get_station(station_id):
    db_utils.get_station(station_id)

# @app.route('/predict/<int:station_id>/<predicted_time>', methods=['GET'])
# def get_prediction(station_id, predicted_time):
#     # Example weather features extracted from request arguments
#     features = [
#         request.args.get('humidity', type=float),
#         request.args.get('pressure', type=float),
#         request.args.get('temperature', type=float),
#         request.args.get('weatherId', type=int),
#         request.args.get('windSpeed', type=float)
#     ]

#     # Convert predicted_time to a format your model expects, if necessary
#     # For example, if your model expects a specific time feature extraction

#     prediction = predict_bike_availability(station_id, predicted_time, features)

#     return jsonify({'predicted_mechanical_bikes_available': prediction})

# TODO: Test this - might not work
@app.route('/availability/<int:station_id>')
def get_availability(station_id):
    availability = db_utils.get_availability(station_id)
    return availability

@app.route('/availability')
def get_availabilities():
    availabilities = db_utils.get_availabilities()
    return availabilities

@app.route('/current-weather')
def get_current_weather():
    current_weather = db_utils.get_current_weather()
    return current_weather


# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)
