import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression, LogisticRegression
import pickle
from web.db_utils import get_historical_availabilities, get_historical_weather, get_stations
import datetime

def get_availability_on_the_hour(availabilities: list):
    current_hour = datetime.strptime(availabilities[0]["LastUpdated"], '%Y-%m-%dT%H:%M:%SZ').hour
    closest_time = datetime.strptime(availabilities[0]["LastUpdated"], '%Y-%m-%dT%H:%M:%SZ')
    availability_to_clean = availabilities[0]
    cleaned_availabilities = []

    for a in availabilities:
        t = datetime.strptime(a["LastUpdated"], '%Y-%m-%dT%H:%M:%SZ') # Get the last updated time
        if t.time().hour < current_hour: # Looking at a new hour
            availability_to_clean["LastUpdated"] = closest_time.replace(hour=current_hour, minute=0, second=0)
            cleaned_availabilities.append(availability_to_clean)
            current_hour = t.time().hour
            closest_time = t
        if t < closest_time:
            closest_time = t
            availability_to_clean = a
    return cleaned_availabilities

def load_data():
    stations = get_stations()
    station_ids = [s["Id"] for s in stations]

    weather = get_historical_weather(100)
    weather_df = pd.DataFrame(weather)
    weather_df['DateTime'] = weather_df['DateTime'].dt.hour

    feature_columns = [
            "FeelsLike",
            "Humidity",
            "Pressure",
            "Temperature",
        ]
    target_columns = ["StandsAvailable"]

    for id in station_ids:
        linear_model = LinearRegression()
        log_model = LogisticRegression()
        availability = get_historical_availabilities(id, 100) # TODO: grab more
        availability_on_the_hour = get_availability_on_the_hour(availability)
        # Filter out to the closest hour
        availability_df = pd.DataFrame(availability_on_the_hour)
        merged_data = pd.merge(availability_df, weather_df, left_on='LastUpdated', right_on="DateTime", how='inner')
        # print(merged_data.head)
        
        X_train, X_test, y_train, y_test = train_test_split(merged_data[feature_columns], merged_data[target_columns])
        linear_model.fit(X_train, y_train)
        log_model.fit(X_train, y_train)

        print("===== EVALUATION =======")
        print(X_test)
        print(y_test)
        ynew = linear_model.predict(X_test)
        print(ynew)

        print("===== EVALUATION =======")
        Xnew = weather_df[feature_columns] # query features
        # make a prediction
        ynew = log_model.predict(Xnew)
        print(f"X={Xnew.iloc[0]}, Predicted={ynew[0]}")

        with open('linear_model.pkl', 'wb') as handle:
            pickle.dump(linear_model, handle, pickle.HIGHEST_PROTOCOL)
        with open('log_model.pkl', 'wb') as handle:
            pickle.dump(log_model, handle, pickle.HIGHEST_PROTOCOL)
            