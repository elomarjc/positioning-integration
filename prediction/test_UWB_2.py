from concurrent.futures import thread
from typing import Counter
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
import time

class UWB_data:
    def __init__ (self):
        self.xPosition = []
        self.yPosition = []
        self.valueCounter = 0

data1 = UWB_data()


def createList (xList, yList, xValue, yValue):
    xList.append(xValue)
    yList.append(yValue)

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
            if (data1.valueCounter%positions_per_second == 0 and data1.valueCounter != 0):
                print("--------------START")
                print(xList)
                print(yList)
                print("--------------END")
            
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
        data1.xPosition.append(influxdb_x)
        data1.yPosition.append(influxdb_y)
        if data1.valueCounter == 4:
            data1.valueCounter = 0
        else:
            data1.valueCounter = data1.valueCounter+1
        #createList(data1.xPosition, data1.yPosition, influxdb_x, influxdb_y)
        #print(str(data1.xPosition))

tag_id= str(5328)
human1 = robotHumanClass.human(tag_id)
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server

def run_tag():
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
if __name__ == '__main__':
    t_tag = mp.Process(target=run_tag)
    t_tag.start()
    t_tag.join()
    t_prediction = mp.Process(target=fillAndUpdatePositionListHuman, args=(4, 12, data1.xPosition, data1.yPosition))
    t_prediction.start()
    t_prediction.join()