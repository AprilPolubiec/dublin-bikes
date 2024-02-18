# import required stuff - see below
# #import dbinfo
# #import requests
# #import json

# import dbinfo
import requests
import json
# Specify the API endpoint URL
url = 'https://api.jcdecaux.com/vls/v3/stations?apiKey=frifk0jbxfefqqniqez09tw4jvk37wyf823b5j1i&contract=dublin'

url = 'https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}&contract={contract_name}'
# url = 'https://api.jcdecaux.com/vls/v1/stations?contract={Dublin} HTTP/1.1'
headers = {
    'Accept': 'application/json'
}

response = requests.get(url, headers=headers)


# response = requests.get(url)
# Check if the request was successful (status code 200)
# if response.status_code == 200:
#     # Print the response content
#     print("Response Body:")
#     print(response.json())  # Assuming the response is in JSON format
# else:
#     print("Failed to fetch data from the API. Status code:", response.status_code)
if response.status_code == 200:
    # Print the response content
    print("Response Body:")
    print(response.json())  # Assuming the response is in JSON format
else:
    print("Failed to fetch data from the API. Status code:", response.status_code)

#We need a key

#create get request

#apply request to a variable
#variable.text


#create function to have request running until project is done and not requesting 
