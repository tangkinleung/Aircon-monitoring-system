from datetime import datetime as dt
import datetime as datetime
import pandas as pd
import GoogleSheets

ELECTRICITY_RATE = 0.29 #cents
#Average "good" aircon wattage
AIRCON_KWH = 0.8#kWh

def getData():
    airconData = GoogleSheets.pull() #get data from whichever data source we are using
    airconData['datetime'] = pd.to_datetime(airconData['datetime'], errors='coerce')
    #Adding extra fields for easier time calculating and filtering dates
    airconData['state'] = airconData['state'].astype('int')
    airconData['temp'] = airconData['temp'].astype('int')
    airconData['date'] = airconData['datetime'].dt.date
    airconData['month'] = airconData['datetime'].dt.month
    airconData['year'] = airconData['datetime'].dt.year
    airconData=airconData.sort_values(by='datetime')
    return airconData

def splitPi(airconData):
    piData = [y for x, y in airconData.groupby('pi_ID', as_index=True)]  # split df according to pi_ID
    return piData

#Calculates current day data, will return a list containing an array of [[time used per pi], [price per pi]]
def calcToday():
    piData = splitPi(getData())
    time = []
    price=[]
    currentDay = dt.now().date()
    for pi in piData:
        matchedDay = pi[pi['date'] == currentDay]
        totalTime = calcTotalTime(matchedDay)
        time.append(totalTime)
        price.append(calcPrice(totalTime))
    return time, price

def calcCurrentWeek():
    piData = splitPi(getData())
    time = []
    price = []
    currentDay = dt.now().date()
    for pi in piData:
        per = pi.datetime.dt.to_period("W")
        weeks = [y for x, y in pi.groupby(per)]
        for week in weeks:
            if currentDay in week.date.values:
                totalTime = calcTotalTime(week)
                time.append(totalTime)
                price.append(calcPrice(totalTime))
    return time, price

#Calculates current day data, will return a list containing an array of [[time used per pi], [price per pi]]
def calcCurrentMonth():
    piData=splitPi(getData())
    time = []
    price = []
    currentMonth = dt.now().date().month
    currentYear = dt.now().date().year
    for pi in piData:
        matchedMonth = pi[(pi['year']==currentYear) & (pi['month']==currentMonth)]
        totalTime = calcTotalTime(matchedMonth)
        time.append(totalTime)
        price.append(calcPrice(totalTime))
    return time, price

def calcPrice(hours):
    return AIRCON_KWH*hours*ELECTRICITY_RATE

def calcTotalTime(df):
    totalTime=datetime.timedelta(hours=0) #in hours
    prev_row=None
    for index, row in df.iterrows():
        #On status to On status
        if row['state']==1 and prev_row is not None:
            if prev_row['state']==1:
                timeDiff=row['datetime']-prev_row['datetime']
                totalTime+=timeDiff
        #On status to Off status
        elif row['state']==0 and prev_row is not None:
            if prev_row['state']==1:
                timeDiff=row['datetime']-prev_row['datetime']
                totalTime+=timeDiff
        prev_row=row
    #print(str(totalTime.total_seconds()/3600)+"h")
    return totalTime.total_seconds()/3600


#Driver commands, can reference for example

#CURRENT DAY CALCULATION EXAMPLE
todayData=calcToday()
print("Daily data: ")
for i in range(len(todayData[0])):
    print("Pi "+str(i+1)+": "+str(round(todayData[0][i],1))+"h")
print("Total price (day): $" + str(round(sum(todayData[1]),2)))

# WEEK CALCULATION EXAMPLE
weekData=calcCurrentWeek()
print("\nWeek Data:")
for i in range(len(weekData[0])):
    print("Pi "+str(i+1)+": "+str(round(weekData[0][i],1))+"h"+" (Daily Avg: "+str(round(weekData[0][i]/7,2))+"h) ")
print("Total price (week): $" + str(round(sum(weekData[1]),2)))

# MONTH CALCULATION EXAMPLE
monthData=calcCurrentMonth()
print("\nMonth Data:")
for i in range(len(monthData[0])):
    print("Pi "+str(i+1)+": "+str(round(monthData[0][i],1))+"h"+" (Daily Avg: "+str(round(monthData[0][i]/30,2))+"h) ")
print("Total price (month): $" + str(round(sum(monthData[1]),2)))


