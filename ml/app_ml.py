from flask import Flask, request, jsonify

import functools
import pandas as pd
from json import loads, dumps

import ml

app = Flask(__name__)

api = ""




@app.route('/predict/<int:StationId>/<int:days_from_today>/<int:predicted_hour>')
def predict_for_future_date(StationId, days_from_today, predicted_hour):

    MechanicalBikesAvailable, ElectricBikesAvailable, StandsAvailable=ml.predict_for_future_date(StationId,days_from_today,predicted_hour)
    return [int(MechanicalBikesAvailable), int(ElectricBikesAvailable), int(StandsAvailable)]


@app.route("/predicted_StandsAvailable/<int:StationId>/<int:days_from_today>")
@functools.lru_cache(maxsize=128)
def predicted_StandsAvailable(StationId, days_from_today):
    no_of_bikes = {}
    for i in range(24):
        mydata = predict_for_future_date(StationId, days_from_today, i)
        no_of_bikes[i] = mydata[0]
    return no_of_bikes


@app.route("/tandsAvailable_avg_data/<int:StationId>")
@functools.lru_cache(maxsize=128)
def StandsAvailable_avg_data(StationId):
    engine = ""

    # Establish a connection to the database using the engine's connect method
    with engine.connect() as connection:
        # Execute an SQL query to fetch all columns from the Availability table for a specific StationId
        # and load the result into a DataFrame
        df = pd.read_sql_query(f"select * from Availability where StationId = {StationId} ;", connection)
        # Explicitly close the database connection (though it's automatically managed by the with context)
        connection.close()

        # Remove duplicate rows based on all columns, keeping only the first occurrence
        df = df.drop_duplicates(keep='first')
        # Convert the 'LastUpdated' column to datetime format for easier manipulation
        df['LastUpdated'] = pd.to_datetime(df['LastUpdated'])
        # Set the 'LastUpdated' column as the index of the DataFrame for time series analysis
        df = df.set_index('LastUpdated')
        # Resample the time series data into 10-minute bins and calculate the mean for each bin
        df = df.resample('10T').mean()
        # Group the data by hour of the day and calculate the average values for each group
        df = df.groupby(df.index.hour).mean()
        # Convert the 'available_bikes' column of the DataFrame into a JSON string with "split" orientation
        result = df['StandsAvailable'].to_json(orient="split")
        # Parse the JSON string back into a Python dictionary
        parsed = loads(result)
        # Convert the dictionary into a pretty-printed JSON string and return it
        return dumps(parsed, indent=4)


if __name__ == '__main__':
    app.run(debug=True)
