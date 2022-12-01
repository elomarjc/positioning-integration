import transformation
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
from datetime import datetime, timedelta
from all_class_instances import getAllInstances
import warnings
sys.path.append(str(Path(__file__).resolve().parents[1]))  # can import files based on the parents path
from robot import robot_api
import tools.map
import matplotlib.pyplot as plt
warnings.filterwarnings("error")


def on_message_tags(client, userdata, msg):  # defining the functions

    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    success_from_json = json_object_from_mqtt[0]["success"]
    tag_id_from_json = json_object_from_mqtt[0]["tagId"]
    if (success_from_json):
        coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]

        influxdb_x, influxdb_y = tools.map.convert_uwb_position_for_unification(
            float(coordinates_from_json["x"]),
            float(coordinates_from_json["y"]))
        for human in humans:
            if (str(tag_id_from_json) == human.tagID): 
                human.xPath.append(influxdb_x)
                human.yPath.append(influxdb_y)

                if (human.readingCounter == 3):
                    #human1.readingCounter = 0
                    human.readyforPrediction = True
                else:
                    human.readingCounter = human.readingCounter+1

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



'''def fillAndUpdatePositionListHuman(positions_per_second, positions_saved, xList, yList):
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
        
            print(e)'''

def main_functions():
    robot1.prevCollisionTime = 1000
    timeWhenSpeedWasDefined = 0
    deltaForMaxSpeed = 2
    limits = transformation.initializeLimits(width = 4, length = 4, robotbooty = 0.5)
    time.sleep(10)
    while True:  

        for human in humans:
            robotStatus = robot_api.robot_status_direct(robot1.robotIP)
            try:
                orientation = robotStatus["position"]["orientation"]-90
            except KeyError:
                pass
            humanInRobotFrame = transformation.homogeneousTransformation(orientation, [human.xPath[-1], human.yPath[-1]], [robot1.xPath[-1], robot1.yPath[-1]])
            inside=transformation.personInNoPredictArea(limits[0], limits[1], limits[2], limits[3], humanInRobotFrame)
            print("-----IS SOMEONE INSIDE NO PREDICT AREA????-----"+str(human.tagID))
            print(inside)
            if human.readyforPrediction and not inside:
                #print(time.time())
                human.readyforPrediction = False
                robotXCoef, robotXinter = robotHumanClass.calculatePath (robot1.xPath, timeBetweenSamples)
                robotYCoef, robotYinter = robotHumanClass.calculatePath (robot1.yPath, timeBetweenSamples)

                personXCoef, personXinter = robotHumanClass.calculatePath (human.xPath, timeBetweenSamples)
                personYCoef, personYinter = robotHumanClass.calculatePath (human.yPath, timeBetweenSamples)

                predictedRobotX = robotHumanClass.predictNextPositions (robot1.xPath, robotXCoef, robotXinter, timeBetweenSamples, timetopredict)
                predictedRobotY = robotHumanClass.predictNextPositions (robot1.yPath, robotYCoef, robotYinter, timeBetweenSamples, timetopredict)
                
                human.xPredictions = robotHumanClass.predictNextPositions (human.xPath, personXCoef, personXinter, timeBetweenSamples, timetopredict)
                human.YPredictions = robotHumanClass.predictNextPositions (human.yPath, personYCoef, personYinter, timeBetweenSamples, timetopredict)       
                robot1.collisionTime = robotHumanClass.timeToCollision(predictedRobotX, predictedRobotY, human.xPredictions, human.YPredictions, timeMargin, timeBetweenSamples, minimumEuclideanDistance)
                if (robot1.collisionTime != -1) and (robot1.collisionTime <=  robot1.prevCollisionTime): #add time condition to be able to increase the speed to a non maximum value
                    robot1.prevCollisionTime = robot1.collisionTime
                    robot1.speedReference = robotHumanClass.neededSpeedReference(robot1)

                    timeWhenSpeedWasDefined = time.time()
                    if robot1.speedReference == 0:
                        robot_api.pause(robot1.robotIP)
                        print("STOOOOOPPPPPPPPPPP")
                    else:
                        robot_api.un_pause(robot1.robotIP)
                        print(robot1.speedReference)
                        robot_api.set_max_speed(robot_ip, str(robot1.speedReference))
                elif ((time.time()>timeWhenSpeedWasDefined+deltaForMaxSpeed)): #on the elif statement we should make the robot go in maximum speed when the time since the robot's speed was set in a non maximum value is greater than the time of the collision that made the speed change

                    robot_api.un_pause(robot1.robotIP)  
                    robot_api.set_max_speed(robot_ip, str(robot1.absolutMaxSpeed))

                else:
                    robot1.prevCollisionTime = 10000
            else:
                pass


#parameters
timeBetweenSamples = 0.25
timetopredict = 6
lower_threshold=1.5
robot_max_speed=0.8
robot_min_speed=0.1
timeMargin = 0.5
minimumEuclideanDistance = 1.5
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server
positions_adquiered_per_second=4
positions_for_the_predictions=16
robot_ip="192.168.100.2"
#create objects
human1=robotHumanClass.human("5329")
human2=robotHumanClass.human("5328")
human3=robotHumanClass.human("5414")
humans = getAllInstances(robotHumanClass.human)
robot1=robotHumanClass.robot(robot_ip, robot_max_speed, robot_min_speed, timetopredict, lower_threshold)
#main functions
human1.readyforPrediction, human2.readyforPrediction, human3.readyforPrediction = False
human1.readingCounter, human2.readingCounter, human3.readingCounter = 0
prediction = Thread(target=main_functions)
prediction.start()
#thread prediction
t_tag = Thread(target=run_tag) 
t_tag.start()
#thread measurements
for human in humans:
    human1_list = Thread(target=robotHumanClass.fillAndUpdatePositionListHuman, args=(positions_adquiered_per_second, positions_for_the_predictions, human.xPath, human.yPath, human))
    human1_list.start()

t_prediction_robot = Thread(target=robotHumanClass.fillAndUpdatePositionListRobot, args=(positions_adquiered_per_second, positions_for_the_predictions, robot1.xPath, robot1.yPath, robot1))
t_prediction_robot.start()



