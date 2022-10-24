import robotHumanClass

import sys
from pathlib import Path
from threading import Thread

import robot.robot_api
import tools.map
import time

robot1 = robotHumanClass("192.168.100.2", 1.1, 0.1, 2, 1)

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

# robot_x, robot_y = tools.map.reverse_convert_robot_position_for_unification(
#     float(0), float(10))
# robot_x, robot_y = tools.map.reverse_convert_robot_position_for_unification(
#     float(0), float(22))
robot_x, robot_y = tools.map.reverse_convert_robot_position_for_unification(
    float(0), float(10))
robot.robot_api.clear_mission_queue(robot_ip)
robot.robot_api.move(robot_ip, robot_x, robot_y)
robot.robot_api.clear_errors(robot_ip)
robot.robot_api.un_pause(robot_ip)

fillAndUpdatePositionListRobot(4, 12, robot1.xPath, robot1.yPath, robot1.robotIP)

# run the prediction algorithm thread
t_prediction = Thread(target=fillAndUpdatePositionListRobot)
t_prediction.start()

for x in range(21):
    print(robot1.xList)
    time.sleep(1)