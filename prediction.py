import pickle

# Function to load the model from a .pkl file
def load_model(pkl_filename):
    with open(pkl_filename, 'rb') as file:
        model = pickle.load(file)
    return model

# Updated function to include station_id and predicted_time
def predict_bike_availability(station_id, predicted_time, features):
    model = load_model('bike_availability_models.pkl')
    # Assuming you have a way to incorporate station_id and predicted_time into your features
    # This might involve adding these directly to your features list, transforming them, or using a model that
    # expects these values.
    full_features = [station_id] + features + [predicted_time]  # Example adjustment
    prediction = model['MechanicalBikesAvailable'].predict([full_features])[0]
    return prediction
