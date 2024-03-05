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
from datetime import datetime


def get_realtime_data():
    f = open("secure/credentials.json")
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
                "latitude": d["position"]["latitude"],
                "longitude": d["position"]["longitude"],
                "address": d["address"],
                "zip": "000000", # TODO: remove
                "city": "Dublin",
                "accepts_cards": d["banking"],
                "total_stands": d["totalStands"]["capacity"],
                "status": d["status"],
                "mechanical_available": d["totalStands"]["availabilities"]["mechanicalBikes"],
                "electric_available": d["totalStands"]["availabilities"]["electricalBikes"],
                "stands_available": d["totalStands"]["availabilities"]["stands"],
                "last_updated": int(datetime.fromisoformat(d["lastUpdate"][:-1]).timestamp()),
            }
            stations.append(station_data)
        return stations
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)


# Query data from JCDecaux
realtime_data = get_realtime_data()

availability_rows = availability_rows_from_list(realtime_data)
station_rows = station_rows_from_list(realtime_data)
# (station_rows_to_update, station_rows_to_add) = get_updated_rows(station_rows)
# print("New station data identified: ", station_rows_to_update)

# if len(station_rows_to_update) > 0:
#     update_stations(station_rows_to_update)
#     print("Updated stations")
# if len(station_rows_to_add) > 0:
#     insert_stations(station_rows_to_add)
#     print("Added stations")

print("Inserting availabilities: ", availability_rows)
insert_availabilities(availability_rows)
