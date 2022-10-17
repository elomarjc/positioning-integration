import paho.mqtt.client as mqtt
import ssl
import json
import csv
import sys
import datetime
import calendar
import time

host = "192.168.100.153"
port = 1883
topic = [("tags",0),("cv",0),("bandwidth",0)]


def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))



def on_message(client, userdata, msg):
    json_stream = msg.payload.decode()#[1:-1]
    # json_parsed = json.loads(json_stream) 

    print(json_stream)

def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic!")


client = mqtt.Client()

# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host, port=port)
client.subscribe(topic)

# works blocking, other, non-blocking, clients are available too.
# client.loop_forever()

try:
    client.loop_forever()
except KeyboardInterrupt:
    pass

client.disconnect()
client.loop_stop()
print("disconnected")