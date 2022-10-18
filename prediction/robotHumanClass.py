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
        self.absolutMaxSpeed = absolutMaxSpeed #use method "set_robot_speed" under controller.py line 217
        self.absolutMinSpeed = absolutMinSpeed #use method "set_robot_speed" under controller.py line 217

    def setSpeed (self):   #use method "set_robot_speed" under controller.py line 217
        pass

class human:
    def __init__ (self, tagID, currentXcoord, currentYcoord): # tagID -> tag_id_from_json
        self.tagID = tagID
        self.currentXcoord = currentXcoord
        self.currentYcoord = currentYcoord



def predictNpoints(): #output predictedYcoord and predictedXcoord
    pass

def calculateVelocity():
    pass