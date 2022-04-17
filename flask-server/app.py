import io
import numpy as np
import csv
import errno
import random
import datetime as dt
from datetime import datetime
import pandas as pd
import os
from distutils.log import debug
from urllib import response
from flask import Flask, render_template, json, Response, redirect, request, jsonify
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import chart
import pandas as pd
import GoogleSheets
from datetime import datetime as dt
import datetime as datetime

# Setup broker and client connection
mqtt_broker = 'broker.emqx.io'
mqtt_client = mqtt.Client()
mqtt_topic = "2006_2_2_IoT_Aircon"
mqtt_port = 1883

ELECTRICITY_RATE = 0.29 #cents
#Average "good" aircon wattage
AIRCON_KWH = 0.8 #kWh


app = Flask(__name__)

# Returns homepage (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Returns graph page (graph.html) along with a dynamically generated graph
@app.route('/graph')
def graph():
    chart.todayChart()
    return render_template('graph.html',
                           name1 = 'Chart #1 (Today)',
                           url1 ='/static/images/today_chart-1.png',
                           name2 = 'Chart #2 (Today)',
                           url2 ='/static/images/today_chart-2.png',
                           name3 = 'Chart #3 (Today)',
                           url3 ='/static/images/today_chart-3.png',
                           day=calcToday(),
                           week=calcCurrentWeek(),
                           month=calcCurrentMonth())

# Function for managing aircon #1
@app.route('/aircon-one', methods=['POST'])
def aircon_one():
    request_data = request.get_json()
    print("JSON String", str(request_data))
    aircon = 1
    power_status = request_data['power_status']
    temp = request_data['temperature']

    print("Power Status: ", str(aircon))
    print("Temperature: ", str(temp))

    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.publish(mqtt_topic, f'{aircon},{temp},{power_status}')
    toReturn = {"msg": "Success!"}
    print(toReturn)
    return jsonify(toReturn)

# Function for managing aircon #2
@app.route('/aircon-two', methods=['POST'])
def aircon_two():
    request_data = request.get_json()
    print("JSON String", str(request_data))
    aircon = 2
    power_status = request_data['power_status']
    temp = request_data['temperature']

    print("Power Status: ", str(aircon))
    print("Temperature: ", str(temp))

    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.publish(mqtt_topic, f'{aircon},{temp},{power_status}')
    toReturn = {"msg": "Success!"}
    print(toReturn)
    return jsonify(toReturn)

# Function for managing aircon #3
@app.route('/aircon-three', methods=['POST'])
def aircon_three():
    request_data = request.get_json()
    print("JSON String", str(request_data))
    aircon = 3
    power_status = request_data['power_status']
    temp = request_data['temperature']

    print("Power Status: ", str(aircon))
    print("Temperature: ", str(temp))

    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.publish(mqtt_topic, f'{aircon},{temp},{power_status}')
    toReturn = {"msg": "Success!"}
    print(toReturn)

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

    return totalTime.total_seconds()/3600

#Calculates current day data, will return a list containing an array of [[time used per pi], [price per pi]]
@app.route('/calc-today', methods=['GET'])
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

    calculated_data = ""
    for i in range(len(piData)):
        calculated_data += ("Pi " + str(i + 1) + ": " + str(round(time[i], 1)) + "h\n")
    calculated_data += ("Total price (day): $" + str(round(sum(price), 2)))
    calculated_data = calculated_data.replace('\n', '<br/>')
    return calculated_data

@app.route('/calc-current-week', methods=['GET'])
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

    calculated_data = ""
    for i in range(len(piData)):
        calculated_data += ("Pi " + str(i + 1) + ": " + str(round(time[i], 1)) + "h" + " (Daily Avg: " + str(
            round(time[i] / 30, 2)) + "h)\n")
    calculated_data += ("Total price (week): $" + str(round(sum(price), 2)))
    calculated_data = calculated_data.replace('\n', '<br/>')
    return calculated_data

#Calculates current day data, will return a list containing an array of [[time used per pi], [price per pi]]
@app.route('/calc-current-month', methods=['GET'])
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

    calculated_data = ""
    for i in range(len(piData)):
        calculated_data += ("Pi " + str(i + 1) + ": " + str(round(time[i], 1)) + "h" + " (Daily Avg: " + str(
            round(time[i] / 30, 2)) + "h)\n")
    calculated_data += ("Total price (month): $" + str(round(sum(price), 2)))
    calculated_data = calculated_data.replace('\n', '<br/>')
    return calculated_data

if __name__ == '__main__':
    app.run(debug=True)