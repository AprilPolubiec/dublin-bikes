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
        "mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB),
        echo=True,
    )
    conn = engine.connect()
except:
    raise Exception("mysql+mysqlconnector://{}:{}@{}:{}/{}".format(USER, data["DB_PASSWORD"], URI, PORT, DB))

confirm_create_station = ""

while confirm_create_station != data["DB_PASSWORD"] and confirm_create_station != 'pass':
    confirm_create_station = input("You are about to create a new Station table which will delete existing Station table if it exists. If you are sure you want to do this, enter the DB password to proceed. To skip table creation, type 'pass': ")

if confirm_create_station == data["DB_PASSWORD"]:
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

while confirm_create_availability != data["DB_PASSWORD"] and confirm_create_availability != "pass":
    confirm_create_availability = input("You are about to create a new Availability table which will delete existing Availability table if it exists. If you are sure you want to do this, enter the DB password to proceed. To skip table creation, type 'pass': ")

if confirm_create_availability == data["DB_PASSWORD"]:
    try:
        sql = """
            CREATE TABLE Availability (
            StationId INT NOT NULL,
            Status VARCHAR(45) NULL,
            MechanicalBikesAvailable INT NULL,
            ElectricBikesAvailable INT NULL,
            StandsAvailable INT NULL,
            LastUpdated VARCHAR(45) NOT NULL,
            PRIMARY KEY (StationId, LastUpdated));
        """
        conn.execute(sqla.text("DROP TABLE IF EXISTS Availability"))
        conn.execute(sqla.text(sql))
        conn.commit()
        print("Availability table created successfully \u2764")
    except:
        raise "Failed to create Availability table"


confirm_create_current_weather = ""

while confirm_create_current_weather != data["DB_PASSWORD"] and confirm_create_current_weather != "pass":
    confirm_create_current_weather = input("You are about to create a new CurrentWeather table which will delete existing CurrentWeather table if it exists. If you are sure you want to do this, enter the DB password to proceed. To skip table creation, type 'pass': ")

if confirm_create_current_weather == data["DB_PASSWORD"]:
    try:
        sql = """
            CREATE TABLE CurrentWeather (
                DateTime DATETIME NOT NULL,
                FeelsLike FLOAT,
                Humidity INTEGER,
                Pressure INTEGER,
                Sunrise DATETIME,
                Sunset DATETIME,
                Temperature FLOAT,
                UVI FLOAT,
                WeatherId INTEGER,
                WindGust FLOAT,
                WindSpeed FLOAT,
                Rain1h FLOAT,
                Snow1h FLOAT,
                PRIMARY KEY (DateTime)
                )
        """
        conn.execute(sqla.text("DROP TABLE IF EXISTS CurrentWeather"))
        conn.execute(sqla.text(sql))
        conn.commit()
        print("CurrentWeather table created successfully \u2764")
    except:
        raise "Failed to create current table"

while confirm_create_daily_weather != data["DB_PASSWORD"] and confirm_create_daily_weather != "pass":
    confirm_create_daily_weather = input("You are about to create a new DailyWeather table which will delete existing DailyWeather table if it exists. If you are sure you want to do this, enter the DB password to proceed. To skip table creation, type 'pass': ")

if confirm_create_daily_weather == data["DB_PASSWORD"]:
    try:
        sql = """
            CREATE TABLE DailyWeather (
                dt DATETIME NOT NULL,
                future_dt DATETIME NOT NULL,
                humidity INTEGER,
                pop FLOAT,
                pressure INTEGER,
                temp_max FLOAT,
                temp_min FLOAT,
                uvi FLOAT,
                weather_id INTEGER,
                wind_speed FLOAT,
                wind_gust FLOAT,
                rain FLOAT,
                snow FLOAT,
                PRIMARY KEY (dt, future_dt)
                )
        """
        conn.execute(sqla.text("DROP TABLE IF EXISTS DailyWeather"))
        conn.execute(sqla.text(sql))
        conn.commit()
        print("DailyWeather table created successfully \u2764")
    except:
        raise "Failed to create current table"

conn.close()
