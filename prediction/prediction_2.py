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
from datetime import datetime
import warnings
sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

from robot import robot_api
from simple_examples import uwb_example
import tools.map
import matplotlib.pyplot as plt
warnings.filterwarnings("error")

robot_ip="192.168.100.2"
human1=robotHumanClass.human("5329")
robot1=robotHumanClass.robot(robot_ip, 0.8, 0.1, 7, 2)
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server
lower_range=0
upper_range=10
delta=7
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

            if (human1.readingCounter == 3):
                #human1.readingCounter = 0
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
    setSpeedTime=datetime.now()-datetime.now()
    robot1.prevCollisionTime=1000
    while True:
        if (human1.readyforPrediction):# or robot1.readyforPrediction):
            human1.readyforPrediction = False
            robot1.readyforPrediction = False
            human1.readingCounter = 0


            human1.coefficients, human1.intercept = robotHumanClass.predictPaths(human1.xPath, human1.yPath)
            robot1.coefficients, robot1.intercept = robotHumanClass.predictPaths(robot1.xPath, robot1.yPath)
            #print("human----------")
            #print(human1.coefficients)
            #print(human1.intercept)
            #print("robot----------")
            #print(robot1.coefficients)
            #print(robot1.intercept)
            
            #t = datetime.now()
            #print(t)
            
            try:
                intercept = robotHumanClass.findIntercept(lower_range, upper_range, robot1.coefficients, robot1.intercept, human1.coefficients, human1.intercept)
            except RuntimeWarning:
                intercept = -1


            if (type(intercept)== int):
                print("No collision danger, there is no intercept")

            else:
                if(not robotHumanClass.takeCrossingIntoAccount(intercept, robot1.xPath, robot1.yPath, human1.xPath, human1.yPath)):
                    print("No collision danger, the moving objects are moving away from intercept")
                else:
                    print("COLLISION DANGER")
                    #xapth[-1] denbora guztian aktualizatzen doia
                    robot1.collisionDistance = robotHumanClass.calculateDistanceToCollision(robot1.coefficients, robot1.intercept, robot1.xPath[-1],robot1.yPath[-1],intercept[0],intercept[1])
                    human1.collisionDistance = robotHumanClass.calculateDistanceToCollision(human1.coefficients, human1.intercept, human1.xPath[-1],human1.yPath[-1],intercept[0],intercept[1])
                    robot_status = robot_api.robot_status_direct(robot1.robotIP)
                    try:
                        robot1.actualSpeed = robot_status['velocity']['linear']
                    except KeyError:
                        robot1.actualSpeed=0
                    #robot1.actualSpeed = robotHumanClass.calculateCurrentSpeed(robot1.xPath,robot1.yPath)#read from API
                    human1.actualSpeed = robotHumanClass.calculateCurrentSpeed(human1.xPath,human1.yPath)
                    
                    robot1.collisionTime = robotHumanClass.calculateTimeToCollision(robot1.collisionDistance, robot1.actualSpeed)
                    human1.collisionTime = robotHumanClass.calculateTimeToCollision(human1.collisionDistance, human1.actualSpeed)
                    print(robot1.collisionTime)
                    print(human1.collisionTime)

                    if((robotHumanClass.areCollisionTimesClose(robot1.collisionTime, human1.collisionTime, delta)) and (robot1.collisionTime < robot1.prevCollisionTime)):#((((datetime.now()-setSpeedTime).second) > robot1.prevCollisionTime) or (robot1.collisionTime < robot1.prevCollisionTime))) :
                        print("aaaaaa")
                        robot1.speedReference = robotHumanClass.neededSpeedReference(robot1)
                        print(robot1.speedReference)
                        robot1.prevCollisionTime = robot1.collisionTime
                        setSpeedTime= datetime.now()
                        if (robot1.speedReference == 0):
                            robot_api.pause(robot1.robotIP)
                        else:
                            robot_api.un_pause(robot1.robotIP)
                            robot_api.set_desired_speed(robot_ip, str(robot1.speedReference) )

                        
                    elif ((datetime.now()-setSpeedTime).second):#.second(S) ) > robot1.prevCollisionTime):
                        robot_api.set_max_speed(robot_ip, "1.1")
                        print("max_speed")
                    else:
                        pass
                            
        else:
            pass
            





        
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
t_prediction_robot = Thread(target=robotHumanClass.fillAndUpdatePositionListRobot, args=(4, 12, robot1.xPath, robot1.yPath, robot1))
t_prediction_robot.start()



