import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2])
                )  # can import files based on the parents path

import time

import tools.map
import robot.robot_api

# (-4, 6)
# (0, 20)

robot_ip = "192.168.100.140"
x1 = -4
y1 = 5
x2 = 0
y2 = 20


def move(x, y):
    original_robot_x, original_robot_y = tools.map.reverse_convert_robot_position_for_unification(
        float(x), float(y))
    robot.robot_api.clear_mission_queue(robot_ip)
    robot.robot_api.move(robot_ip, original_robot_x, original_robot_y)
    robot.robot_api.clear_errors(robot_ip)
    robot.robot_api.un_pause(robot_ip)


def loop_move():
    while (1):
        move(x1, y1)
        time.sleep(60)
        move(x2, y2)
        time.sleep(60)


if __name__ == "__main__":
    loop_move()
