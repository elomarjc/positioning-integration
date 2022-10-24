#code purely for running the test case
import robotHumanClass
import time
from threading import Thread
robot1 = robotHumanClass.robot(100, 1.1, 0.1)

def take_measurement():
    positions_per_second = 4
    positions_saved = 12
    while True:
        # Saves the newest position in a list. This list is limited to n elements
        robot1.xPath.append('xHello World! This is number ')# + str(n)) # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION
        robot1.yPath.append('yHello World!') # CHANGE THIS TO CALL THE API FOR POSITIONAL INFORMATION
        if len(robot1.xPath) != len(robot1.yPath): # Handles the case where xPath and yPath have a different number of elements, though I don't see how that could happen
            print("ERROR in positional tracking. Resetting position list") # This message should maybe be sent somewhere other than the terminal, if it is needed at all
            robot1.xPath.clear()
            robot1.yPath.clear()
        elif len(robot1.xPath) > positions_saved:
            del robot1.xPath[0]
            del robot1.yPath[0]
        if (len(robot1.xPath)%positions_per_second == 0 and len(robot1.yPath)%positions_per_second == 0 and k != 0):
            print("Call the next function") # CALL FOR LINEAR REGRESSION
        time.sleep(1/positions_per_second)


# run the prediction algorithm thread
t_prediction = Thread(target=take_measurement)
t_prediction.start()

### TRY THIS ON MONDAY ###
print(json_object_from_mqtt[0]["data"]["coordinates"])