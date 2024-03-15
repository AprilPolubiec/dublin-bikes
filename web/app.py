from flask import Flask, render_template, request

from . import db_utils1 as db_utils
import os
import json
from datetime import datetime






app = Flask(__name__)


@app.route('/')
def root():
    file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure/credentials.json")
    f = open(file_path)
    data = json.load(f)
    api_key = data["GOOGLE_MAPS_KEY"]
    return render_template('index.html', apiKey=api_key)



# startregion STATION QUERIES
@app.route('/stations')
def get_stations():
    stations = db_utils.get_stations()
    return stations


@app.route('/stations/<int:station_id>')
def get_station(station_id):
    station = db_utils.get_station(station_id)
    return station



#startregion AVAILABILITY QUERIES



@app.route('/availability/<int:station_id>')
def get_availability(
        station_id):  # TODO COM-46: needs to expect the following query params: stationId, startTime, endTime
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    availability = db_utils.get_availability(station_id, start_time, end_time)
    return availability

@app.route('/availability')
def get_availabilities():
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    availabilities = db_utils.get_availabilities(start_time,end_time)
    return availabilities
get_availabilities


@app.route('/weather/')
def get_current_weather():
    weather = db_utils.get_current_weather()
    return weather

@app.route('/weather/<string:date>/')
def get_forecast_weather(date):
    weather = db_utils.get_date_weather(date)
    return weather




# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)
