# robotHumanClass.robot.xPath[]
# robotHumanClass.robot.yPath[]

import robotHumanClass

robot1 = robotHumanClass.robot(100, 1.1, 0.1) # It is assumed that an instance of the robot class has already been called, named robot

for x in range(40):
    robot1.xPathTemp.append('Hello World! This is number ' + str(x))

for x in range(20):
    robot1.xPath.append(robot1.xPathTemp[len(robot1.xPathTemp)-(20-x)])
    if x == 19:
        print("Successfully copied the list")
        robot1.xPathTemp.clear()

for x in range(20):
    print(robot1.xPath[x])
