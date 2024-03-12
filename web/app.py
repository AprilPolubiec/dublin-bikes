from flask import Flask, render_template, request

from . import db_utils as db_utils
import os
import json
import requests
import datetime
from db_utils import CurrentWeatherRow, DailyWeatherRow, insert_rows, availability_rows_from_list, insert_row




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


#endregion

#startregion AVAILABILITY QUERIES
@app.route('/availability')
def get_availabilities():
    realtime_data = get_realtime_data()
    availability_rows = availability_rows_from_list(realtime_data)
    return availability_rows


@app.route('/availability/<int:station_id>/')
def get_availability(
        station_id):  # TODO COM-46: needs to expect the following query params: stationId, startTime, endTime
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    availability = db_utils.get_availability(station_id, start_time, end_time)
    return availability



@app.route('/weather/')
def get_current_weather():
    weather = db_utils.get_current_weather()
    return weather

@app.route('/weather/<datetime:date>/')
def get_forecast_weather(date):
    weather = db_utils.get_date_weather(date)

    return weather


def get_realtime_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    credentials_path = os.path.join(script_dir, 'secure', 'credentials.json')

    f = open(credentials_path)
    data = json.load(f)
    # real-time data url
    url = "https://api.jcdecaux.com/vls/v3/stations?apiKey={}&contract={}".format(
        data["API_KEY"], "dublin"
    )

    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print("Got data: ", response.json())
        stations = []
        for d in data:
            station_data = {
                "number": d["number"],
                "name": d["name"],
                "latitude": d["position"]["latitude"], # TODO: the DB is cutting off the decimal - fix
                "longitude": d["position"]["longitude"], # TODO: the DB is cutting off the decimal - fix
                "address": d["address"],
                "zip": "000000", # TODO: remove
                "city": "Dublin",
                "accepts_cards": d["banking"],
                "total_stands": d["totalStands"]["capacity"],
                "status": d["status"],
                "mechanical_available": d["totalStands"]["availabilities"]["mechanicalBikes"],
                "electric_available": d["totalStands"]["availabilities"]["electricalBikes"],
                "stands_available": d["totalStands"]["availabilities"]["stands"],
                "last_updated": d["lastUpdate"],
            }
            stations.append(station_data)
        return stations
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)
#endregion AVAILABILITY QUERIES



# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)
