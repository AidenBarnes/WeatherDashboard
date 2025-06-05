
import os
import time
import requests
import pandas as pd
import schedule as sch
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

load_dotenv()  

api_key = os.getenv("API_KEY")


#Cosmetic functions/helpers
def unixToDatetime(unixTime):
    return datetime.fromtimestamp(unixTime, tz=timezone.utc)

def utcToLocal(utc, tzDelta):
    return unixToDatetime(utc) + timedelta(seconds=tzDelta)

def convertDegtoDirection(deg: int) -> str:
    #for once I'm missing switch TT
    #yes this function is used ONCE TT
    direction = ''
    #Quad I
    if deg == 0 or deg == 360:
        direction = 'E'
    elif deg in range(1, 31):
        direction = 'ENE'
    elif deg in range(31, 61):
        direction = 'NE'
    elif deg in range (61, 90):
        direction = 'NNE'
    #Quad II
    elif deg == 90:
        direction = 'N'
    elif deg in range(91, 121):
        direction = 'NNW'
    elif deg in range(121, 151):
        direction = 'NW'
    elif deg in range(151, 180):
        direction = 'WNW'
    #Quad III
    elif deg == 180:
        direction = 'W'
    elif deg in range(181, 211):
        direction = 'WSW'
    elif deg in range(211, 241):
        direction = 'SW'
    elif deg in range(241, 270):
        direction = 'SSW'
    #Quad IV
    elif deg == 270:
        direction = 'S'
    elif deg in range(271, 301):
        direction = 'SSE'
    elif deg in range(301, 331):
        direction = 'SE'
    elif deg in range(331, 360):
        direction = 'ESE'

    return direction

def getUnitList(units: str) -> list:
    if units == 'metric':
        return ['',  ' \u00b0C', ' meters/s', '\u00b0', ' Second difference from UTC']
    if units == 'imperial':
        return ['', ' \u00b0F', ' miles/h', '\u00b0', ' Second difference from UTC']

#Data manipulation
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
        "windgusts": rawdata["wind"].get("gust", "N/A"),
        "degrees": rawdata["wind"]["deg"],
        "sunrise": rawdata["sys"]["sunrise"],
        "sunset": rawdata["sys"]["sunset"],
        "condition": rawdata.get("weather", [{}])[0].get("description"),
        "tzdiff": rawdata["timezone"]
    }

#Handlers
def currentDisplayHelper(filtered_data: dict, Units: str):
    unitList = getUnitList(Units)

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
    print("Wind Direction: " + str(filtered_data["degrees"]) + unitList[3] + ' ' + convertDegtoDirection(filtered_data.get("degrees")))
    print("\n---Sun Info (Sunrise and Sunset are Local, then UTC)---")
    print("Timezone: " + str(filtered_data["tzdiff"]) + unitList[4])
    print("Sunrise: " + utcToLocal(filtered_data["sunrise"], filtered_data["tzdiff"]).strftime("%H:%M") + ", " + unixToDatetime(filtered_data["sunrise"]).strftime('%H:%M'))
    print("Sunset: " + utcToLocal(filtered_data["sunset"], filtered_data["tzdiff"]).strftime("%H:%M") + ", " + unixToDatetime(filtered_data["sunset"]).strftime('%H:%M'))
    print(45 * "-")

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
            
        except requests.exceptions.HTTPError:
            print("API says city is invalid.")
        except requests.exceptions.RequestException:
            print("Network error — check your internet or API settings.")
    
    return units, city

def csvWrite(data: dict, filename: str, units:str):
    data["units"] = units
    df = pd.DataFrame([data])
    base_dir = Path(__file__).parent
    filepath = base_dir / filename

    file_exists = filepath.exists()
    is_empty = not file_exists or filepath.stat().st_size == 0

    df.to_csv(filepath, mode='a', header=is_empty, index=False)

def scheduleWeatherCall(units, city, filename: str):
    raw_filtered = gatherData(fetchWeather(city, api_key, units))
    csvWrite(raw_filtered, filename, units)
    print("Data logged to " + filename + ", Timestamp: " + datetime.now().strftime("%H:%M"))


#callables
def scheduleWeatherCaller():
    print("\n" + (45 * "-") + "\n")
    print("NOTE/WARNING: This process is not threaded, since it doesn't have a good point to stop itself. " \
    "This means closing the window will STOP GATHERING DATA\nIf you would like more info on gathering data, " \
    "please consult the readme(TODO)")
    print("\n" + (45 * "-") + "\n")
    time.sleep(5)
    units, city = inputHelper()
    filename = str(input("Please type out the name of the file you want data to go to. Please be specific, and include the .csv (data file must be csv)\n"))
    scheduleWeatherCall(units, city, filename)
    sch.every(30).minutes.do(lambda: scheduleWeatherCall(units, city, filename))
    while True:
        sch.run_pending()
        time.sleep(1)

def currentWeather():
    units, city = inputHelper()
    raw_filtered = gatherData(fetchWeather(city, api_key, units))
    currentDisplayHelper(raw_filtered, units)

#main
def main():
    while True:
        while True:
            try:
                choice = int(input("What do you want to do?\n 1. Get weather at the moment\n 2. Start gathering data (will lock you out of getting current)\n 3. exit\n"))
                break
            except ValueError:
                print("Please enter an int.")
                time.sleep(1)
        if choice == 1:
            currentWeather()
            time.sleep(5)
        elif choice ==2:
            scheduleWeatherCaller()
        elif choice == 3:
            break
        else:
            print("out of range")
            time.sleep(1)


if __name__ == "__main__":     
    #main()
    scheduleWeatherCall('metric', 'Seattle', 'weather_report.csv')
