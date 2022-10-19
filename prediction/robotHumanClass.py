import robot.robot_api             
            

             # controller -> move method:
class robot: # finalXY -> self.move_x_entry.get()
             # robotID -> self.id_option_value.get()
             # robotIP -> self.robot_records[robot_record_key].ip
             # currentX -> coordinates_from_json["x"] & coordinates_from_json["y"]
    def __init__ (self, robotIP, absolutMaxSpeed, absolutMinSpeed):
        self.robotIP = robotIP
        self.absolutMaxSpeed = absolutMaxSpeed # maximum speed that the robot can have
        self.absolutMinSpeed = absolutMinSpeed # minimum speed that the robot can have
        self.yPredictions = []
        self.xPredictions = []
        self.xPath = []
        self.yPath = []
        self.speedReference : float
        self.currentX : float
        self.currentY : float
        self.collisionTime: float

    def neededSpeedReference (tc: float, absolutMaxSpeed:float, absolutMinSpeed:float, robot_ip:str):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
        t1 = 2 # (adjustable lower limt) time in sec before collision
        t2 = 6  # (adjustable upper limit) time in sec before collision

        m = (absolutMaxSpeed-absolutMinSpeed)/(t2-t2) # calculate slope
        n = absolutMinSpeed-(m*t2) # calculate intercept

        if tc < t1:
            v = 0 # since the robot has a limit of 0.1 when v = 0 we should pause the robot -> robot.robot_api.pause(robot_ip)

        elif t1 <= tc <= t2: #if t_c is more than min and less than max, then set speed accoording to a function of t_c
            v = m*tc+(n)  

        else:
            v = absolutMaxSpeed
        
class human:
    def __init__ (self, tagID): # tagID -> tag_id_from_json
        self.tagID = tagID
        self.xPath = []
        self.yPath = []
        self.yPredictions = []
        self.xPredictions = []
        self.speed : float
        self.currentX : float
        self.currentY: float
        self.collisionTime: float

def fillAndUpdatePositionList (newX, newY): #input the readings of position. Update rate 1s, get 4 points per second -> Add a chunck of 4 points every sencond deleting the oldest 4. Get data of last 3-4 seconds
    pass

def calculateCurrentSpeed(): #Could be used to calculate the current person speed and perhaps robots speed
    pass

def calculateCollision(): #input current positions and predictions, output time and or distance until collision
    pass

def predictNpoints(listOfX, listOfY): #output predictedYcoord and predictedXcoord
     pass

