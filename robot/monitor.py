import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import tkinter
import threading

import tools.basewindow
import tools.map
import tools.tools


class robot_monitor():

    def __init__(self, left_control_panel: tkinter.Frame,
                 right_control_panel: tkinter.Frame, robot_records: dict,
                 robot_records_lock: threading.Lock):
        self.left_control_panel = left_control_panel
        self.right_control_panel = right_control_panel
        self.robot_records = robot_records
        self.robot_records_lock = robot_records_lock

        self.initialize_monitor()

    def initialize_monitor(self):
        # put a label to show the volocities of robots
        self.velocity_text = tkinter.StringVar()
        self.velocity_label = tkinter.Label(self.left_control_panel,
                                            textvariable=self.velocity_text,
                                            font=tools.basewindow.text_font)
        self.velocity_label.pack()
        self.velocity_label.place(relx=0.5, rely=0.965, anchor=tkinter.S)

    # refresh the speed of robots on the panel
    def refresh_linear_velocity(self):
        velocity_text = "Current speed:"  # speed = abs(linear_velocity)
        for canvas_tag in self.robot_records.keys():
            robot_id = tools.tools.robot_canvas_tag_to_id(canvas_tag)
            # through test, I judge that the unit of the linear velocity is m/s
            velocity_text += "\n{}: {:.3f}m/s".format(
                tools.tools.robot_canvas_text(robot_id),
                abs(float(self.robot_records[canvas_tag].linear_velocity)))
        self.velocity_text.set(velocity_text)
