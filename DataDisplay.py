import matplotlib.pyplot as mp
import pandas as pd
from pathlib import Path
import numpy as np
import datetime
from WeatherDashboard import getUnitList

USABLE_COLUMN_LIST = ['temp','high','low','windspeed','windgusts','degrees','sunrise','sunset']
UNIT_LABEL_INDEX = [1, 1, 1, 2, 2, 3, 0, 0]

def unitValidator(df) -> str:
    units = extractColumn(df, 'units').to_numpy()
    if(np.all(units == units[0])):
       return units[0]
    else:
        print("you have different units for different rows, data may be incorrect/malformed, and axis will deault to metric labels")
        return 'metric'
    

def getData():
    found = False
    while found == False:
        try:
            filename = str(input("What is the name of your file? (Be exact and include .csv, make sure your file is in this folder)\n"))
            directory = Path(__file__).parent
            path = directory / filename
            df = pd.read_csv(path)
            found = True
        except FileNotFoundError:
            print("Could not find file, please try again.")
        except PermissionError:
            print("Threw a permission error, please try again.")
        
    return df

def extractColumn(df, name):
    return df[name]

def getDaysMean(df: pd.DataFrame, timestamp_col: str = 'timestamp'):
    if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    
    df['date'] = df[timestamp_col].datetime.date
    grouped = df.groupby('date').mean(numeric_only=True)
    return grouped.to_dict(orient="Index")

def getMean(values: list) -> int:
    return sum(values)/len(values)

def graph(data: list, name: str, units: str):
    fig, ax = mp.subplots()
    unitList = getUnitList(units)
    ax.plot(range(len(data)), data, c='blue')
    ax.scatter(range(len(data)), data, c='blue')
    ax.set_ylabel(name + " (" + unitList[UNIT_LABEL_INDEX[USABLE_COLUMN_LIST.index(name)]] + ")")
    mp.show()


def main():
    name = ''
    df = getData()
    units = unitValidator(df)
    while name not in USABLE_COLUMN_LIST:
        name = input("What data do you want to track?\n")
        if name not in USABLE_COLUMN_LIST:
            print("Not viewable data or doesn't exist, try again. " + str(USABLE_COLUMN_LIST))
    data = extractColumn(df, name)
    avgdata = getDaysMean(df)
    graph(data, name, units)



main()