# import required stuff - see below
#import dbinfo
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
    #print(response.json())  # Assuming the response is in JSON format
else:
    print("Failed to fetch data from the API. Status code:", response.status_code)

# This is me trying to read in the JSON file and make it into displayable objects

json_data = json.dumps(response.json())

#apply request to a variable
list_of_bike_stands =[item for item in json.loads(json_data)]

# There are 114 different bike stands
print(len(list_of_bike_stands))


# List for filtering properties
select_list = ['number', 'name', 'position', 'address', 'zip', 'contractName', 'banking', 'totalStands', 'status', 'mechanical_available', 'electric_available', 'stands_available', 'lastUpdate']
second_list = ['longitude', 'latitude', 'capacity', 'stands']

filtered_bike_stands = []

#Loop through each bike stand for filtering (bike_stand is a dictionary)
for bike_stand in list_of_bike_stands:
    #Delete 'mainStands' because its the same as 'totalStands' TBC
    del bike_stand['mainStands']

    # Create a temp dictionary called result which gets reset after each bikestand loop
    result = {}
    #Loops through each filtered property
    for key in select_list:
        # If the bike stand contains the key property i.e we are interested in this 
        if key in bike_stand:
            # Checks if the value of the matched key is a dictionary (this applies for position and totalStands)
            if isinstance(bike_stand[key], dict):
                innerDict = {}
                innerDict[key] = bike_stand[key]
                # Loops through the values of the matched dictionary
                for innerValue in innerDict.values():
                    for key in second_list:
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

for i in filtered_bike_stands:
    print(i)

# Notes
    # Cant see zip from the data
    # is accept_cards = banking? (I think so)
    # Unsure about mechanical/electrical_available too, is it electricalInternalBatteryBikes or just mechanical/electricalBikes? 
    # If you figure this out, add key (string) property name to the second_list
    # total stands = capacity btw