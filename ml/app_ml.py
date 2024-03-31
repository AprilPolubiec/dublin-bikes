# app.py
from flask import Flask, request, jsonify
from ml import bike_model
import pandas as pd

app = Flask(__name__)

@app.route('/predict/<int:station_id>/<predicted_time>', methods=['GET'])
def predict(station_id, predicted_time):
    # Parsing additional parameters for the prediction
    humidity = request.args.get('humidity', type=float)
    pressure = request.args.get('pressure', type=float)
    temperature = request.args.get('temperature', type=float)
    weather_id = request.args.get('weatherId', type=int)
    wind_speed = request.args.get('windSpeed', type=float)
    
    # Prepare the features as a list in the order expected by the model
    # Note: You might need to adjust datetime handling based on your model's training
    features = [station_id, predicted_time, humidity, pressure, temperature, weather_id, wind_speed]
    
    # Convert features to match the model's training format, e.g., datetime processing
    # This is an example and needs to be adjusted according to your specific model requirements
    
    predicted_availability = bike_model.predict_availability(features)
    
    return jsonify({
        'station_id': station_id,
        'predicted_time': predicted_time,
        'predicted_availability': predicted_availability
    })

if __name__ == '__main__':
    app.run(debug=True)
