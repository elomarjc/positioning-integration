from concurrent.futures import thread
from typing import Counter
import robotHumanClass
import sys
from pathlib import Path
from threading import Thread
import multiprocessing as mp
import paho.mqtt.client as mqtt
import json
import time
from simple_examples import uwb_example
import tools.map
import matplotlib.pyplot as plt

human1=robotHumanClass.human("5329")
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server
def fillAndUpdatePositionListHuman(positions_per_second, positions_saved, xList, yList):
    while True:
        
        try:
            if len(xList) != len(yList): # Handles the case where xPath and yPath have a different number of elements, though I don't see how that could happen
                print("ERROR in positional tracking. Resetting position list") # This message should maybe be sent somewhere other than the terminal, if it is needed at all
                xList.clear()
                yList.clear()
            elif len(xList) > positions_saved:
                del xList[0]
                del yList[0]
            if (human1.readingCounter%positions_per_second == 0 and human1.readingCounter != 0):
                pass
            time.sleep(1/positions_per_second)
        except Exception as e:
        
            print(e)

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
       # print(str(influxdb_x), str(influxdb_y),str(tag_id_from_json))
    if (str(tag_id_from_json) == "5329"):
        human1.xPath.append(influxdb_x)
        human1.yPath.append(influxdb_y)

        if (human1.readingCounter == 4):
            human1.readingCounter = 0
            human1.readyforPrediction = True
        else:
            human1.readingCounter = human1.readingCounter+1
    #time.sleep(1/4)
def on_connect(client, userdata, flags, rc):  # defining the functions
    print(mqtt.connack_string(rc))
    pass
def on_subscribe(client, userdata, mid, granted_qos):  # defining the functions
    print("Subscribed to topic")

def run_tag():
    client = mqtt.Client()
    client.on_connect = on_connect  # set callbacks
    client.on_message = on_message_tags
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
def main_functions():
    counter = 0
    while True:
        if (human1.readyforPrediction):
            counter = counter+1
            human1.readyforPrediction = False
            human1.coefficients, human1.intercept = robotHumanClass.predictPaths(human1.xPath, human1.yPath)
            print("X path")
            print(human1.xPath)
            print("Y path")
            print(human1.yPath)
            print("Coefficients")
            print(human1.coefficients)
            print("Intercep")
            print(human1.intercept)


        
#main functions
human1.readyforPrediction = False
human1.readingCounter = 0
prediction = Thread(target=main_functions)
prediction.start()

#thread prediction
t_tag = Thread(target=run_tag)
t_tag.start()
#thread measurements
t_prediction = Thread(target=fillAndUpdatePositionListHuman, args=(4, 12, human1.xPath, human1.yPath))
t_prediction.start()




