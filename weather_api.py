
import requests
import json

# Replace 'YOUR_API_KEY' with your actual API key
api_key = 'f9ac1e6b527fcf1a4b08d54ef9419527'
city = 'Dublin'
latitude = 53.3498
longitude = -6.2672
url = f'https://api.openweathermap.org/data/2.5/weather'

f = open("secure/credentials.json")
data = json.load(f)
W_API = data["W_API"]

# Make the API request
response = requests.get(url, params={"units":"metric", "lat": latitude, "lon":longitude, "appid":W_API})

# Check if request was successful
if response.status_code == 200:
    # Parse JSON response
    data = response.json()
    
    # Extract relevant weather information
    temperature = data['main']['temp']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    
    # Print weather information
    print(f'Weather in {city}:')
    print(f'Temperature: {temperature} K')
    print(f'Humidity: {humidity}%')
    print(f'Wind Speed: {wind_speed} m/s')
else:
    print('Failed to retrieve weather data')