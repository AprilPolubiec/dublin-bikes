import sqlalchemy as sqla
import json
import csv
import os
from utils import group_by

# Opening JSON file
f = open("secure/credentials.json")
data = json.load(f)

URI = "dublin-bikes-db.cl020iymavvj.us-east-1.rds.amazonaws.com"
PORT = 3306
DB = "dublin-bikes"
USER = "admin"

engine = sqla.create_engine(
    "mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB),
    echo=True,
)


class DBRow:
    columns = []
    def __init__(self, table: str, id=None):
        self.Id = id
        self.TableName = table

    def __eq__(self, other):
        self_vars = vars(self).items()
        other_vars = vars(other).items()
        if len(self_vars) != len(other_vars):
            return False
        for attribute in self_vars:
            if attribute[1] != getattr(other, attribute[0]):
                return False
        return True

    def values(self):
        obj = {}
        for val in self.columns:
            obj[val] = self.__getattribute__(val)
        return obj
    
    def to_csv_row(self):
        return [self.__getattribute__(column) for column in self.columns]
    
    def from_csv_row(self, csv_row: list):
        for val in csv_row:
            self.__setattr__(val, csv_row[val])


class StationRow(DBRow):
    columns = [
        "Id",
        "Name",
        "PositionLatitude",
        "PositionLongitude",
        "Address",
        "ZipCode",
        "City",
        "AcceptsCards",
        "TotalStands",
    ]

    def __init__(self):
        self.Id = 0
        self.Name = ""
        self.PositionLatitude = ""
        self.PositionLongitude = ""
        self.Address = ""
        self.ZipCode = ""
        self.City = ""
        self.AcceptsCards = False
        self.TotalStands = 0

    def __init__(
        self,
        number,
        name,
        latitude,
        longitude,
        address,
        zip,
        city,
        accepts_cards,
        total_stands,
    ):
        DBRow.__init__(self, "Station")
        self.Id = number
        self.Name = name
        self.PositionLatitude = latitude
        self.PositionLongitude = longitude
        self.Address = address
        self.ZipCode = zip
        self.City = city
        self.AcceptsCards = accepts_cards
        self.TotalStands = total_stands

    def __init__(self, obj, is_csv_row = False):
        if is_csv_row:
            self.from_csv_row(obj)
        else:
            self.Id = obj["number"]
            self.Name = obj["name"]
            self.PositionLatitude = obj["latitude"]
            self.PositionLongitude = obj["longitude"]
            self.Address = obj["address"]
            self.ZipCode = obj["zip"]
            self.City = obj["city"]
            self.AcceptsCards = obj["accepts_cards"]
            self.TotalStands = obj["total_stands"]

class AvailabilityRow(DBRow):
    columns = ["Station", "Status", "MechanicalBikesAvailable", "ElectricBikesAvailable", "StandsAvailable", "LastUpdated"]
    def __init__(self):
        self.Station = ""
        self.Status = ""
        self.MechanicalBikesAvailable = 0
        self.ElectricBikesAvailable = 0
        self.StandsAvailable = 0
        self.LastUpdated = 0

    def __init__(
        self,
        station,
        status,
        mechanical_available,
        electric_available,
        stands_available,
        last_updated,
    ):
        DBRow.__init__(self, "Availability")
        self.Station = station
        self.Status = status
        self.MechanicalBikesAvailable = mechanical_available
        self.ElectricBikesAvailable = electric_available
        self.StandsAvailable = stands_available
        self.LastUpdated = last_updated

    def __init__(self, obj, is_csv_row = False):
        if is_csv_row:
            self.from_csv_row(obj)
        else:
            DBRow.__init__(self, "Availability")
            self.Station = obj["number"]
            self.Status = obj["status"]
            self.MechanicalBikesAvailable = obj["mechanical_available"]
            self.ElectricBikesAvailable = obj["electric_available"]
            self.StandsAvailable = obj["stands_available"]
            self.LastUpdated = obj["last_updated"]

STATION_TABLE_NAME = "Station"
AVAILABILITY_TABLE_NAME = "Availability"


def insert_row(row: DBRow, table_name: str):
    with engine.connect() as conn:
        table = sqla.Table(table_name)
        conn.execute(sqla.insert(table), row.values())
        conn.commit()


def update_row(row: DBRow, table_name: str):
    with engine.connect() as conn:
        id = row.Id
        table = sqla.Table(table_name)
        conn.execute(sqla.update(table).where(table.Id == id).values(row.values()))
        conn.commit()


def delete_row(id: int, table_name: str):
    with engine.connect() as conn:
        table = sqla.Table(table_name)
        conn.execute(sqla.delete(table).where(table.Id == id))
        conn.commit()


def insert_station(row: StationRow):
    insert_row(row, STATION_TABLE_NAME)


def insert_stations(rows: list[StationRow]):
    for row in rows:
        insert_station(row)
    pass


def update_station(row: StationRow):
    update_row(row, STATION_TABLE_NAME)


def update_stations(rows: list[StationRow]):
    for row in rows:
        update_station(row)


def delete_station(id: int):
    delete_row(id, STATION_TABLE_NAME)


def delete_stations(ids: list[int]):
    for id in ids:
        delete_station(id)


def insert_availability(row: AvailabilityRow):
    insert_row(row, AVAILABILITY_TABLE_NAME)


def insert_availabilities(rows: list[AvailabilityRow]):
    for row in rows:
        insert_availability(row)
    pass


def update_availability(row: AvailabilityRow):
    update_row(row, AVAILABILITY_TABLE_NAME)


def update_availabilities(rows: list[AvailabilityRow]):
    for row in rows:
        update_availability(row)


def delete_availability(id: int):
    delete_row(id, AVAILABILITY_TABLE_NAME)


def delete_availabilities(ids: list[int]):
    for id in ids:
        delete_availability(id)


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


def get_cache_path(row_type):
    csv_path = "data/{}_cache.csv".format(row_type)
    return csv_path


def get_updated_rows(pending_rows: list[DBRow]):
    row_type = type(pending_rows[0])

    csv_path = get_cache_path(pending_rows[0].__class__.__name__)
    if not os.path.exists(csv_path):
        return pending_rows
    pending_rows = group_by(pending_rows, "Id")

    rows_to_update = []
    with open(csv_path, "r") as csv_file:
        reader = csv.DictReader(csv_file)
        existing_rows = []
        for csv_row in reader:
            db_row = row_type(csv_row, True) #TODO: this comes in already with the correct fields so need different constructor
            existing_rows.append(db_row)
        existing_rows_by_id = group_by(existing_rows, "Id")

    for pending_row_idx in pending_rows:
        existing = existing_rows_by_id[pending_row_idx]
        if existing is None:
            rows_to_update.append(pending_rows[pending_row_idx])
            continue
        if existing != pending_rows[pending_row_idx]:
            rows_to_update.append(pending_rows[pending_row_idx])
    return rows_to_update


def cache_data(rows: list[DBRow]):
    row_type = type(rows[0])
    csv_path = get_cache_path(rows[0].__class__.__name__)
    f = open(csv_path, "w")
    writer = csv.writer(f)

    writer.writerow(rows[0].columns)
    for row in rows:
        if type(row) != row_type:
            raise "All rows must be of the same type"
        writer.writerow(row.to_csv_row())

    f.close()
