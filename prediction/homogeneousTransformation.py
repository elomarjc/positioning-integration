import numpy as np
import math
import time
import paho.mqtt.client as mqtt
import json
from threading import Thread

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

from robot import robot_api
import tools.map

host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server

tagPosi = []

def homogeneousTransformation (angle, pointToTransform, robotCoordenate): #pointToTransform and robotCoordenate are lists
    pointToTransformMatrix = np.array([])
    robotCoordenateMatrix = np.array([])
    
    for point in pointToTransform:
        pointToTransformMatrix = np.append(pointToTransformMatrix, point)
        
    pointToTransformMatrix = np.append(pointToTransformMatrix, 0) #Append 0 as z coordenate value
    pointToTransformMatrix = np.append(pointToTransformMatrix, 1) #Appended 1 to be able to multiply by de homogenous transform matrix
    pointToTransformMatrix = pointToTransformMatrix.transpose()
    
    for coordenate in robotCoordenate:
        robotCoordenateMatrix = np.append(robotCoordenateMatrix, coordenate)
    
    robotCoordenateMatrix = np.append(robotCoordenateMatrix, 0) #Append 0 as z coordenate value
    
    robotCoordenateMatrix = robotCoordenateMatrix*-1 #By definition of the transformation, to move from base frame to robot frame, we need to put robot frame "on top of" base frame
    
    angle = angle*math.pi/180 #Input angle is on deg, radians needed for the function
    
    rotationInZ = np.array([[math.cos(angle), -math.sin(angle), 0, 0], #Homogeneous transform only with rotation, positive rotation clockwise
                            [math.sin(angle), math.cos(angle), 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
    
    traslationXY = [[1, 0, 0, robotCoordenateMatrix[0]], #Homogenneous transform only with translation
                    [0, 1, 0, robotCoordenateMatrix[1]],
                    [0, 0, 1, robotCoordenateMatrix[2]],
                    [0, 0, 0, 1]]
    
    homogeneousTransformation = np.matmul(rotationInZ, traslationXY)
    
    transformationResult = np.matmul(homogeneousTransformation, pointToTransformMatrix)
    
    return [transformationResult[0], transformationResult[1]] #X and Y positions on robot frame

def personInNoPredictArea (topRightLimit, topLeftLimit, bottomRightLimit, bottomLeftLimit, personPosi): # since its a square, same X and Y will show twice    
    if (topRightLimit[0] > topLeftLimit[0]): #Check for x position
        if (personPosi[0] >= topLeftLimit[0] and personPosi[0] <= topRightLimit[0]):
            xIn = True
        else:
            xIn = False
    else:
        if (personPosi[0] <= topLeftLimit[0] and personPosi[0] >= topRightLimit[0]):
            xIn = True
        else:
            xIn = False
    
    if (topRightLimit[1] > bottomRightLimit[1]): #Check for Y position
        if (personPosi[1] <= topRightLimit[1] and personPosi[1] >= bottomRightLimit[1]):
            yIn = True
        else:
            yIn = False
    else:
        if (personPosi[1] >= topRightLimit[1] and personPosi[1] <= bottomRightLimit[1]):
            yIn = True
        else:
            yIn = False
    
    if (xIn and yIn):
        return True
    else:
        return False

def initializeLimits (width, length, robotbooty): #The limits of the area are defined on the robot frame
    topRightLimit = [width/2, 0-robotbooty]

    topLeftLimit = [-width/2, 0-robotbooty]

    bottomRightLimit = [width/2, -length-robotbooty]

    bottomLeftLimit = [-width/2, -length-robotbooty]

    return topRightLimit, topLeftLimit, bottomRightLimit, bottomLeftLimit

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

        if (str(tag_id_from_json) == "5328"): 
            tagPosi[0] = (influxdb_x)
            tagPosi[1] =(influxdb_y)

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

def mainFunc():
    while True:
        initialized_points = initializeLimits(4, 4, 0.5)
        A = initialized_points[0]
        B = initialized_points[1]
        C = initialized_points[2]
        D = initialized_points[3]

        robotStatus = robot_api.robot_status_direct("192.168.100.2")
        orientation = robotStatus["position"]["orientation"]-90
        robotPosi = (map.convert_robot_position_for_unification(robotStatus['position']['x'], robotStatus['position']['y']))

        personInRobotFrame = homogeneousTransformation(orientation, tagPosi, robotPosi)

        if(personInNoPredictArea(A, B, C, D, personInRobotFrame)):
            print("The person is inside the No Predict Area")
        else:
            print("The person is outside the No Predict Area")

        time.sleep(5)

threadMain = Thread(target=mainFunc)
threadMain.start()

threadTag = Thread(target=run_tag)
threadTag.start()