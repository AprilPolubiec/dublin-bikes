import sqlalchemy as sqla
import json
import os

DEV = os.environ["DBIKE_DEV"] == "True"

if not DEV:
    print("create_db can only be run locally. Exiting.")
    exit()

# Opening JSON file
file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "secure/credentials.json")
f = open(file_path)
data = json.load(f)

PORT = 3306
DB = "dublin-bikes"
URI = "127.0.0.1"
USER = "admin"

try:
    engine = sqla.create_engine(
        "mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB),
        echo=True,
    )
    conn = engine.connect()
except:
    raise "Failed to connect to db: mysql+mysqldb://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB)

confirm_create_station = ""

while confirm_create_station != data["DB_PASSWORD"]:
    confirm_create_station = input("You are about to create a new Station table which will delete existing Station table if it exists. If you are sure you want to do this, enter the DB password to proceed: ")

if confirm_create_station == "y":
    try:
        sql = """
            CREATE TABLE Station (
            Id INT NOT NULL,
            Name VARCHAR(45) NULL,
            PositionLatitude DECIMAL(6) NULL,
            PositionLongitude DECIMAL(6) NULL,
            Address VARCHAR(45) NULL,
            ZipCode VARCHAR(45) NULL,
            City VARCHAR(45) NULL,
            AcceptsCard INT NULL,
            TotalStands INT NULL,
            PRIMARY KEY (Id));
        """
        conn.execute(sqla.text("DROP TABLE IF EXISTS Station"))
        conn.execute(sqla.text(sql))
        conn.commit()
        print("Station table created successfully \u2764")
    except:
        raise "Failed to create Station table"

confirm_create_availability = ""

while confirm_create_availability != data["DB_PASSWORD"]:
    confirm_create_availability = input("You are about to create a new Availability table which will delete existing Availability table if it exists. If you are sure you want to do this, enter the DB password to proceed: ")

if confirm_create_availability == "y":
    try:
        sql = """
            CREATE TABLE Availability (
            StationId INT NOT NULL,
            Status VARCHAR(45) NULL,
            MechanicalBikesAvailable INT NULL,
            ElectricBikesAvailable INT NULL,
            StandsAvailable INT NULL,
            LastUpdated INT NOT NULL,
            PRIMARY KEY (StationId, LastUpdated));
        """
        conn.execute(sqla.text("DROP TABLE IF EXISTS Availability"))
        conn.execute(sqla.text(sql))
        conn.commit()
        print("Availability table created successfully \u2764")
    except:
        raise "Failed to create Availability table"

# confirm_create_current_weather = ""

# while confirm_create_current_weather != data["DB_PASSWORD"]:
#     confirm_create_current_weather = input("You are about to create a new Current Weather table which will delete existing Current Weather table if it exists. If you are sure you want to do this, enter the DB password to proceed: ")

# if confirm_create_current_weather == "y":
#     try:
#         sql = """
#             CREATE TABLE Availability (
#             StationId INT NOT NULL,
#             Status VARCHAR(45) NULL,
#             MechanicalBikesAvailable INT NULL,
#             ElectricBikesAvailable INT NULL,
#             StandsAvailable INT NULL,
#             LastUpdated INT NOT NULL,
#             PRIMARY KEY (StationId, LastUpdated));
#         """
#         conn.execute(sqla.text("DROP TABLE IF EXISTS Availability"))
#         conn.execute(sqla.text(sql))
#         conn.commit()
#         print("Availability table created successfully \u2764")
#     except:
#         raise "Failed to create Availability table"

conn.close()
