
import pandas as pd

import simplejson as json
import time
import datetime
import requests

import pickle
api = ""

def weather_forecast(days_from_today, hour):
    # Initialize the database engine connection string (this should be replaced with actual connection details)
    engine = ""

    # Establish a connection to the database
    with engine.connect() as connection:
        # Fetch weather forecast data from an external API
        forecast_info = requests.get(api)
        # Convert the JSON response into a Python dictionary
        forecast_info_json = json.loads(forecast_info.text)
        # Explicitly close the database connection (note: this is unnecessary in a 'with' context for database connections)
        connection.close()

    # Get today's date
    today = datetime.date.today()
    # Calculate the datetime object for the future date and hour of interest
    date_time = datetime.datetime(today.year, today.month, today.day + days_from_today, hour)
    # Convert the datetime object to a Unix timestamp (seconds since epoch)
    time_unix_timestamp = int(time.mktime(date_time.timetuple()))

    # Initialize variables to find the closest weather forecast entry to the desired time
    index = 0
    closest_date = abs(forecast_info_json[0].get('ForecastDate') - time_unix_timestamp)
    # Iterate through the first 40 forecast entries to find the closest one to the desired time
    for i in range(40):
        if abs(forecast_info_json[i].get('dt') - time_unix_timestamp) < closest_date:
            closest_date = abs(forecast_info_json[i].get('ForecastDate') - time_unix_timestamp)
            index = i

    # Extract the weather information from the closest forecast entry
    weather_info = forecast_info_json.get('list')[index]
    # Create a dictionary with the relevant weather data
    weather_data = {'Temperature': weather_info.get('Temperature', type=float),
                    'WindSpeed': weather_info.get('WindSpeed', type=float),
                    'Pressure': weather_info.get('Pressure', type=float),
                    'weatherId': weather_info.get('WeatherId', type=int),
                    'Humidity': weather_info.get('Humidity', type=float)}
    # Convert the weather data dictionary into a Pandas DataFrame
    future_weather_data = pd.DataFrame(weather_data, index=[0])

    # Return the DataFrame containing the weather data
    return future_weather_data


def predict_for_future_date(StationId, days_from_today, predicted_hour):
    # Load the predictive model from a file. The filename should include the StationId to identify the specific model for a station.
    with open("pkl".format(StationId), "rb") as handle:
        model = pickle.load(handle)

    # Call the weather_forecast function to get weather data for the specified days from today and at the predicted hour.
    future_weather_data = weather_forecast(days_from_today, predicted_hour)
    # Get today's date.
    today_date = datetime.date.today()

    # Preprocess the weather data to include additional time-related and weather-related features for the prediction.
    future_date = pd.to_datetime(today_date)
    day = future_date.day + days_from_today  # Calculate the future day.
    hour = predicted_hour  # The hour for prediction.
    year = future_date.year  # Extract the year.
    month = future_date.month  # Extract the month.
    # Determine if the future date is a weekday (Monday=0, Sunday=6).
    is_weekday = int((future_date.weekday() >= 0) & (future_date.weekday() <= 4))
    # Determine if the prediction is for busy hours in the morning (7-10) or evening (16-19).
    is_busy_hours = int(((hour >= 7) & (hour <= 10)) | ((hour >= 16) & (hour <= 19)))
    # Check if the temperature is below 5 degrees Celsius, indicating cold weather.
    cold_weather = (future_weather_data['Temperature'][0] < 5).astype(float)
    # Check if the wind speed is above 8 m/s, indicating windy weather.
    windy_weather = (future_weather_data['WindSpeed'][0] > 8).astype(float)

    # Copy the future weather data to a new DataFrame and add the derived features.
    input_df = future_weather_data.copy()
    input_df['year'] = year
    input_df['month'] = month
    input_df['day'] = day
    input_df['hour'] = hour
    input_df['StationId'] = StationId
    input_df['is_weekday'] = is_weekday
    input_df['is_busy_hours'] = is_busy_hours
    input_df['cold_weather'] = cold_weather
    input_df['windy_weather'] = windy_weather

    # Define a list of column names that are expected in the training data.
    A = [
        'StationId',
        'MechanicalBikesAvailable',
        'ElectricBikesAvailable',
        'StandsAvailable',
        'year',
        'month',
        'day',
        'hour',
        'minute_x',
        'Humidity',
        'Pressure',
        'Temperature',
        'WeatherId',
        'WindSpeed',
        'minute_y',
        'is_weekday',
        'is_busy_hours',
        'cold_weather',
        'windy_weather'
    ]

    # Initialize a DataFrame with columns specified in A. This is for ensuring compatibility with the model's input requirements.
    X = pd.DataFrame(columns=A)

    # Fill in missing columns in input_df with 0s to match the model's expected input structure.
    for col in X.columns:
        if col not in input_df.columns:
            input_df[col] = 0

    # Ensure the columns in input_df are in the same order as expected by the model.
    input_df = input_df[X.columns]

    # Use the loaded model to make a prediction based on the processed input data.
    prediction = model.predict(input_df)

    # Return the first element of the prediction, typically representing the predicted value.
    return prediction[0]
