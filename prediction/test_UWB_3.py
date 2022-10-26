from datetime import datetime
import time
import robotHumanClass
import sys
from pathlib import Path
from threading import Thread
import multiprocessing as mp

import paho.mqtt.client as mqtt
import json
from simple_examples import uwb_example

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path


import robot.robot_api  # use API to get data from Robot
import tools.map




def on_message_tags(client, userdata, msg):  # defining the functions

    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    success_from_json = json_object_from_mqtt[0]["success"]
    tag_id_from_json = json_object_from_mqtt[0]["tagId"]
    if (success_from_json):
        coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]

       # print("[{}] Coordinates from UWB tag id:".format(time_log_str),
        #      tag_id_from_json, coordinates_from_json)
        # write data into influxdb
        # use unified coordinates to write influxdb
        influxdb_x, influxdb_y = tools.map.convert_uwb_position_for_unification(
            float(coordinates_from_json["x"]),
            float(coordinates_from_json["y"]))
        t = datetime.now()
        if (tag_id_from_json=="5329"):

            print(str(influxdb_x), str(influxdb_y),str(tag_id_from_json), t)

        #createList(data1.xPosition, data1.yPosition, influxdb_x, influxdb_y)
        #print(str(data1.xPosition))

tag_id= str(5328)
human1 = robotHumanClass.human(tag_id)
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server


client = mqtt.Client()
client.on_connect = uwb_example.on_connect  # set callbacks
client.on_message = on_message_tags
client.on_subscribe = uwb_example.on_subscribe
client.connect(host, port=port)
client.subscribe(topic)
try:  # Here we are making a loop to run above program forever untill there is a KBD intrrupt occurs
    client.loop_forever()
    

except KeyboardInterrupt:
    pass
client.disconnect()
client.loop_stop()
print("disconnected")

