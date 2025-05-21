
import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()  

api_key = os.getenv("API_KEY")

print(api_key)

CITY = "Seattle"
UNITS = "metric"
DATAFILE = "weather_report.csv"

def fetchWeather(city: str, apikey: str, units: str) -> dict:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={apikey}&units={units}"
    response = requests.get(url)
    data = response.json()
    return data


def main():
    print("nothing yet!")
    