#code purely for running the test case
import robotHumanClass
robot1 = robotHumanClass.robot(100, 1.1, 0.1)
n = 0


# Saves the newest position in a list. This list is limited to 20 elements
def take_measurement():
    robot1.xPath.append('Hello World! This is number ' + str(n)) #CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION
    robot1.yPath.append('Hello World!')
    if len(robot1.xPath) > 20: # this if-statement neglects the case where xPath and yPath have a different number of elements, though I don't see how that could happen
        del robot1.xPath[0]



#code purely for running the test case
while(n<25):
    take_measurement()
    n+=1
for x in range(len(robot1.xPath)):
    print(robot1.xPath[len(robot1.xPath)-(20-x)])