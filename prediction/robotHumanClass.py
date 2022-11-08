from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt
import warnings
import time
from threading import Thread
import sys
from pathlib import Path
import math
from sklearn.linear_model import LinearRegression

from traitlets import Bool

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
        self.coefficients = []
        self.intercept : float
        self.speedReference : float
        self.currentX : float
        self.currentY : float
        self.collisionTime: float
        self.prevCollisionTime: float
        self.collisionDistance: float
        self.actualSpeed: float
        self.readingCounter = 0
        self.readyforPrediction = False


        self.SpeedSlope = (absolutMaxSpeed-absolutMinSpeed)/(upperTimeThreshold-lowerTimeThreshold)
        self.SpeedIntercept = absolutMinSpeed-self.SpeedSlope*lowerTimeThreshold
'''
    def neededSpeedReference (self):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
        if (self.collisionTime >= self.upperTimeThreshold):
            self.neededSpeed = 0.8#self.absolutMaxSpeed
        elif (self.collisionTime < self.lowerTimeThreshold):
            self.speedReference = 0
        else:
            self.speedReference = self.SpeedSlope*self.collisionTime+self.SpeedIntercept
'''
class human:
    def __init__ (self, tagID): # tagID -> tag_id_from_json
        self.tagID = tagID
        self.xPath = []
        self.yPath = []
        self.yPredictions = []
        self.xPredictions = []
        self.xCoefficients = []
        self.yCoefficients = []
        self.xIntercept : float
        self.yIntercept : float
        self.actualSpeed : float
        self.currentX : float
        self.currentY: float
        self.collisionTime: float
        self.collisionDistance: float
        self.readingCounter = 0
        self.readyforPrediction = False

#code purely for running the test case

def neededSpeedReference (robot):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
    if (robot.collisionTime >= robot.upperTimeThreshold):
        return (robot.absolutMaxSpeed)#self.absolutMaxSpeed

    elif (robot.collisionTime < robot.lowerTimeThreshold):
        return 0

    else:
        return (robot.SpeedSlope*robot.collisionTime+robot.SpeedIntercept)

def fillAndUpdatePositionListRobot(positions_per_second, positions_saved, xList, yList, robot):
    counter = 0
    
    while True:
        
        try:
            robot_status = robot_api.robot_status_direct(robot.robotIP)
            # Saves the newest position in a list. This list is limited to n elements
            xyValues = (map.convert_robot_position_for_unification(robot_status['position']['x'], robot_status['position']['y']))
            xList.append(xyValues[0]) # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION
            yList.append(xyValues[1]) # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION

            if len(xList) != len(yList): # Handles the case where xPath and yPath have a different number of elements, though I don't see how that could happen
                print("ERROR in positional tracking. Resetting position list") # This message should maybe be sent somewhere other than the terminal, if it is needed at all
                xList.clear()
                yList.clear()
            elif len(xList) > positions_saved:
                del xList[0]
                del yList[0]
            if (counter%positions_per_second == 0 and counter != 0):

                robot.readyforPrediction = True

                counter = 0
            else:
                counter = counter+1
            
            time.sleep(1/positions_per_second)
            
        except Exception as e:
        
            print(e)




def calculateCurrentSpeed (Xpositionlist = [], Ypositionlist=[], *args):

    total_Xdistance_in_1_sec= abs(Xpositionlist[-1]-Xpositionlist[-4]) # Only a subtraction among the two points is done assuming linearity.
    total_Ydistance_in_1_sec= abs(Ypositionlist[-1]-Ypositionlist[-4]) # Since its 1 second it should not be a problem.

    current_Xspeed = total_Xdistance_in_1_sec  # V=distance/time [m/s]; time is 1s 
    current_Yspeed = total_Ydistance_in_1_sec

    current_speed = np.sqrt(((current_Xspeed**2)+(current_Yspeed**2)))
    return current_speed

def calculateDistanceToCollision(coef_array, intercept, origin_point_x,origin_point_y, collision_point_x, collision_point_y): #input current positions and predictions, output time and or distance until collision
    if origin_point_x <  collision_point_x:
        larger=collision_point_x
        smaller=origin_point_x
        y_coordinate_previous=origin_point_y
        x_coordinate_previous=origin_point_x
        
    else:
        larger=origin_point_x
        smaller=collision_point_x
        y_coordinate_previous=collision_point_y
        x_coordinate_previous=collision_point_x
        
    step=float(larger-smaller)/200
    x=0
    y_coordinate=0
    x_coordinate=0
    distance_y=0
    distance_x=0
    total_distance=0

    while((smaller+x*step)<=larger):
        y_coordinate=coef_array[2]*(smaller+x*step)**3+coef_array[1]*(smaller+x*step)**2+coef_array[0]*(smaller+x*step)+intercept
        distance_y=y_coordinate-y_coordinate_previous 
        y_coordinate_previous=y_coordinate
        x_coordinate=smaller+x*step
        distance_x=x_coordinate-x_coordinate_previous
        x_coordinate_previous=x_coordinate
        total_distance=total_distance + np.sqrt((distance_y**2)+(distance_x**2))
        x=x+1
    return total_distance

def calculateTimeToCollision(distanceToCollision, speed): #input current positions and predictions, output time and or distance until collision
    if speed==0:
        time_to_collision=1000
    else:
        time_to_collision=abs(distanceToCollision)/abs(speed)
    return time_to_collision
  

def findIntercept (lowerRange, upperRange, coeffRobot, interRobot, coeffPerson, interPerson): #f,
    def f(xy):
        x, y = xy
        z = np.array([y-coeffRobot[2]*x**3-coeffRobot[1]*x**2-coeffRobot[0]*x-interRobot, y-coeffPerson[2]*x**3-coeffPerson[1]*x**2-coeffPerson[0]*x-interPerson])
        return z
    return (fsolve(f, [lowerRange, upperRange]))

def takeCrossingIntoAccount (interception, xRobot, yRobot, xPerson, yPerson):
    if (xRobot[0]<xRobot[-1]):
        xRobotSmall = xRobot[0]
        xRobotBig = xRobot[-1]
    else:
        xRobotSmall = xRobot[-1]
        xRobotBig = xRobot[0]
        
    if (xPerson [0] < xPerson[-1]):
        xPersonSmall = xPerson[0]
        xPersonBig = xPerson[-1]
    else:
        xPersonSmall = xPerson[-1]
        xPersonBig = xPerson[0]
    
    if ((((xRobot[0]-interception[0])**2+(yRobot[0]-interception[1])**2) < ((xRobot[-1]-interception[0])**2+(yRobot[-1]-interception[1])**2)) or (((xPerson[0]-interception[0])**2+(yPerson[0]-interception[1])**2) < ((xPerson[-1]-interception[0])**2+(yPerson[-1]-interception[1])**2)) or (xRobotSmall < interception[0] < xRobotBig) or (xPersonSmall < interception[0] < xPersonBig)): #If collision point was closer in t-4 than in the latest position, the robot is going away from the collision point->No need to take it into account
        return False
    else: #collision must be taken into account
        return True 
    
def areCollisionTimesClose (robotTimeToCollide, personTimeToCollide, delta):
    if (((robotTimeToCollide+delta) >= personTimeToCollide) or ((robotTimeToCollide-delta) <= personTimeToCollide)):
        return True
    else:
        return False

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
                #print(distanceAmongPoints)
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
