from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
import paho.mqtt.client as mqtt
import warnings
import time
from threading import Thread
import sys
from pathlib import Path
import math
from sklearn.linear_model import LinearRegression



sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

from robot import robot_api
from tools import map


warnings.filterwarnings("error")

             # controller -> move method:
class robot: # finalXY -> self.move_x_entry.get()
             # robotID -> self.id_option_value.get()
             # robotIP -> self.robot_records[robot_record_key].ip
             # currentX -> coordinates_from_json["x"] & coordinates_from_json["y"]
    def __init__ (self, robotIP, absolutMaxSpeed, absolutMinSpeed, upperTimeThreshold, lowerTimeThreshold):
        self.robotIP = robotIP
        self.absolutMaxSpeed = absolutMaxSpeed # maximum speed that the robot can have
        self.absolutMinSpeed = absolutMinSpeed # minimum speed that the robot can have
        self.upperTimeThreshold = upperTimeThreshold
        self.lowerTimeThreshold = lowerTimeThreshold
        self.yPredictions = []
        self.xPredictions = []
        self.xPath = []
        self.yPath = []
        self.speedReference : float
        self.currentX : float
        self.currentY : float
        self.collisionTime: float

        self.SpeedSlope = (absolutMaxSpeed-absolutMinSpeed)/(upperTimeThreshold-lowerTimeThreshold)
        self.SpeedIntercept = absolutMinSpeed-self.SpeedSlope*lowerTimeThreshold




class human:
    def __init__ (self, tagID): # tagID -> tag_id_from_json
        self.tagID = tagID
        self.xPath = []
        self.yPath = []
        self.yPredictions = []
        self.xPredictions = []
        self.speed : float
        self.currentX : float
        self.currentY: float
        self.collisionTime: float

#code purely for running the test case

def neededSpeedReference (robot):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
    if (robot.collisionTime >= robot.upperTimeThreshold):
        return (robot.absolutMaxSpeed)#self.absolutMaxSpeed

    elif (robot.collisionTime < robot.lowerTimeThreshold):
        return 0

    else:
        return (robot.SpeedSlope*robot.collisionTime+robot.SpeedIntercept)

def fillAndUpdatePositionListRobot(positions_per_second, positions_saved, xList, yList, robot_ip):
    counter = 0
    while True:
        
        try:
            robot_status = robot_api.robot_status_direct(robot_ip)
            # Saves the newest position in a list. This list is limited to n elements
            xyValues = (map.convert_robot_position_for_unification(robot_status['position']['x'], robot_status['position']['y']))
            xList.append(xyValues[0]) # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION
            yList.append(xyValues[1]) # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION

            counter = counter+1

            if len(xList) != len(yList): # Handles the case where xPath and yPath have a different number of elements, though I don't see how that could happen
                print("ERROR in positional tracking. Resetting position list") # This message should maybe be sent somewhere other than the terminal, if it is needed at all
                xList.clear()
                yList.clear()
            elif len(xList) > positions_saved:
                del xList[0]
                del yList[0]
            if (counter%positions_per_second == 0 and counter != 0):
                print("Call the next function") # CALL FOR LINEAR REGRESSION

                counter = 0
            
            time.sleep(1/positions_per_second)
        except Exception as e:
        
            print(e)

def euclideanDistance (x1, y1, x2, y2):
    return math.sqrt((x1-x2)**2+(y1-y2)**2)

def timeToCollision (predictedX1, predictedY1, predictedX2, predictedY2, timeMargin, timeDelta, minimumEuclideanDistance): #timeMargin will define points with how many time diff are checked
    index = 0 #to iterate in the lists
    
    while index < len (predictedX1):
        
        maxAddition = int(timeMargin/timeDelta) # maxAddition will show the amount of indexes that need to be compared 
        addition = -maxAddition
        
        while addition <= maxAddition:
            if index + addition >= 0 and index + addition < len(predictedX1): # negative indexes do not exist and the length can't be exceded
                distanceAmongPoints = euclideanDistance(predictedX1[index], predictedY1[index], predictedX2[index+addition], predictedY2[index+addition])
            
                if distanceAmongPoints <= minimumEuclideanDistance:
                    if addition+index <= index: # we will always return the most critical time to collision
                        return (addition+index+1)*timeDelta #1 is added because collision in index = 0 means collision in t = timeDelta
                    else:
                        return (index+1)*timeDelta
                else:
                    pass #when the euclidean distance is greater than the defined minimum no actions needed
            else:
                pass #we will pass when the index is negative or the index is greater than the length of the list
            
            addition = addition+1
        index = index+1
    return -1 #-1 means no collision danger

def calculatePath (points, timeDelta):
    pointArray = np.array([])

    for point in points:
        pointArray = np.append(pointArray, point)
    
    timeArray = np.arange(0, timeDelta*len(points), timeDelta)
    timeArray = timeArray.reshape(-1, 1) #must be reshaped, otherwise the regression can't be done
    
    model = LinearRegression().fit(timeArray, pointArray)

    return model.coef_, model.intercept_

def predictNextPositions (points, coefficients, intercept, timeDelta, timeToPredict):
    predictedPoints = [] #Empty list where the future X or Y values will be stored
    timeValue = (len(points)-1)*timeDelta #Time value of the last known point assuming first element of the list points is in t=0
    finalTimeToPredict = timeValue+timeToPredict #Calculate the time value for the last point that is gonna be predicted
    
    while timeValue < finalTimeToPredict:
        timeValue = timeValue+timeDelta
        predictedPoints.append(timeValue*coefficients[0]+intercept)
    
    return predictedPoints




