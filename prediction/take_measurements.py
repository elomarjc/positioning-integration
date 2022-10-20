# robotHumanClass.robot.xPath[]
# robotHumanClass.robot.yPath[]

import robotHumanClass

robot1 = robotHumanClass.robot(100, 1.1, 0.1) # It is assumed that an instance of the robot class has already been called, named robot

robot1.xPath[1] = ('Hello World!')

print(robot1.xPath[1])
