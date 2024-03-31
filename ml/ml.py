# db_utils1.py
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

def csv_path_for_table(table_name):
    return f"E:/software_engineer/mnt/data/{table_name}.csv"

class BikeAvailabilityModel:
    def __init__(self):
        self.model = self._train_model()

    def _load_and_prepare_data(self):
        # Load the datasets
        availability_path = csv_path_for_table('Availability')
        weather_path = csv_path_for_table('CurrentWeather')
        availability_data = pd.read_csv(availability_path)
        weather_data = pd.read_csv(weather_path)
        
        # Assuming both datasets have a 'datetime' and 'station_id' columns for merging
        # Convert datetime to a uniform format if necessary
        weather_data['datetime'] = pd.to_datetime(weather_data['datetime'])
        availability_data['datetime'] = pd.to_datetime(availability_data['datetime'])
        
        # Merge on datetime and station_id
        merged_data = pd.merge(availability_data, weather_data, on=['datetime', 'station_id'])

        return merged_data

    def _train_model(self):
        data = self._load_and_prepare_data()
        
        # Assuming 'available_bikes' is your target variable and is part of availability_data
        # Including weather and time features
        feature_columns = ['station_id', 'datetime', 'Humidity', 'Pressure', 'Temperature', 'WeatherId', 'WindSpeed']
        X = data[feature_columns]
        y = data['available_bikes']
        
        X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
        
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        return model

    def predict_availability(self, features):
        prediction = self.model.predict([features])
        return prediction[0]

# Initialize the model instance; it will start training upon initialization
bike_model = BikeAvailabilityModel()
