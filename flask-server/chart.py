import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import GoogleSheets
import energyCalc
from pathlib import Path

plt.style.use('seaborn-whitegrid')

def getData():
    # pull data from google sheets as dataframe
    airconData = GoogleSheets.pull()
    # convert datetime column in dateframe to datetime type for the below ops
    airconData['datetime'] = pd.to_datetime(airconData['datetime'])
    # getting date from datetime and create a new columnm in the dataframe from it
    airconData['date'] = airconData['datetime'].dt.date
    # get just the time portion from datetime and create a new column in the dataframe from it
    # casting the column as string for matplotlib
    airconData['time'] = airconData['datetime'].dt.time.astype('str')
    airconData['temp'] = airconData['temp'].astype('int')
    airconData['state'] = airconData['state'].astype('int')
    # sort values chronologically
    airconData = airconData.sort_values(by='datetime')
    return airconData

def todayChart():
    airconData = getData()
    Path("figures").mkdir(parents=True, exist_ok=True)
    #splitting pidata to each respective pi, taken from energyCalc.py
    piData = energyCalc.splitPi(airconData)
    #get current date
    currentDay = datetime.now().date()
    #for each pi we have,
    piNum=1
    for pi in piData:
        #filter data that matches with the current date (today)
        matchedDay = pi[pi['date'] == currentDay]
        #Change all temp when state is 0 to 0 degrees as well (because aircon is off)
        matchedDay.loc[matchedDay['state'] == 0, 'temp'] = 0
        #plot the chart with time as x axis, temp as y axis
        plt.figure()
        plt.title("Pi-%d" %piNum)
        plt.xlabel("Time")
        plt.xticks(rotation=45)
        plt.ylabel("Temperature")
        plt.plot(matchedDay['time'], matchedDay['temp'],'-o', color='gray',
         markersize=8, linewidth=2,
         markerfacecolor='white',
         markeredgecolor='gray',
         markeredgewidth=2)
        plt.subplots_adjust(bottom=0.30)
        piNum+=1
        v=1
    for i in plt.get_fignums():
        plt.figure(v)
        #plt.savefig('figures/todaypi-%d.png' % v)
        plt.savefig('static/images/today_chart-%d.png' % v)
        v+=1
        if v==4:
            v=1
