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
        self.xPathTemp = []
        self.yPath = []
        self.yPathTemp = []
        self.speedReference : float
        self.currentX : float
        self.currentY : float
        self.collisionTime: float

    def neededSpeedReference (self):  #input the time to collide or distance to collide and outpu define the speed that the robot must have
        pass

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

