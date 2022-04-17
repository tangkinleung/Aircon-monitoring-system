"""
Subscriber (Rpi 2 - Kin Leung)
"""

from typing import NamedTuple
import os
from time import sleep
from datetime import datetime
import paho.mqtt.client as mqtt
import threading
from sense_hat import SenseHat
import GoogleSheets_rpi

""" 
Constants
"""
# setup broker and client connection
mqtt_broker = 'broker.emqx.io'
mqtt_client = mqtt.Client()
mqtt_topic = "2006_2_2_IoT_Aircon/2"
mqtt_port = 1883
sense = SenseHat()


""" 
Global Values
"""
device_name = "2"
aircon_temp = int()
sensor_data = ""
global_state = "0"
message = "RPI 2 Loop threads"

red = (255, 0, 0)
green = (0, 255, 0)


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    global aircon_temp
    message = msg.payload.decode('utf-8')
    parsed_string = message.split(",")

    aircon_num = parsed_string[0]
    aircon_temp = parsed_string[1]
    state = parsed_string[2]
    now = datetime.now()
    now = now.strftime("%Y/%m/%d %H:%M:%S")

    sensor_data = convert_list(str(now) + "," + message)
    turnOn_Off(state, aircon_temp)

    print(f'Message received: {message}')
    print(aircon_num)
    print(aircon_temp)
    print(state)
    dataList = [str(now), str(aircon_num), str(aircon_temp), str(state)]

    if sensor_data is not None:
        try:
            GoogleSheets_rpi.push(dataList)
        except:
            sleep(2)


# Get cpu temp
def get_cpu_temp():
    res = os.popen("vcgencmd measure_temp").readline()
    t = float(res.replace("temp=", "").replace("'C\n", ""))
    return t


def publishEveryHour():
    print("WAIT for max: ", 2)
    while True:
        sleep(6)
        publishSingularData()


def publishSingularData():
    global aircon_temp
    sense = SenseHat()
    sensor_id = device_name
    now = datetime.now()
    now = now.strftime("%Y/%m/%d %H:%M:%S")

    state = ""

    if sense.get_pixels() == [[0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0], [0, 252, 0],
                              [0, 252, 0]]:
        state = 1
    else:
        state = 0

    temp = aircon_temp
    # Append to Google sheets
    dataList = [str(now), str(sensor_id), str(temp), str(state)]
    try:
        GoogleSheets_rpi.push(dataList)
    except:
        sleep(2)

    # For testing only
    print("Date and Time: " + str(now))
    print("Sensor Id: " + str(sensor_id))
    print("Temperature: %.1f" % temp + " celsius")
    print("State: " + str(state))
    print("====================================\n")


class SensorData(NamedTuple):
    datetime: str
    aircon_id: str
    temperature: float
    state: str


def convert_list(msg):
    elements = msg.split(",")
    print(elements)
    return SensorData(elements[0], elements[1], elements[2], elements[3])


def turnOn_Off(state, temp):
    if "1" in state:
        sense.show_message(temp)
        sleep(0.5)
        sense.clear(green)
    else:
        sense.clear(red)


def main():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()


sub = threading.Thread(target=publishEveryHour)
pub = threading.Thread(target=main)

if __name__ == '__main__':
    print(message)
    sub.start()
    pub.start()
