import math
import json

# We can define the name of each UWB tag in the file: conf/person_with_tag.conf.
# There are some examples in this file, and we can imitate these examples to create new lines.
# We do not need to delete the examples, because no UWB tag can map them, so they do not have effects.
person_with_tag_conf = dict()
with open("conf/person_with_tag.conf", 'r', encoding='utf-8') as f:
    person_with_tag_conf = json.load(f)

# For a Robot not connected to the fleet-manager, we can give it an ID, and configure the ID and Robot IP into the file conf/extra_robots.conf. The robots in this file will be monitored and managed by this application.
extra_robots_conf = dict()
with open("conf/extra_robots.conf", 'r', encoding='utf-8') as f:
    extra_robots_conf = json.load(f)

# When we need to put a UWBtag on a robot, we can set them as alarm exemption in the configuration file conf/alarm_exemption.conf.
# Then their will not be alarms generated due to their close distance, and thereby the robot speed will not decrease.
alarm_exemption_conf = dict()
with open("conf/alarm_exemption.conf", 'r', encoding='utf-8') as f:
    alarm_exemption_conf = json.load(f)


# record the x, y and time of a coordinate
class coor():

    def __init__(self,
                 x,
                 y,
                 t,
                 alarm_text="",
                 ip="",
                 linear_velocity="",
                 current_alarm_level=0):
        self.x = x
        self.y = y
        self.t = t
        self.alarm_text = alarm_text
        self.ip = ip
        self.linear_velocity = linear_velocity
        self.current_alarm_level = current_alarm_level


# record the last record of a cvID/tagID/robotID in influxdb
class last_influxDB_records():

    def __init__(self):
        self.cv = dict()
        self.uwb = dict()
        self.robot = dict()


# generate canvas_tag from UWB tagID
def uwb_canvas_tag(id):
    return "uwbtagid{}".format(id)


# generate canvas_text from UWB tagID
def uwb_canvas_text(id):
    original_text = "UWBtag {}".format(id)
    if original_text in person_with_tag_conf.keys():
        return person_with_tag_conf[original_text]
    return "UWBtag {}".format(id)


# generate canvas_tag from the ID given by CV
def cv_canvas_tag(id):
    return "cvid{}".format(id)


# generate canvas_text from the ID given by CV
def cv_canvas_text(id):
    return "Person {}".format(id)


# generate canvas_tag from the Robot ID
def robot_canvas_tag(id):
    return "robotid{}".format(id)


# get Robot ID from canvas_tag
def robot_canvas_tag_to_id(canvas_tag: str):
    return canvas_tag[7::]


# generate canvas_text from the Robot ID
def robot_canvas_text(id):
    return "Robot {}".format(id)


# calculate the distance between (x1, y1) and (x2, y2)
def get_dist(x1, y1, x2, y2):
    return math.sqrt(
        pow((float(x1) - float(x2)), 2) + pow((float(y1) - float(y2)), 2))
