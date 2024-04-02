import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pickle


def load_data(availability_path, weather_path):
    availability = pd.read_csv(availability_path)
    weather = pd.read_csv(weather_path)

    # Ensure 'datetime' conversion and alignment
    availability['datetime'] = pd.to_datetime(availability['LastUpdated']).dt.tz_localize(None).dt.floor('H')
    weather['datetime'] = pd.to_datetime(weather['ForecastDate']).dt.tz_localize(None).dt.floor('H')

    # Diagnostics prints
    print("Availability Range:", availability['datetime'].min(), availability['datetime'].max())
    print("Weather Range:", weather['datetime'].min(), weather['datetime'].max())

    # Attempt merge
    merged_data = pd.merge(availability, weather, on='datetime', how='inner')

    # Check if merge was successful
    if merged_data.empty:
        raise ValueError("Merged dataset is empty. Check merge keys and data alignment.")
    else:
        print("Merge successful, total records:", len(merged_data))

    return merged_data


def train_models(merged_data):
    # Ensure the feature and target columns exist in merged_data
    feature_columns = ['Humidity', 'Pressure', 'Temperature', 'WeatherId', 'WindSpeed']
    if not all(column in merged_data for column in
               feature_columns + ['MechanicalBikesAvailable', 'ElectricBikesAvailable', 'StandsAvailable']):
        raise ValueError("One or more specified columns are missing from the merged dataset.")

    models = {}
    for target in ['MechanicalBikesAvailable', 'ElectricBikesAvailable', 'StandsAvailable']:
        X = merged_data[feature_columns]
        y = merged_data[target]

        # Proceed with splitting and training if there are enough samples
        if len(y) > 0:
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X_train, y_train)
            models[target] = model
        else:
            raise ValueError(f"No samples available for training the model for {target}.")

    return models


def save_models_to_pickle(models, filename):
    with open(filename, 'wb') as f:
        pickle.dump(models, f)

if __name__ == "__main__":
    availability_path = 'E:/software_engineer/mnt/data/Availability.csv'
    weather_path = 'E:/software_engineer/mnt/data/HourlyWeather.csv'

    try:
        merged_data = load_data(availability_path, weather_path)
        models = train_models(merged_data)
        save_models_to_pickle(models, 'bike_availability_models.pkl')
        print("Models trained and saved successfully.")
    except ValueError as e:
        print(e)