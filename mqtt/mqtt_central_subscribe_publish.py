"""
Central Pi Subscriber/Publisher

This publisher is to accommodate the sending of data from user to aircon

"""
import paho.mqtt.client as mqtt

# Setup broker and client connection
mqtt_broker = 'broker.emqx.io'
mqtt_client = mqtt.Client()
mqtt_topic = "2006_2_2_IoT_Aircon"
mqtt_port = 1883

mqtt_client.connect(mqtt_broker, mqtt_port, 60)


def publishSingularData(aircon_num, temp, state):  # publish command
    if "1" in aircon_num:
        subtopic = "/1"
    elif "2" in aircon_num:
        subtopic = "/2"
    elif "3" in aircon_num:
        subtopic = "/3"
    else:
        subtopic = ""
    mqtt_client.publish(mqtt_topic+subtopic, f'{aircon_num},{temp},{state}')


def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(mqtt_topic)


def on_message(client, userdata, msg):
    message = msg.payload.decode('utf-8')
    parsed_string = message.split(",")
    aircon_num = parsed_string[0]
    temp = parsed_string[1]
    state = parsed_string[2]

    publishSingularData(aircon_num, temp, state)


def main():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(mqtt_broker, mqtt_port, 60)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('MQTT Central RPi')
    main()
