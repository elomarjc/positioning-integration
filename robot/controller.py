import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import tkinter
from PIL import ImageTk
import threading

import tools.basewindow
import tools.map
import tools.tools
import robot.robot_api


class robot_controller():

    def __init__(self, control_panel: tkinter.Frame, robot_records: dict,
                 robot_records_lock: threading.Lock,
                 map_canvas: tkinter.Canvas):
        self.control_panel = control_panel
        self.robot_records = robot_records
        self.robot_records_lock = robot_records_lock
        self.map_canvas = map_canvas

        self.initialize_control_panel()

        # to preview the position to move to
        self.position_icon_photo = ImageTk.PhotoImage(
            tools.map.new_position_icon)
        self.canvas_tag = "preview"

    # create the objects on control panel
    def initialize_control_panel(self):
        base_rely = 0
        spacing = 0.07

        # The label and option menu to choose a robot to control
        operate_label_rely = 0.07
        self.operate_label = tkinter.Label(self.control_panel,
                                           text="Robot ID:",
                                           font=tools.basewindow.text_font)
        self.operate_label.pack()
        self.operate_label.place(relx=0.57,
                                 rely=base_rely + operate_label_rely,
                                 anchor=tkinter.E)

        self.robot_ids = ["0"]
        self.id_option_value = tkinter.StringVar(self.control_panel)
        self.id_option_value.set("0")
        self.id_option = tkinter.OptionMenu(self.control_panel,
                                            self.id_option_value,
                                            *(self.robot_ids))
        self.id_option.pack()
        self.id_option.place(relx=0.59,
                             rely=base_rely + operate_label_rely,
                             anchor=tkinter.W)

        base_rely = base_rely + operate_label_rely + spacing

        # The labels and input box to specify a position to move to
        self.move_label = tkinter.Label(
            self.control_panel,
            text="Move to the position (coordinates):",
            font=tools.basewindow.text_font)
        self.move_label.pack()
        self.move_label.place(relx=0.5, rely=base_rely, anchor=tkinter.CENTER)

        # specify the x coordinate
        self.move_x_label = tkinter.Label(self.control_panel,
                                          text="X:",
                                          font=tools.basewindow.text_font)
        self.move_x_label.pack()
        self.move_x_label.place(relx=0.28,
                                rely=base_rely + 0.04,
                                anchor=tkinter.E)

        self.move_x_entry = tkinter.Entry(self.control_panel,
                                          font=tools.basewindow.text_font,
                                          width=7)
        self.move_x_entry.pack()
        self.move_x_entry.place(relx=0.30,
                                rely=base_rely + 0.04,
                                anchor=tkinter.W)

        # specify the y coordinate
        self.move_y_label = tkinter.Label(self.control_panel,
                                          text="Y:",
                                          font=tools.basewindow.text_font)
        self.move_y_label.pack()
        self.move_y_label.place(relx=0.55,
                                rely=base_rely + 0.04,
                                anchor=tkinter.E)

        self.move_y_entry = tkinter.Entry(self.control_panel,
                                          font=tools.basewindow.text_font,
                                          width=7)
        self.move_y_entry.pack()
        self.move_y_entry.place(relx=0.57,
                                rely=base_rely + 0.04,
                                anchor=tkinter.W)

        # 3 button about the "move" function
        self.move_preview_button = tkinter.Button(
            self.control_panel,
            text="Preview",
            font=tools.basewindow.button_font,
            command=self.preview)
        self.move_preview_button.pack()
        self.move_preview_button.place(relx=0.25,
                                       rely=base_rely + 0.09,
                                       anchor=tkinter.CENTER)

        self.move_clear_button = tkinter.Button(
            self.control_panel,
            text="Clear",
            font=tools.basewindow.button_font,
            command=self.clear)
        self.move_clear_button.pack()
        self.move_clear_button.place(relx=0.5,
                                     rely=base_rely + 0.09,
                                     anchor=tkinter.CENTER)

        self.move_move_button = tkinter.Button(
            self.control_panel,
            text="Move",
            font=tools.basewindow.button_font,
            command=self.move)
        self.move_move_button.pack()
        self.move_move_button.place(relx=0.75,
                                    rely=base_rely + 0.09,
                                    anchor=tkinter.CENTER)

        base_rely = base_rely + 0.09 + spacing

        # set speed (speed = abs(linear_velocity)
        self.set_speed_label = tkinter.Label(self.control_panel,
                                             text="Set speed as:",
                                             font=tools.basewindow.text_font)
        self.set_speed_label.pack()
        self.set_speed_label.place(relx=0.57, rely=base_rely, anchor=tkinter.E)

        self.set_speed_entry = tkinter.Entry(self.control_panel,
                                             font=tools.basewindow.text_font,
                                             width=7)
        self.set_speed_entry.pack()
        self.set_speed_entry.place(relx=0.59, rely=base_rely, anchor=tkinter.W)

        self.set_speed_button = tkinter.Button(
            self.control_panel,
            text="Set",
            font=tools.basewindow.button_font,
            command=self.set_robot_speed)
        self.set_speed_button.pack()
        self.set_speed_button.place(relx=0.5,
                                    rely=base_rely + 0.05,
                                    anchor=tkinter.CENTER)

        base_rely = base_rely + 0.05 + spacing

    # when robot ids change we update
    def update_id_option(self, new_robot_ids: list):
        if set(self.robot_ids) != set(new_robot_ids):
            self.robot_ids.clear()
            menu = self.id_option['menu']
            menu.delete(0, 'end')
            for id in new_robot_ids:
                self.robot_ids.append(id)
                menu.add_command(
                    label=id, command=lambda x=id: self.id_option_value.set(x))
            if len(self.robot_ids) > 0:
                self.id_option_value.set(self.robot_ids[0])

    # preview the coordinates on the map
    def preview(self):
        x = self.move_x_entry.get()
        y = self.move_y_entry.get()
        print("Preview the coordinates: ({}, {}).".format(x, y))
        robot_x, robot_y = tools.map.reverse_convert_robot_position_for_unification(
            float(x), float(y))
        tools.map.show_position_icon(
            self.map_canvas, tools.basewindow.proportion, robot_x, robot_y,
            self.canvas_tag, self.position_icon_photo, "",
            tools.map.convert_robot,
            tools.map.convert_robot_position_for_unification, 0, 10)

    # clear the preview coordinates on the map
    def clear(self):
        print("Clear the preview coordinates.")
        self.map_canvas.delete(self.canvas_tag)

    # move the selected robot to a specified position
    def move(self):
        robot_id = self.id_option_value.get()
        robot_record_key = tools.tools.robot_canvas_tag(robot_id)
        robot_ip = self.robot_records[robot_record_key].ip
        dst_x = self.move_x_entry.get()
        dst_y = self.move_y_entry.get()
        print("Move Robot {}, IP: {} to ({}, {}).".format(
            robot_id, robot_ip, dst_x, dst_y))
        original_robot_x, original_robot_y = tools.map.reverse_convert_robot_position_for_unification(
            float(dst_x), float(dst_y))
        # the following three steps: (1)move; (2)clear errors; (3)unpause.
        # They are copied from Allan's code:
        # wireless-realsense\MiR_REST_base.py:
        # "def go_to_coordinates(_robot_ip, _coordinates)"
        # Probably because the errors and pause may block the behaviors of the robots.
        robot.robot_api.clear_mission_queue(
            robot_ip
        )  # I added this, clear previous tasks to avoid being blocked
        robot.robot_api.move(robot_ip, original_robot_x, original_robot_y)
        robot.robot_api.clear_errors(robot_ip)
        robot.robot_api.un_pause(robot_ip)

    # set robot speed
    def set_robot_speed(self):
        robot_id = self.id_option_value.get()
        robot_record_key = tools.tools.robot_canvas_tag(robot_id)
        robot_ip = self.robot_records[robot_record_key].ip
        desired_speed = self.set_speed_entry.get()
        robot.robot_api.set_max_speed(robot_ip, "1.1")
        robot.robot_api.set_desired_speed(robot_ip, desired_speed)