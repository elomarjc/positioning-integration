from math import dist
import sys
from pathlib import Path
from textwrap import fill

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import tkinter
import threading

import tools.tools
import tools.basewindow
import tools.map
import robot.robot_api


# every alarm level has a triggering distance, and a alarm color
class alarm_level():

    def __init__(self, triggering_dist: float, color: str,
                 robot_max_speed: str):
        self.triggering_dist = triggering_dist
        self.color = color
        self.robot_max_speed = robot_max_speed


# An alarm is composed of a robot, another object, and the distance between them
class one_alarm():

    def __init__(self, robot_id: str, another_obj: str, dist_between: float):
        self.robot_id = robot_id
        self.another_obj = another_obj
        self.dist_between = dist_between

    def alarm_str(self):
        return '"{}" to "{}": {:.2f}m'.format(self.robot_id, self.another_obj,
                                              self.dist_between)


# To generate alarms for robots
class robot_alarms():

    def __init__(
        self,
        control_panel: tkinter.Frame,
        cv_records: dict,
        cv_records_lock: threading.Lock,
        uwb_records: dict,
        uwb_records_lock: threading.Lock,
        robot_records: dict,
        robot_records_lock: threading.Lock,
    ):
        self.control_panel = control_panel
        self.cv_records = cv_records
        self.cv_records_lock = cv_records_lock
        self.uwb_records = uwb_records
        self.uwb_records_lock = uwb_records_lock
        self.robot_records = robot_records
        self.robot_records_lock = robot_records_lock

        self.alarm_lock = threading.Lock(
        )  # to avoid refreshing alarm in wrong timing.

        self.alarms: list[one_alarm] = []
        # define alarm levels, and distances
        # 0: no alarm; 1: yellow alarm; 2: red alarm
        self.current_alarm_level: int = 0
        self.alarm_levels: list[alarm_level] = []
        self.alarm_levels.append(
            alarm_level(100, tools.basewindow.FRESH_LEAVES, "1.1"))
        self.alarm_levels.append(
            alarm_level(2, tools.basewindow.MARIGOLD, "0.5"))
        self.alarm_levels.append(alarm_level(1, tools.basewindow.RED, "0.1"))

        base_rely = 0
        spacing = 0.06

        # put explanation of alarms
        base_rely += 0.03

        # title
        title_text = "Safety Alarm Zones"
        alarm_zone_title = tkinter.Label(self.control_panel,
                                         text=title_text,
                                         font=tools.basewindow.text_font_big)
        alarm_zone_title.pack()
        alarm_zone_title.place(relx=0.5, rely=base_rely, anchor=tkinter.CENTER)
        # title of the table
        base_rely += 0.04
        this_spacing = 0.03
        self.alarm_zone_texts = [tkinter.Label]
        table_title_text = "Level\tRadius\tSpeed Limit"
        table_title = tkinter.Label(self.control_panel,
                                    text=table_title_text,
                                    font=tools.basewindow.text_font)
        table_title.pack()
        table_title.place(relx=0.5, rely=base_rely, anchor=tkinter.CENTER)
        base_rely += this_spacing
        self.alarm_zone_texts.append(table_title)
        # content of the table
        level_index = 1
        while level_index < len(self.alarm_levels):
            one_alarm_zone_text = "{}\t{}m\t{}m/s".format(
                level_index, self.alarm_levels[level_index].triggering_dist,
                self.alarm_levels[level_index].robot_max_speed)
            one_alarm_zone_label = tkinter.Label(
                self.control_panel,
                text=one_alarm_zone_text,
                font=tools.basewindow.text_font,
                fg=self.alarm_levels[level_index].color)
            one_alarm_zone_label.pack()
            one_alarm_zone_label.place(relx=0.5,
                                       rely=base_rely,
                                       anchor=tkinter.CENTER)
            base_rely += this_spacing
            self.alarm_zone_texts.append(one_alarm_zone_label)
            level_index += 1

        # put a checkbutton on the control panel to turn on/off the alarm area display
        base_rely = base_rely - this_spacing + spacing
        self.area_on = tkinter.BooleanVar()
        self.area_on.set(True)
        self.area_switch = tkinter.Checkbutton(
            self.control_panel,
            text="Show safety alarm zones on the map.",
            font=tools.basewindow.text_font,
            variable=self.area_on,
            onvalue=True,
            offvalue=False)
        self.area_switch.pack()
        self.area_switch.place(relx=0.5, rely=base_rely, anchor=tkinter.CENTER)

        # put alarm on the control panel
        base_rely += 0.04
        self.alarm_text = tkinter.StringVar()
        self.alarm_label = tkinter.Label(self.control_panel,
                                         textvariable=self.alarm_text,
                                         font=tools.basewindow.text_font)
        self.alarm_label.pack()
        self.alarm_label.place(relx=0.5, rely=base_rely, anchor=tkinter.N)

    # Check whether any objects are too close to any robots.
    # This method should be executed when any objects change on the map.
    # For example,
    # robot move, robot appear, robot disappear,
    # uwbtag move/appear/disappear,
    # person in cv move/appear/disappear
    # However, to reduce the compuation resource consumption, we limit the refresh rate of alarm, using influxdb write rate to limit alarm rate
    # If it is necessary, we can also consider executing this method periodically in a separated thread.
    def refresh_alarm(self):
        if self.alarm_lock.locked():
            return  # At one time, we only need to one refresh rather than repeated refresh
        self.alarm_lock.acquire()
        print("Refresh alarms.")
        # reset the status firstly
        self.alarms.clear()
        self.current_alarm_level = 0
        for robot_id in self.robot_records.keys():
            self.robot_records[robot_id].current_alarm_level = 0

        accessed_robots = set()  # To avoid repeated alarms between 2 robots
        self.robot_records_lock.acquire()
        for robot_id in self.robot_records.keys():
            accessed_robots.add(robot_id)

            # refresh alarm: robot vs cv
            self.cv_records_lock.acquire()
            print("Alarm, current cv:")
            print(self.cv_records.keys())
            self.refresh_one_type(robot_id, self.cv_records, accessed_robots)
            self.cv_records_lock.release()

            # refresh alarm: robot vs uwb
            self.uwb_records_lock.acquire()
            print("Alarm, current uwb:")
            print(self.uwb_records.keys())
            self.refresh_one_type(robot_id, self.uwb_records, accessed_robots)
            self.uwb_records_lock.release()

            # refresh alarm: robot vs robot
            print("Alarm, current robots:")
            print(self.robot_records.keys())
            self.refresh_one_type(robot_id, self.robot_records,
                                  accessed_robots)
        self.robot_records_lock.release()

        # display alarms on the window
        self.publish_alarms()

        # adjust the speed of the robots according to their alarm levels
        self.adjust_speed()

        self.alarm_lock.release()

    # refresh the alarm about one type (cv, uwb, robot)
    def refresh_one_type(self, robot_id: str, records: dict, acceesed: set):
        for key in records.keys():
            if key in acceesed:  # jump the accessed obj
                continue

            # jump the pairs with alarm exemption
            if robot_id in tools.tools.alarm_exemption_conf.keys():
                if tools.tools.alarm_exemption_conf[robot_id] == key:
                    continue

            # calculate the distance between this robot and this object
            dist_between = tools.tools.get_dist(self.robot_records[robot_id].x,
                                                self.robot_records[robot_id].y,
                                                records[key].x, records[key].y)

            # find the level of alarm that should be generate
            index = len(self.alarm_levels) - 1
            while index >= 1 and dist_between > self.alarm_levels[
                    index].triggering_dist:
                index -= 1
            if index >= 1:
                new_alarm = one_alarm(self.robot_records[robot_id].alarm_text,
                                      records[key].alarm_text, dist_between)
                self.alarms.append(new_alarm)
                if index > self.current_alarm_level:
                    self.current_alarm_level = index
                # record the alarm of every robot, to adjust the speed
                if index > self.robot_records[robot_id].current_alarm_level:
                    self.robot_records[robot_id].current_alarm_level = index
                # ip != "" means that it is a robot
                if records[key].ip != "" and index > records[
                        key].current_alarm_level:
                    records[key].current_alarm_level = index

    # show current alarms on the control panel
    def publish_alarms(self):
        # set alarm color for the control panel
        print("Current alarm level: {}. Alarm, set control panel color: {}".
              format(self.current_alarm_level,
                     self.alarm_levels[self.current_alarm_level].color))
        self.control_panel.config(
            bg=self.alarm_levels[self.current_alarm_level].color)
        if len(self.alarms) == 0:  # if no alarm
            self.alarm_text.set("Safe distance.")
        else:
            # generate alarm text
            alarm_text = "Safety alarms:"
            for alarm in self.alarms:
                alarm_text += "\n" + alarm.alarm_str()
            # put the alarm text on the control panel
            self.alarm_text.set(alarm_text)

    # adjust the speed of the robots according to their alarm levels
    def adjust_speed(self):
        for robot_id in self.robot_records.keys():
            max_speed = self.alarm_levels[self.robot_records[robot_id].
                                          current_alarm_level].robot_max_speed
            robot_ip = self.robot_records[robot_id].ip
            robot.robot_api.set_max_speed(robot_ip, max_speed)

    def show_areas(self, canvas_map: tkinter.Canvas, proportion: float, x, y,
                   canvas_tag: str):
        # draw circles with the center (converted_x, converted_y)
        converted_x, converted_y = tools.map.convert_robot(
            float(x), float(y), proportion)

        # For every alarm level, draw a circle
        level_index = 1
        while level_index < len(self.alarm_levels):
            # the radius of the circle should be "self.alarm_levels[level_index].triggering_dist", unit: meter.
            # We should convert it from meter to pixel
            # "5cm is 1 pixel!" (see the comments of the convert methods in the file "tools\map.py")
            radius = self.alarm_levels[
                level_index].triggering_dist * 100 / 5 * proportion
            x1 = converted_x - radius
            y1 = converted_y - radius
            x2 = converted_x + radius
            y2 = converted_y + radius
            canvas_map.create_oval(
                x1,
                y1,
                x2,
                y2,
                outline="{}".format(self.alarm_levels[level_index].color),
                tag=canvas_tag)  # do not set fill, it will be transparent
            level_index += 1
