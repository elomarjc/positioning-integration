import paho.mqtt.client as mqtt
import json

host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server


def on_connect(client, userdata, flags, rc):  # defining the functions
    print(mqtt.connack_string(rc))


def on_message(client, userdata, msg):  # defining the functions
    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    print(string_from_mqtt_stream)


def on_subscribe(client, userdata, mid, granted_qos):  # defining the functions
    print("Subscribed to topic")


client = mqtt.Client()
client.on_connect = on_connect  # set callbacks
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host, port=port)
client.subscribe(topic)
try:  # Here we are making a loop to run above program forever untill there is a KBD intrrupt occurs
    client.loop_forever()
except KeyboardInterrupt:
    pass
client.disconnect()
client.loop_stop()
print("disconnected")