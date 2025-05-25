
import os
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

load_dotenv()  

api_key = os.getenv("API_KEY")

DATAFILE = "weather_report.csv"

def fetchWeather(city: str, apikey: str, units: str) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&units={units}"
    response = requests.get(url)
    data = response.json()
    return data

def gatherData(rawdata: dict) -> dict:
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "city": rawdata["name"],
        "temp": rawdata["main"]["temp"],
        "high": rawdata["main"]["temp_max"],
        "low": rawdata["main"]["temp_min"],
        "windspeed": rawdata["wind"]["speed"],
        "windgusts": rawdata["wind"]["gust"],
        "degrees": rawdata["wind"]["deg"],
        "sunrise": rawdata["sys"]["sunrise"],
        "sunset": rawdata["sys"]["sunset"],
        "condition": rawdata.get("weather", [{}])[0].get("description"),
        "tzdiff": rawdata["timezone"]
    }

def unixToDatetime(unixTime):
    return datetime.fromtimestamp(unixTime, tz=timezone.utc)

def utcToLocal(utc, tzDelta):
    return unixToDatetime(utc) + timedelta(seconds=tzDelta)

def convertDegtoDirection(deg):
    #for once I'm missing switch TT
    return 0

def displayHelper(filtered_data: dict, Units: str):
    unitListMetric = ['',  ' \u00b0C', ' meters/s', '\u00b0', ' Second difference from UTC']
    unitlistImperial = ['', ' \u00b0F', ' miles/h', '\u00b0', ' Second difference from UTC']
    unitList = []
    if Units == 'metric':
        unitList = unitListMetric
    elif Units == 'imperial':
        unitList = unitlistImperial
    
    #Header
    print(45 * "-")
    print("\tWeather for: " +  str(filtered_data["city"]).upper())
    print((45 * "-") + '\n')
    print("Record Timestamp: " + str(filtered_data["timestamp"]) + '\n')
    print(45 * "-")
    #dump
    print("\n---Temperature Info---")
    print("Current Temp: " + str(filtered_data["temp"]) + unitList[1])
    print("High: " + str(filtered_data["high"]) + unitList[1])
    print("Low: " + str(filtered_data["low"]) + unitList[1])
    print("\n---Condition Info---")
    print("Condition: " + filtered_data["condition"])
    print("Wind Speed: " + str(filtered_data["windspeed"]) + unitList[2])
    print("Wind Gust Speed: " + str(filtered_data["windgusts"]) + unitList[2])
    print("Wind Direction: " + str(filtered_data["degrees"]) + unitList[3])
    print("\n---Sun Info (Sunrise and Sunset are Local, then UTC)---")
    print("Timezone: " + str(filtered_data["tzdiff"]) + unitList[4])
    print("Sunrise: " + utcToLocal(filtered_data["sunrise"], filtered_data["tzdiff"]).strftime("%H:%M") + ", " + unixToDatetime(filtered_data["sunrise"]).strftime('%H:%M'))
    print("Sunset: " + utcToLocal(filtered_data["sunset"], filtered_data["tzdiff"]).strftime("%H:%M") + ", " + unixToDatetime(filtered_data["sunset"]).strftime('%H:%M'))
    print(45 * "-")
    #FUTURE(easy): convert raw_filtered[degrees] to direction and overall UI improvements

def inputHelper():
    units = None
    city = ''
    while units != "metric" and units != "imperial":
        units = (input("What units? (Metric/Imperial): \n")).lower()
    while True:
        try:
            city = input("What city? \n")

            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units={units}"
            response = requests.get(url)
            response.raise_for_status()
            break
            
        except requests.exceptions.HTTPError as e:
            print("API says city is invalid.")
        except requests.exceptions.RequestException:
            print("Network error — check your internet or API settings.")
    
    return units, city

def main():
    units, city = inputHelper()
    raw_filtered = gatherData(fetchWeather(city, api_key, units))
    displayHelper(raw_filtered, units)

        
main()    
