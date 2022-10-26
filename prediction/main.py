t_prediction = Thread(target=robotHumanClass.fillAndUpdatePositionListRobot, args=(4, 12, robot1.xPath, robot1.yPath, robot1.robotIP))
t_prediction.start()
main_flowchart = Thread(target=robotHumanClass.fillAndUpdatePositionListRobot, args=())
main_flowchart.start()