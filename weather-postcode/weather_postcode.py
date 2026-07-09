import sys
import requests
import json

# API endpoints
POSTCODE_ENDPOINT = "https://api.postcodes.io/postcodes/"
WEATHER_ENDPOINT = "https://api.openweathermap.org/data/2.5/weather"

# read api key from file
with open("weather_api_key") as file:
    API_KEY = file.readline().strip()


# this function takes a postcode and returns the lat and lon
def get_lat_lon(postcode):
    headers = {"Content-Type": "application/json"}
    body = {"postcodes": [postcode]}

    # post request to postcodes api
    response = requests.post(
        url=POSTCODE_ENDPOINT,
        headers=headers,
        json=body
    )

    # pull out lat and lon from the nested response
    result = response.json()["result"][0]["result"]
    lat = result["latitude"]
    lon = result["longitude"]

    return lat, lon


# this function takes lat and lon and returns weather data
def get_weather(lat, lon):
    # build the url with the coords and api key
    url = WEATHER_ENDPOINT + f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"

    response = requests.get(url)

    # return the response as a dict
    return response.json()


# grab postcode from command line argument
postcode = sys.argv[1]

# get the coordinates
lat, lon = get_lat_lon(postcode)

# get the weather using those coordinates
weather = get_weather(lat, lon)

# pull out the bits we want to display
description = weather["weather"][0]["description"]
temp = weather["main"]["temp"]
feels_like = weather["main"]["feels_like"]
humidity = weather["main"]["humidity"]

# pull out the bits we want to display
description = weather["weather"][0]["description"]
temp = weather["main"]["temp"]
feels_like = weather["main"]["feels_like"]
humidity = weather["main"]["humidity"]
wind = weather["wind"]["speed"]

# fun weather commentary based on temp
if temp >= 28:
    vibe = "AWOOP,JUMPSCARE!!! immediately back inside"
    advice = "do NOT go out without sunscreen babe, might just combust"
elif temp >= 20:
    vibe = "its giving summer sis ☀️"
    advice = "cute outfit weather, lets keep it light"
elif temp >= 14:
    vibe = "ermmm chefs kisss "
    advice = "grab a jacket just in case babes"
elif temp >= 8:
    vibe = "ITS A BIT CHIILY ISNT IT"
    advice = "Might wanna break out the furrrrr"
else:
    vibe = "HUNNI WHY IS IT THIS COLD "
    advice = "full winter mode. coat, scarf, the works. stay inside if u can"

# print it out
print(f"\n📍 {postcode.upper()} weather report bestie:\n")
print(f"  {vibe}")
print(f"  Condition : {description}")
print(f"  Temp      : {temp}C (feels like {feels_like}C)")
print(f"  Humidity  : {humidity}%")
print(f"  Wind      : {wind} m/s")
print(f"\n  verdict: {advice}\n")
