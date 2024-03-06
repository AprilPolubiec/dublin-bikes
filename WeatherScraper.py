import requests
import json
from datetime import datetime

import Config
import scraper


class Weather:
    def __init__(self, my_dict, i):
        self.dt = my_dict['hourly'][i]['dt']
        self.future_dt = my_dict['hourly'][i]['future_dt']
        self.feels_like = my_dict['hourly'][i]['feels_like']
        self.humidity = my_dict['hourly'][i]['humidity']
        self.pop = my_dict['hourly'][i]['pop']
        self.temp = my_dict['hourly'][i]['temp']
        self.uvi = my_dict['hourly'][i]['uvi']
        self.weather_id = my_dict['hourly'][i]['weather_id']

        self.wind_speed = my_dict['hourly'][i]['wind_speed']
        self.wind_gust = my_dict['hourly'][i]['wind_gust']
        self.rain_1h = my_dict['hourly'][i]['rain_1h']
        self.snow_1h = my_dict['hourly'][i]['snow_1h']


class WeatherScraper(scraper):
    def __init__(self, config):
        scraper.__init__(self, config)

    # override parent method: implement feature
    def _request_api(self):
        request = requests.get(
            self._config["APIWLink"] + self._config["APIWKEY"])
        response = request.text
        return response

    # override parent method: implement feature
    def _convert_to_obj(self, response):
        my_dict = json.loads(response)
        # turn it into Weather object
        weather_list = []
        for i in range(0, 24):
            weather_i = Weather(my_dict, i)
            weather_list.append(weather_i)
        return weather_list

    # override parent method: implement feature
    def _create_tables(self):
        # create database
        sql1 = """CREATE DATABASE IF NOT EXISTS dublinbikesdb"""
        self._engine.execute(sql1)

        # create the table for dynamic hourly weather
        sql2 = """CREATE TABLE hourly (
                            dt DATETIME NOT NULL,
                            future_dt DATETIME NOT NULL,
                            feels_like FLOAT,
                            humidity INTEGER,
                            pop FLOAT,
                            pressure INTEGER,
                            temp FLOAT,
                            uvi FLOAT,
                            weather_id INTEGER,
                            wind_speed FLOAT,
                            wind_gust FLOAT,
                            rain_1h FLOAT,
                            snow_1h FLOAT,
                            PRIMARY KEY (dt, future_dt)
                            )"""

        sql_forecast = """CREATE TABLE hourly (
                                    dt DATETIME NOT NULL,
                                    future_dt DATETIME NOT NULL,
                                    feels_like FLOAT,
                                    humidity INTEGER,
                                    pop FLOAT,
                                    pressure INTEGER,
                                    temp FLOAT,
                                    uvi FLOAT,
                                    weather_id INTEGER,
                                    wind_speed FLOAT,
                                    wind_gust FLOAT,
                                    rain_1h FLOAT,
                                    snow_1h FLOAT,
                                    PRIMARY KEY (dt, future_dt)
                                    )"""

        # create the table for historical hourly weather
        sql3 = """CREATE TABLE hourly (
                            dt DATETIME NOT NULL,
                            future_dt DATETIME NOT NULL,
                            feels_like FLOAT,
                            humidity INTEGER,
                            pop FLOAT,
                            pressure INTEGER,
                            temp FLOAT,
                            uvi FLOAT,
                            weather_id INTEGER,
                            wind_speed FLOAT,
                            wind_gust FLOAT,
                            rain_1h FLOAT,
                            snow_1h FLOAT,
                            PRIMARY KEY (dt, future_dt)
                            )"""
        try:
            self._engine.execute(sql2)
            self._engine.execute(sql3)
            self._engine.execute(sql_forecast)
        except Exception as e:
            print(e)

    # override parent method: implement feature
    def _save_to_db(self, weather_list):
        self._hourly_to_db(weather_list[:1])
        self._hourly_forecast_to_db(weather_list[1:])

    # Insert the data into the Database.
    def _hourly_to_db(self, item):
        dt_value = item[0].dt
        epoch_time = int(dt_value)
        time_date = datetime.fromtimestamp(epoch_time)
        datetime_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
        feels_like = item[0].feels_like
        humidity = item[0].humidity
        pop = item[0].pop
        pressure = item[0].pressure
        temp = item[0].temp
        uvi = item[0].uvi
        weather_id= item[0].weather_id
        wind_speed = item[0].wind_speed
        wind_gust = item[0].wind_gust
        rain_1h = item[0].rain_1h
        snow_1h = item[0].snow_1h
        print("Deleting")
        self._engine.execute("DELETE FROM hourlyWeather")
        print(datetime_str, feels_like, humidity , pop , pressure, temp,
              uvi, weather_id,wind_speed,wind_gust,rain_1h,snow_1h)
        vals = (datetime_str, feels_like, humidity , pop , pressure, temp,
              uvi, weather_id,wind_speed,wind_gust,rain_1h,snow_1h)
        self._engine.execute(
            "insert into hourlyWeather values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            vals)

        now = datetime.now()
        print("INFO: WeatherScraper._hourly_to_db: now is", now)
        minute = now.minute
        # if the minute is between 30 and 39, then insert history data
        if minute // 10 == 3:
            print("INFO: Start to historical weather data.")
            self._half_hour_to_history(vals)
        return

    # Insert the forecast data into the Database.
    def _hourly_forecast_to_db(self, items):
        print("Deleting hourlyWeatherForecast")
        self._engine.execute("DELETE FROM hourlyWeatherForecast")
        print("Inserting hourlyWeatherForecast")
        for item in items:
            dt_value = item.dt
            epoch_time = int(dt_value)
            time_date = datetime.fromtimestamp(epoch_time)
            datetime_str = time_date.strftime('%Y-%m-%d %H:%M:%S')
            feels_like = item.feels_like
            humidity = item.humidity
            pop = item.pop
            pressure = item.pressure
            temp = item.temp
            uvi = item.uvi
            weather_id = item.weather_id
            wind_speed = item.wind_speed
            wind_gust = item.wind_gust
            rain_1h = item.rain_1h
            snow_1h = item.snow_1h

            print(datetime_str, feels_like, humidity, pop, pressure, temp,
                  uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)
            vals = (datetime_str, feels_like, humidity, pop, pressure, temp,
                    uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)
            self._engine.execute(
                "insert into hourlyWeatherForecast values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                vals)

    def _half_hour_to_history(self, values):
        """Add every 6th row on the half hour to the historical table for
        weather. """
        self._engine.execute("insert into hourlyWeather_hist ("
                             "datetime_str, feels_like, humidity, pop, pressure, temp,"
                             "uvi, weather_id, wind_speed, wind_gust, rain_1h, snow_1h)"
                             " values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                             values)


if __name__ == "__main__":
    s = WeatherScraper(Config().load())
    s.scrape()
