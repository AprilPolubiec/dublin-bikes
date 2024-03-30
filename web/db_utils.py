import sqlalchemy as sqla
from sqlalchemy import select
from sqlalchemy import desc
import json
import csv
import os
import sys
import datetime
from .utils import group_by, clean_type

# Opening JSON file
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure/credentials.json")
f = open(file_path)
data = json.load(f)

DEV = os.getenv("DBIKE_DEV", "False") == "True"
if DEV:
    URI = "127.0.0.1"
else:
    URI = "dublin-bikes-db.cnyo8auy4q4b.us-east-1.rds.amazonaws.com" # TODO: add dev env variables

PORT = 3307
DB = "dublin-bikes"
USER = "admin"

engine = sqla.create_engine(
    "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB),
    echo=True,
)
caching_enabled = True
print("Starting connection...")
conn = engine.connect()

class DBRow:
    columns = []
    table_name = ""
    def __init__(self, id=None):
        self.Id = id

    def __eq__(self, other):
        self_vars = vars(self).items()
        other_vars = vars(other).items()
        if len(self_vars) != len(other_vars):
            return False
        for attribute in self_vars:
            if str(attribute[1]) != str(getattr(other, attribute[0])):
                return False
        return True

    def __str__(self):
        return ', '.join([str(self.__getattribute__(column)) for column in self.columns])

    def __repr__(self):
        return ', '.join([str(self.__getattribute__(column)) for column in self.columns])

    def values(self):
        """Returns each attribute of the row class as a dictionary where the key is the attribute name.

        Returns:
            dictionary: each attribute and its value. Example: { "Id": 12, "Name": "Station A" } 
        """
        obj = {}
        for val in self.columns:
            obj[val] = self.__getattribute__(val)
        return obj
    
    def from_sql(self, row: list):
        """Given a list of values exported from a cache csv, sets the corresponding attributes
          on the class. This assumes that the row is in the same order as the columns or was generated by the `to_row` method.
        
          For example:
          A DBRow class with the following attributes:
            columns = ["Id", "Name", "City"]
          when passed [1, "Station ABC", "Dublin"] as row
          will set self.Id = 1, self.Name = "Station ABC" and self.City = "Dublin"
        Returns:
            row_values: list of values with columns in order of columns in db
        """
        for idx, val in enumerate(row):
            self.__setattr__(self.columns[idx], clean_type(val))

class StationRow(DBRow):
    table_name = "Station"
    table = sqla.Table(table_name, sqla.MetaData(), autoload_with=engine)
    columns = [
        "Id",
        "Name",
        "PositionLatitude",
        "PositionLongitude",
        "Address",
        "City",
        "AcceptsCard",
        "TotalStands",
    ]

    def __init__(self, obj, is_sql = False, is_csv = False):
        if is_sql:
            self.from_sql(obj)
        elif is_csv:
            self.Id = obj["Id"]
            self.Name = obj["Name"]
            self.PositionLatitude = obj["PositionLatitude"]
            self.PositionLongitude = obj["PositionLongitude"]
            self.Address = obj["Address"]
            self.City = obj["City"]
            self.AcceptsCard = obj["AcceptsCard"]
            self.TotalStands = obj["TotalStands"]
        else:
            try:
                self.Id = obj["number"]
                self.Name = obj["name"]
                self.PositionLatitude = obj["latitude"]
                self.PositionLongitude = obj["longitude"]
                self.Address = obj["address"]
                self.City = obj["city"]
                self.AcceptsCard = obj["accepts_cards"]
                self.TotalStands = obj["total_stands"]
            except TypeError:
                raise "Attempted to create row from object but a different type was received. If creating from a list, make sure to set is_sql = True"
        print("Created station row: {}".format(self))

class CurrentWeatherRow(DBRow):
    table_name = "CurrentWeather"
    table = sqla.Table(table_name, sqla.MetaData(), autoload_with=engine)
    columns = [
        "DateTime",
        "FeelsLike",
        "Humidity",
        "Pressure",
        "Sunrise",
        "Sunset",
        "Temperature",
        "UVI",
        "WeatherId",
        "WindGust",
        "WindSpeed",
        "Rain1h",
        "Snow1h",
    ]

    def __init__(self, obj, is_sql = False):
        if is_sql:
            self.from_sql(obj)
        else:
            try:
                self.DateTime = datetime.datetime.now()
                self.FeelsLike = obj["feels_like"]
                self.Humidity = obj["humidity"]
                self.Pressure = obj["pressure"]
                self.Sunrise = obj["sunrise"]
                self.Sunset = obj["sunset"]
                self.Temperature = obj["temperature"]
                self.UVI = None
                self.WeatherId = obj["weather_id"]
                self.WindSpeed = obj["wind_speed"]
                self.WindGust = None # where does this come from? daily?
                self.Rain1h = None # what is this
                self.Snow1h = None # what is this
                # self.Rain1h = obj["rain_1h"]
                # self.Snow1h = obj["snow_1h"]
            except TypeError:
                raise "Attempted to create row from object but a different type was received. If creating from a list, make sure to set is_sql = True"
        print("Created CurrentWeather row: {}".format(self))

class DailyWeatherRow(DBRow):
    table_name = "DailyWeather"
    table = sqla.Table(table_name, sqla.MetaData(), autoload_with=engine)
    columns = [
        "DateTime",
        "ForecastDate",
        "Humidity",
        "Pop",
        "Pressure",
        "TemperatureMax",
        "TemperatureMin",
        "UVI",
        "WeatherId",
        "WindSpeed",
        "WindGust",
        "Rain",
        "Snow",
    ]

    def __init__(self, obj, is_sql = False):
        if is_sql:
            self.from_sql(obj)
        else:
            try:
                self.DateTime = datetime.datetime.now()
                self.ForecastDate = obj["forecast_date"] # What is this?
                self.Humidity = obj["humidity"]
                self.Pop = obj["pop"]
                self.Pressure = obj["pressure"]
                self.TemperatureMax = obj["temperature_max"]
                self.TemperatureMin = obj["temperature_min"]
                self.UVI = None
                self.WeatherId = obj["weather_id"]
                self.WindGust = obj["wind_gust"]
                self.WindSpeed = obj["wind_speed"]
                self.Rain = None if "rain" not in obj.keys() else obj["rain"]
                self.Snow = None if "snow" not in obj.keys() else obj["snow"]
            except TypeError:
                raise "Attempted to create row from object but a different type was received. If creating from a list, make sure to set is_sql = True"
        print("Created DailyWeatherRow row: {}".format(self))
class HourlyWeatherRow(DBRow):
    table_name = "HourlyWeather"
    table = sqla.Table(table_name, sqla.MetaData(), autoload_with=engine)
    columns = [
        "DateTime",
        "ForecastDate",
        "FeelsLike",
        "Humidity",
        "Pop",
        "Pressure",
        "Temperature",
        "UVI",
        "WeatherId",
        "WindSpeed",
        "WindGust",
        "Rain1h",
        "Snow1h",
    ]

    def __init__(self, obj, is_sql = False):
        if is_sql:
            self.from_sql(obj)
        else:
            try:
                self.DateTime = datetime.datetime.now()
                self.ForecastDate = obj["forecast_date"] # What is this?
                self.FeelsLike = obj["feels_like"]
                self.Pop = obj["pop"]
                self.Humidity = obj["humidity"]
                self.Pressure = obj["pressure"]
                self.Temperature = obj["temperature"]
                self.UVI = None
                self.WeatherId = obj["weather_id"]
                self.WindSpeed = obj["wind_speed"]
                self.WindGust = obj["wind_gust"]
                self.Rain1h = None if "rain_1h" not in obj.keys() else obj["rain_1h"]
                self.Snow1h = None if "snow_1h" not in obj.keys() else obj["snow_1h"]
            except TypeError:
                raise "Attempted to create row from object but a different type was received. If creating from a list, make sure to set is_sql = True"
        print("Created HourlyWeatherRow row: {}".format(self))

class AvailabilityRow(DBRow):
    table_name = "Availability"
    table = sqla.Table(table_name, sqla.MetaData(), autoload_with=engine)
    columns = ["StationId", "Status", "MechanicalBikesAvailable", "ElectricBikesAvailable", "StandsAvailable", "LastUpdated"]

    def __init__(self, obj, is_csv = False, is_sql = False):
        if is_sql:
            self.from_sql(obj)
        elif is_csv:
            self.StationId = obj["StationId"]
            self.Status = obj["Status"]
            self.MechanicalBikesAvailable = obj["MechanicalBikesAvailable"]
            self.ElectricBikesAvailable = obj["ElectricBikesAvailable"]
            self.StandsAvailable = obj["StandsAvailable"]
            self.LastUpdated = obj["LastUpdated"]
        else:
            try:
                self.StationId = obj["number"]
                self.Status = obj["status"]
                self.MechanicalBikesAvailable = obj["mechanical_available"]
                self.ElectricBikesAvailable = obj["electric_available"]
                self.StandsAvailable = obj["stands_available"]
                self.LastUpdated = obj["last_updated"]
            except TypeError:
                raise "Attempted to create row from object but a different type was received. If creating from a list, make sure to set is_sql = True"
        print("Created availability row: {}".format(self.values()))

def close():
    print("Closing connection...")
    conn.close()

def disable_caching():
    global caching_enabled
    caching_enabled = False

def enable_caching():
    global caching_enabled
    caching_enabled = True

#startregion DB FUNCTIONS
def insert_row(row: DBRow, table: sqla.Table):
    conn.execute(sqla.insert(table), row.values())
    print("Inserting row: {}".format(row))
    conn.commit()
    return row

def insert_rows(rows: list[DBRow], table: sqla.Table):
    conn.execute(sqla.insert(table), [
            r.values() for r in rows
    ])
    print("Inserting rows: {}".format(rows))
    conn.commit()
    return rows

def update_row(row: DBRow, table: sqla.Table):
    id = row.Id
    conn.execute(sqla.update(table).where(table.c.Id == id).values(row.values()))
    print("Updating row: {}".format(row))
    conn.commit()
    return row

def delete_row(id: int, table: sqla.Table):
    conn.execute(sqla.delete(table).where(table.c.Id == id))
    print("Deleting row: {}".format(id))
    conn.commit()
    return id
#endregion

# startregion STATION QUERIES
def get_station(station_id: str):
    table = StationRow.table  
    rows = conn.execute(sqla.select(table).where(table.c.Id == station_id)).all()
    if len(rows) > 1:
        raise "Found more than one station with id {}".format(station_id)
    print("Found station: {}".format(rows[0]))
    return StationRow(rows[0], is_sql=True)

def get_stations():
    stations = []
    stmnt = sqla.select(StationRow.table)
    rows = conn.execute(stmnt)
    
    for row in rows:
        station = StationRow(list(row), is_sql=True).values() # Convert the list into a StationRow instance
        stations.append(station)
    print("Found stations: {}".format(stations))
    return stations

def insert_station(row: StationRow):
    return insert_row(row, StationRow.table)

def insert_stations(rows: list[StationRow]):
    try:
        res = insert_rows(rows, StationRow.table)
        cache_data(StationRow)
        return res
    except Exception as e:
        close()
        print("Failed to insert rows: {}".format(e.message))

def update_station(row: StationRow) -> StationRow:
    result = update_row(row, StationRow.table)
    cache_data(StationRow)
    return result

def update_stations(rows: list[StationRow]) -> list[StationRow]:
    results = []
    for row in rows:
        result = update_station(row)
        results.append(result)
    return results

def delete_station(id: int) -> int:
    return delete_row(id, StationRow.table)

def delete_stations(ids: list[int]) -> list[int]:
    results = []
    for id in ids:
        result = delete_station(id)
        results.append(result)
    return results

#endregion
    
#startregion AVAILABILITY QUERIES
def get_availability(station_id: str, start_timestamp: int, end_timestamp: int):
    start_timestamp = start_timestamp if start_timestamp is not None else 0
    end_timestamp = end_timestamp if end_timestamp is not None else sys.maxsize
    availabilities = []
    table = AvailabilityRow.table
    rows = conn.execute(sqla.select(table)
                        .where(table.c.StationId == station_id)
                        .where(table.c.LastUpdated >= start_timestamp)
                        .where(table.c.LastUpdated <= end_timestamp)
                    )
    for row in rows:
        availabilities.append(AvailabilityRow(row, is_sql=True))
    print("Found availabilities: {}".format(availabilities))
    return availabilities

def insert_availability(row: AvailabilityRow) -> AvailabilityRow:
    return insert_row(row, AvailabilityRow.table)

def insert_availabilities(rows: list[AvailabilityRow]) -> list[AvailabilityRow]:
    try:
        return insert_rows(rows, AvailabilityRow.table)
    except Exception as e:
        close()
        print("Failed to insert rows: {}".format(e))

def delete_availabilities(station_id: int, start_timestamp: int, end_timestamp: int):
    start_timestamp = start_timestamp if start_timestamp is not None else 0
    end_timestamp = end_timestamp if end_timestamp is not None else sys.maxsize
    table = AvailabilityRow.table
    result = conn.execute(sqla.delete(AvailabilityRow.table)
                          .where((table.c.StationId == station_id) & 
                                 (table.c.LastUpdated >= start_timestamp) & 
                                 (table.c.LastUpdated <= end_timestamp)))
    conn.commit()
    print("Deleted rows: {}".format(result.rowcount))
    return result.rowcount

#endregion AVAILABILITY QUERIES

#startregion UTILITY FNS
def availability_rows_from_list(objs: list):
    rows = []
    for o in objs:
        row = AvailabilityRow(o)
        rows.append(row)
    return rows

def station_rows_from_list(objs: list):
    rows = []
    for o in objs:
        row = StationRow(o)
        rows.append(row)
    return rows

def hourly_weather_rows_from_list(objs: list):
    rows = []
    for o in objs:
        row = HourlyWeatherRow(o)
        rows.append(row)
    return rows

def get_cache_path(table_name):
    """Given a type of row, returns where the cache file will be stored for that table.

    Args:
        table_name (string): the name of the row class eg: "StationRow"

    Returns:
        path (string): where the cache is
    """
    csv_path = "data/{}_cache.csv".format(table_name)
    return csv_path


def get_updated_rows(pending_rows: list[DBRow]):
    """Given a list of rows, finds the cached data and checks if anything has been updated, removed or added.
        Returns a tuple where the first element is the rows that need to be updated and the second
        element is the rows that need to be added

    Args:
        pending_rows (list[DBRow]): a list of rows that we want to check

    Returns:
        (rows_to_update, rows_to_add): a tuple containing all rows that need to be updated and all that need to be inserted
    """
    row_type = type(pending_rows[0])
    csv_path = get_cache_path(pending_rows[0].table_name)
    if not os.path.exists(csv_path):
        print("Cache does not exist. Building new from current data")
        cache_data(StationRow)

    pending_rows = group_by(pending_rows, "Id")

    rows_to_update = []
    rows_to_add = []

    # first, get all the rows that we currently have stored in our cache
    with open(csv_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        existing_rows = []
        for csv_row in reader:
            db_row = row_type(csv_row, is_csv=True)
            existing_rows.append(db_row)
        existing_rows_by_id = group_by(existing_rows, "Id")

    # Iterate over each of the rows we are checking
    for pending_row_idx in pending_rows:
        k = str(pending_row_idx)
        if k not in existing_rows_by_id.keys(): # This is a brand new row
            rows_to_add.append(pending_rows[k])
            continue
        if existing_rows_by_id[k] != pending_rows[k]: # If it does exist and the rows mismatch, we need to update
            rows_to_update.append(pending_rows[k])
    print("Found {} rows to update: {}".format(len(rows_to_update), rows_to_update))
    print("Found {} rows to add: {}".format(len(rows_to_add), rows_to_add))
    return (rows_to_update, rows_to_add)


def cache_data(row_type: StationRow):
    """Given a row type, queries the DB and stores the current contents in a local cache file.
        Should be called after every insert/update or periodically.

    Args:
        row_type (StationRow): the class of the row type
    """
    if (caching_enabled is False): 
        return
    if row_type is StationRow:
        data = get_stations()
    else:
        raise "Invalid row type: {}".format(row_type)

    csv_path = get_cache_path(row_type.table_name)
    f = open(csv_path, "w")
    writer = csv.writer(f)

    writer.writerow(row_type.columns)
    for row in data:
        writer.writerow(row.values())

    f.close()

def get_current_weather():
    # table = CurrentWeatherRow.table 
    current_weather = []
    stmnt = select(CurrentWeatherRow.table).order_by(desc(CurrentWeatherRow.table.c.DateTime)).limit(1)
    rows = conn.execute(stmnt)

    for row in rows:
        currentweather = CurrentWeatherRow(list(row), is_sql = True).values() # Convert the list into a CurrentWeatherRow instance
        current_weather.append(currentweather)
    print("Found weather: {}".format(current_weather))
    return current_weather


#select(user_table).order_by(user_table.c.name) but replace user_table
# print(stmnt)


#endregion
