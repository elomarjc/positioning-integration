from scipy.optimize import fsolve
import numpy as np
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.preprocessing import PolynomialFeatures
import warnings

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

    def neededSpeedReference (self):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
         if (self.collisionTime >= self.upperTimeThreshold):
            self.neededSpeed = self.absolutMaxSpeed

         elif (self.collisionTime < self.lowerTimeThreshold):
            self.speedReference = 0

         else:
            self.speedReference = self.SpeedSlope*self.collisionTime+self.SpeedIntercept

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

def fillAndUpdatePositionList (newX, newY): #input the readings of position. Update rate 1s, get 4 points per second -> Add a chunck of 4 points every sencond deleting the oldest 4. Get data of last 3-4 seconds
    pass

def calculateCurrentSpeed (Xpositionlist = [], Ypositionlist=[], *args):

    total_Xdistance_in_1_sec= Xpositionlist[-1]-Xpositionlist[-4] # Only a subtraction among the two points is done assuming linearity.
    total_Ydistance_in_1_sec= Ypositionlist[-1]-Ypositionlist[-4] # Since its 1 second it should not be a problem.

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
    time_to_collision=distanceToCollision/speed
    return time_to_collision

def predictPaths(listOfX, listOfY): #output predictedYcoord and predictedXcoord
    xArray = np.array([])

    for x in listOfX:
        xArray = np.append(xArray, x)

    polynomial = PolynomialFeatures(degree=3, include_bias=False)
    polynomial_features = polynomial.fit_transform(xArray.reshape(-1, 1))
    polynomial_regression_model = linear_model.LinearRegression()

    model = polynomial_regression_model.fit(polynomial_features, listOfY)

    return model.coef_, model.intercept_

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
    if (((robotTimeToCollide+delta) >= personTimeToCollide) and ((robotTimeToCollide-delta) <= personTimeToCollide)):
        return True
    else:
        return False