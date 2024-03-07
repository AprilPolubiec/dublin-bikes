import requests
from web.db_utils import (
    availability_rows_from_list,
    station_rows_from_list,
    get_updated_rows,
    update_stations,
    insert_stations,
    insert_availabilities,
)
import json
import datetime
import os
import pytz

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
                "accepts_cards": int(d["banking"]),
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


now = datetime.datetime.now(tz=pytz.timezone('Europe/Dublin')).time()
if now >= datetime.time(5, 0) or now <= datetime.time(0, 30): # Don't scrape between 12:30 - 05:00
    # Query data from JCDecaux
    realtime_data = get_realtime_data()

availability_rows = availability_rows_from_list(realtime_data)
station_rows = station_rows_from_list(realtime_data)
(station_rows_to_update, station_rows_to_add) = get_updated_rows(station_rows)

# TODO: this is a bit finicky so lets make sure it doesnt break things
if len(station_rows_to_update) > 0:
    update_stations(station_rows_to_update)
    print("Updated stations")
if len(station_rows_to_add) > 0:
    insert_stations(station_rows_to_add)
    print("Added stations")

    insert_availabilities(availability_rows)
