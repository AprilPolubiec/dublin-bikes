import requests
from web.db_utils import (
    availability_rows_from_list,
    station_rows_from_list,
    get_updated_rows,
    update_stations,
    insert_stations,
    cache_data,
    update_availabilities,
)
import json


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
        return response.json()
    else:
        print("Failed to fetch data from the API. Status code:", response.status_code)


# Query data from JCDecaux
realtime_data = get_realtime_data()
# print("Got realtime data: ", realtime_data)


realtime_data = [
    {
        "number": 1,
        "name": "Aprils Stand New Name",
        "latitude": 123,
        "longitude": 456,
        "address": "Main St",
        "zip": "D9ghwf",
        "city": "Dublin",
        "accepts_cards": True,
        "total_stands": 100,
        "status": "OPEN",
        "mechanical_available": 10,
        "electric_available": 5,
        "stands_available": 5,
        "last_updated": 9372934,
    }
]
# TODO: update get_realtime_data to return a list like the one above
availability_rows = availability_rows_from_list(realtime_data)
station_rows = station_rows_from_list(realtime_data)
(station_rows_to_update, station_rows_to_add) = get_updated_rows(station_rows)
print("New station data identified: ", station_rows_to_update)

# if len(station_rows_to_update) > 0:
#     update_stations(station_rows_to_update)
#     print("Updated stations")
# if len(station_rows_to_add) > 0:
#     insert_stations(station_rows_to_add)
#     print("Added stations")

# print("Updating availabilities: ", availability_rows)
# update_availabilities(availability_rows)
