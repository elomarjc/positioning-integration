from concurrent.futures import thread
import robotHumanClass
import sys
from pathlib import Path
from threading import Thread
import multiprocessing as mp

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import robot.robot_api  # use API to get data from Robot
import tools.map
import time
robot_ip="192.168.100.2"
robot1 = robotHumanClass.robot(robot_ip, 1.1, 0.1, 2, 1)

robot_x, robot_y = tools.map.reverse_convert_robot_position_for_unification(
    float(0), float(11))
robot.robot_api.clear_mission_queue(robot_ip)
robot.robot_api.move(robot_ip, robot_x, robot_y)
robot.robot_api.clear_errors(robot_ip)
robot.robot_api.un_pause(robot_ip)



t_prediction = Thread(target=robotHumanClass.fillAndUpdatePositionListRobot, args=(4, 12, robot1.xPath, robot1.yPath, robot1.robotIP))

t_prediction.start()

