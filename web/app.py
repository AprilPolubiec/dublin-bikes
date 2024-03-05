from flask import Flask, render_template
import web.db_utils as db_utils

app = Flask(__name__)

@app.route('/')
def root():
    return render_template('index.html')

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

@app.route('/availability/<int:station_id>/)
def get_availability(station_id): # TODO COM-46: needs to expect the following query params: stationId, startTime, endTime
    db_utils.get_availability(station_id, start_time, end_time)

@app.teardown_appcontext
def close_connection(exception):
    db_utils.close()

if __name__ == "__main__":
    app.run(debug=True)