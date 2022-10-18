             # controller -> move method:
class robot: # finalXY -> self.move_x_entry.get()
             # robotID -> self.id_option_value.get()
             # robotIP -> self.robot_records[robot_record_key].ip
             # currentX -> coordinates_from_json["x"] & coordinates_from_json["y"]
    def __init__ (self, robotIP, currentXcoord, currentYcoord, finalXcoord, finalYcoord, absolutMaxSpeed, absolutMinSpeed):
        self.robotIP = robotIP
        self.curretnXcoord = currentXcoord
        self.currentYcoord = currentYcoord
        self.finalXcoord = finalXcoord
        self.finalYcoord = finalYcoord
        self.absolutMaxSpeed = absolutMaxSpeed
        self.absolutMinSpeed = absolutMinSpeed

    def setSpeed (self):
        pass

class human:
    def __init__ (self, tagID, currentXcoord, currentYcoord):
        self.tagID = tagID
        self.currentXcoord = currentXcoord
        self.currentYcoord = currentYcoord



def predictNpoints(): #output predictedYcoord and predictedXcoord
    pass

def calculateVelocity():
    pass