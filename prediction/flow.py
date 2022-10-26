from concurrent.futures import thread
import robotHumanClass
import warnings
warnings.filterwarnings("error")
import sys
from pathlib import Path
from threading import Thread
from datetime import datetime
from robot import robot_api
import robotHumanClass


sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import robot.robot_api  # use API to get data from Robot
import tools.map
import time
robot_ip="192.168.100.2"
tag_id="1888"
lower_range=0
upper_range=0
delta=5
setSpeedTime=0
robot1 = robotHumanClass.robot(robot_ip, 1.1, 0.1, 2, 1)
human1 = robotHumanClass.human(tag_id)

while True:
    if(robotHumanClass.fourNewMeasurements):
        robot1.coefficients, robot1.intercept = robotHumanClass.predictPaths(robot1.xPath, robot1.yPath)
        human1.coefficients, human1.intercept = robotHumanClass.predictPaths(human1.xPath, human1.yPath)
        try:
            intercept = robotHumanClass.findIntercept(lower_range, upper_range, robot1.coefficients, robot1.intercept, human1.coefficients, human1.intercept)
        except RuntimeWarning:
            intercept = -1

        if (type(intercept)== int):
            print("No collision danger, there is no intercept")

        else:
            if(not robotHumanClass.takeCrossingIntoAccount):
                print("No collision danger, the moving objects are moving away from intercept")
            else:
                #xapth[-1] denbora guztian aktualizatzen doia
                robot1.collisionDistance = robotHumanClass.calculateDistanceToCollision(robot1.coefficients, robot1.intercept, robot1.xPath[-1],robot1.yPath[-1],intercept[0],intercept[1])
                human1.collisionDistance = robotHumanClass.calculateDistanceToCollision(human1.coefficients, human1.intercept, human1.xPath[-1],human1.yPath[-1],intercept[0],intercept[1])
                robot_status = robot_api.robot_status_direct(robot1.robotIP)
                robot1.actualSpeed = robot_status['velocity']['linear']
                #robot1.actualSpeed = robotHumanClass.calculateCurrentSpeed(robot1.xPath,robot1.yPath)#read from API
                human1.actualSpeed = robotHumanClass.calculateCurrentSpeed(human1.xPath,human1.yPath)

                robot1.collisionTime = robotHumanClass.calculateTimeToCollision(robot1.collisionDistance, robot1.actualSpeed)
                human1.collisionTime = robotHumanClass.calculateTimeToCollision(human1.collisionDistance, human1.actualSpeed)
                if((robotHumanClass.areCollisionTimesClose(robot1.collisionTime, human1.collisionTime, delta)) and ((((datetime.now()-setSpeedTime).seconds) > robot1.prevCollisionTime) or (robot1.collisionTime < robot1.prevCollisionTime)) ):
                    print()
                    robot1.speedReference= robot1.neededSpeedReference()
                    robot1.prevCollisionTime = robot1.collisionTime

                    #PONER EN EL API LA VELOCIDAD
                    setSpeedTime= datetime.now()
                else:
                    #PONER EN EL API LA VELOCIDAD maxima
                    pass

    else:
        pass