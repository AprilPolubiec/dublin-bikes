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

create_station = ""

while create_station != "y" and create_station != "n":
    create_station = input("Would you like to create a new Station table? If one already exists, it will be deleted and overwritten. y/n: ")

if create_station == "y":
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

create_availability = ""
while create_availability != "y" and create_availability != "n":
    create_availability = input("Would you like to create a new Availability table? If one already exists, it will be deleted and overwritten. y/n: ")

if create_availability == "y":
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

conn.close()
