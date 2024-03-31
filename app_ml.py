from flask import Flask, request, jsonify
from load import predict_bike_availability

app = Flask(__name__)


@app.route('/predict/<int:station_id>/<predicted_time>', methods=['GET'])
def get_prediction(station_id, predicted_time):
    # Example weather features extracted from request arguments
    features = [
        request.args.get('humidity', type=float),
        request.args.get('pressure', type=float),
        request.args.get('temperature', type=float),
        request.args.get('weatherId', type=int),
        request.args.get('windSpeed', type=float)
    ]

    # Convert predicted_time to a format your model expects, if necessary
    # For example, if your model expects a specific time feature extraction

    prediction = predict_bike_availability(station_id, predicted_time, features)

    return jsonify({'predicted_mechanical_bikes_available': prediction})


if __name__ == '__main__':
    app.run(debug=True)
