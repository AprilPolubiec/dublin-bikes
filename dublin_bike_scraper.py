import requests
import json
from datetime import datetime

f = open("secure/credentials.json")
data = json.load(f)

# Specify the API endpoint URL
url = "https://api.jcdecaux.com/vls/v3/stations?apiKey={}&contract=Dublin".format(data["key_2"])

headers = {'Accept': 'application/json'}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    # Print the response content
    print("Response Body:")
    print(response.json())  # Assuming the response is in JSON format
else:
    print("Failed to fetch data from the API. Status code:", response.status_code)

# This is me trying to read in the JSON file and make it into displayable objects

json_data = json.dumps(response.json())

#apply request to a variable
list_of_bike_stands =[item for item in json.loads(json_data)]

# There are 114 different bike stands
print(len(list_of_bike_stands))

# List for filtering properties
dict_keys = ['number', 'name', 'position', 'address', 'zip', 'contractName', 'banking', 'totalStands', 'status', 'mechanical_available', 'electric_available', 'stands_available', 'lastUpdate']
innerDict_keys = ['longitude', 'latitude', 'capacity', 'stands', 'mechanicalBikes', 'electricalBikes']

filtered_bike_stands = []

#Loop through each bike stand for filtering (bike_stand is a dictionary)
for bike_stand in list_of_bike_stands:
    #Delete 'mainStands' because its the same as 'totalStands' TBD
    del bike_stand['mainStands']

    # Create a temp dictionary called result which gets reset after each bikestand loop
    result = {}
    #Loops through each filtered property
    for key in dict_keys:
        # If the bike stand contains the key property i.e we are interested in this 
        if key in bike_stand:
            # Checks if the value of the matched key is a dictionary (this applies for position and totalStands)
            if isinstance(bike_stand[key], dict):
                innerDict = {}
                innerDict[key] = bike_stand[key]
                # Loops through the values of the matched dictionary
                for innerValue in innerDict.values():
                    for key in innerDict_keys:
                        # For totalStands, its value is yet another dictionary called availabilities
                        if 'availabilities' in innerValue:
                            availabilities = innerValue.get('availabilities')
                            # Checks if desired property is contained in availabilities dictionary (stands)
                            if key in availabilities:
                                result[key] = availabilities[key]
                            # Else if checks if desired property is in totalStands, (capacity)
                            elif key in innerValue:
                                result[key] = innerValue[key]
                        # Otherwise the value is just a property (floats for longitude/latitude)
                        else:
                            if key in innerValue:
                                result[key] = innerValue[key]
            # If the value is not a dictionary and is a float/string/boolean, we add to the temporary result dictionary
            else:
                result[key] = bike_stand[key]
    
    # After each bike-stand loop, we add the filtered properties to the list of all bike stands
    filtered_bike_stands.append(result)

class BikeStand:
    def __init__(self, number, name, longitude, latitude, address, contractName, banking, capacity, stands, mechanicalBikes, electricalBikes, status, lastUpdate):
        self.number = number
        self.name = name
        self.longitude = longitude
        self.latitude = latitude
        self.address = address
        self.city = contractName
        self.accepts_cards = banking
        self.total_stands = capacity
        self.stands_available = stands
        self.mechanical_available = mechanicalBikes
        self.electric_available = electricalBikes
        self.status = status
        self.last_updated = datetime.timestamp(datetime.strptime(lastUpdate, "%Y-%m-%dT%H:%M:%SZ"))

formatted_bike_stands = []

for i in filtered_bike_stands:
    bike_stand = BikeStand(**i)
    formatted_bike_stands.append(bike_stand)

for bike_stand in formatted_bike_stands:
    print(bike_stand)