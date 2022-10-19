# robotHumanClass.robot.xPath[]
# robotHumanClass.robot.yPath[]

robot = prediction.robotHumanClass(100, 1.1, 0.1) # It is assumed that an instance of the robot class has already been called, named robot

robot.robot.xPath('Hello World!')

print(robot.robot.xPath[0])
