from flask import Flask, render_template
from . import db_utils as db_utils
import os
import json

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

@app.route('/availability')
def get_availabilities():
    db_utils.get_availabilities()

@app.route('/availability/<int:station_id>/')
def get_availability(station_id): # TODO COM-46: needs to expect the following query params: stationId, startTime, endTime
    db_utils.get_availability(station_id, start_time, end_time)

@app.route('/current-weather')
def get_current_weather():
    #folder.get_currentweather


# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)