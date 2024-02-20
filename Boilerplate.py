# import required stuff - see below
# #import dbinfo
# #import requests
# #import json

# import dbinfo
import requests
import json
# Specify the API endpoint URL

url = 'https://api.jcdecaux.com/vls/v3/stations?apiKey={api_key}&contract={contract_name}'

headers = {
    'Accept': 'application/json'
}

response = requests.get(url, headers=headers)



if response.status_code == 200:
    # Print the response content
    print("Response Body:")
    print(response.json())  # Assuming the response is in JSON format
else:
    print("Failed to fetch data from the API. Status code:", response.status_code)



#apply request to a variable
#variable.text


#create function to have request running until project is done and not requesting 
