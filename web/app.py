from flask import Flask, render_template, request

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

#startregion DB FUNCTIONS
@app.route('/insert_row/<DBRow:row>')
def insert_row(row):
    table = request.args.get('table')
    row = db_utils.insert_row(row, table)
    return row


@app.route('/insert_row/<list[DBRow]:row>')
def insert_rows(row):
    table = request.args.get('table')
    rows = db_utils.insert_rows(row, table)
    return rows


@app.route('/update_row/<DBRow:row>')
def update_row(row):
    table = request.args.get('table')
    row = db_utils.update_row(row, table)
    return row

@app.route('/delete_row/<int:id>')
def delete_row(id):
    table = request.args.get('table')
    id = db_utils.delete_row(id, table)
    return id
#endregion

# startregion STATION QUERIES
@app.route('/stations')
def get_stations():
    stations = db_utils.get_stations()
    return stations


@app.route('/stations/<int:station_id>')
def get_station(station_id):
    station = db_utils.get_station(station_id)
    return station

@app.route('/insert_station/<StationRow:row>')
def insert_station(row):
    station = db_utils.insert_row(row)
    return station

@app.route('/insert_station/<list[StationRow]:rows>')
def insert_stations(rows):
    stations = db_utils.insert_stations(rows)
    return stations

@app.route('/update_station/<StationRow:row>')
def update_station(row):
    stations = db_utils.update_station(row)
    return stations

@app.route('/update_station/<list[StationRow]:rows>')
def update_stations(rows):
    stations = db_utils.update_stations(rows)
    return stations

@app.route('/delete_station/<int:id>')
def delete_station(id):
    id = db_utils.delete_stations(id)
    return id

@app.route('/delete_station/<list[int]:id>')
def delete_stations(id):
    result = db_utils.delete_stations(id)
    return result
#endregion

#startregion AVAILABILITY QUERIES
@app.route('/availability')
def get_availabilities():
    availabilities = db_utils.get_availabilities()
    return availabilities


@app.route('/availability/<int:station_id>/')
def get_availability(
        station_id):  # TODO COM-46: needs to expect the following query params: stationId, startTime, endTime
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    availability = db_utils.get_availability(station_id, start_time, end_time)
    return availability

@app.route('/insert_availability/<AvailabilityRow:row>/')
def insert_availability(row):
    availability = db_utils.insert_availability(row,table)
    return availability

@app.route('/insert_availability/<AvailabilityRow:row>/')
def insert_availabilities(rows):
    availabilities = db_utils.insert_availability(rows,table)
    return availabilities

@app.route('/availability/<int:station_id>/')
def delete_availabilities(station_id):
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    availabilities = db_utils.delete_availabilities(station_id, start_time, end_time)
    return availabilities
#endregion AVAILABILITY QUERIES

#startregion UTILITY FNS
@app.route('/availability_rows_from_list/<list:objs>/')
def availability_rows_from_list(objs):
    rows = db_utils.availability_rows_from_list(objs)
    return rows

@app.route('/hourly_weather_rows_from_list/<list:objs>/')
def hourly_weather_rows_from_list(objs):
    rows = db_utils.hourly_weather_rows_from_list(objs)
    return rows

@app.route('/get_cache_path/<table_name>/')
def get_cache_path(table_name):
    csv_path = db_utils.get_cache_path(table_name)
    return csv_path

@app.route('/get_updated_rows/<list[DBRow]:pending_rows>/')
def get_updated_rows(pending_rows):
    csv_path = db_utils.get_updated_rows(pending_rows)
    return csv_path

@app.route('/cache_datas/<StationRow:row_type>/')
def cache_data(row_type):
    csv_path = db_utils.cache_data(row_type)
    return csv_path

# @app.teardown_appcontext
# def close_connection(exception):
#     db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)
