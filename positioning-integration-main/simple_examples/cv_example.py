import paho.mqtt.client as mqtt
import json

host = "192.168.100.153"
port = 1883
topic = "cv"


def on_connect(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))


def on_message(client, userdata, msg):
    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    # success_from_json = json_object_from_mqtt[0]["success"]
    # if (success_from_json):
    #     coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]
    #     print("Coordinates from cv :", coordinates_from_json)
    print(string_from_mqtt_stream)


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to topic Computer Vision (cv)!")


client = mqtt.Client()
# set callbacks
client.on_connect = on_connect
client.on_message = on_message
client.on_subscribe = on_subscribe
client.connect(host, port=port)
client.subscribe(topic)
try:
    client.loop_forever()
except KeyboardInterrupt:
    pass
client.disconnect()
client.loop_stop()
print("disconnected")