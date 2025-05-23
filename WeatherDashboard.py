
import os
import requests
import pandas as pd
from datetime import datetime
from datetime import timezone
from dotenv import load_dotenv

load_dotenv()  

api_key = os.getenv("API_KEY")

CITY = "Seattle"
UNITS = "metric"
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
        "degrees": rawdata["wind"]["deg"],
        "gusts": rawdata["wind"]["gust"]
    }



#FUTURE: Try/Catch func for invalid city/ other inputs.

unitListMetric = ['', ' \u00b0C', ' \u00b0C', ' \u00b0C', ' m/s', '\u00b0', ' m/s']
def main():
    #FUTURE: Inputs
    raw_filtered = gatherData(fetchWeather(CITY, api_key, UNITS))
    print(40 * "-")
    print("\tWeather for: " +  str(raw_filtered["city"]).upper())
    print(40 * "-")
    i = 0
    for keys,values in raw_filtered.items():
        if keys != "city":
            print(str(keys) + ": " + str(values) + unitListMetric[int(i)])
            i += 1
        #FUTURE(easy): convert raw_filtered[degrees] to direction
main()    

