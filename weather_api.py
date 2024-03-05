
import requests

def get_weather_data(latitude, longitude, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch data.")
        return None

latitude = 53.3498
longitude = 6.2603
api_key = "YOUR_API_KEY"  # Replace "YOUR_API_KEY" with your actual API key from OpenWeatherMap

# weather_data = get_weather_data(latitude, longitude, api_key)
# if weather_data:
#     print(weather_data)

codes = get_weather_data(53.3498, 6.2603, "730dd6087a1a7062c59f120c2ada380e9a7c32e4")
latitude = 53.3498
longitude = 6.2603

# 53.3498° N, 6.2603° W of dublin 