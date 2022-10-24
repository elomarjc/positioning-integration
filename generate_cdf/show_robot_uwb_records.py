import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1])
                )  # can import files based on the parents path

import csv  # operate csv file
import math

from threading import Thread
from threading import Lock
from threading import Timer

from PIL import Image, ImageTk  # put a picture (lab map) in the window
import tkinter  # Python GUI tool, to open a window
import tkinter.font  # to change the font size of titles
import tools.adjustable_text_size
import tools.map

import tools.tools
import tools.basewindow

import time

# button play/pause
play_pause_text = tkinter.StringVar()
play_text = "Play"
pause_text = "Pause"
play_pause_text.set(pause_text)


def play_pause_func():
    global pause
    pause_lock.acquire()
    if play_pause_text.get() != play_text:
        play_pause_text.set(play_text)
        pause = True
    elif play_pause_text.get() != pause_text:
        play_pause_text.set(pause_text)
        pause = False
    pause_lock.release()


play_pause_button = tkinter.Button(tools.basewindow.control_panel,
                                   textvariable=play_pause_text,
                                   font=tools.basewindow.button_font,
                                   command=play_pause_func)
play_pause_button.pack()
play_pause_button.place(relx=0.5, rely=0.13, anchor=tkinter.CENTER)

# set interval between two frames
interval_text = tkinter.StringVar()
interval_label = tkinter.Label(tools.basewindow.control_panel,
                               textvariable=interval_text,
                               font=tools.basewindow.text_font)
interval_label.pack()
interval_label.place(relx=0.5, rely=0.2, anchor=tkinter.CENTER)
interval_set_label = tkinter.Label(tools.basewindow.control_panel,
                                   text="Set interval as:",
                                   font=tools.basewindow.text_font)
interval_set_label.pack()
interval_set_label.place(relx=0.35, rely=0.25, anchor=tkinter.CENTER)
interval_set_entry = tkinter.Entry(tools.basewindow.control_panel,
                                   font=tools.basewindow.text_font,
                                   width=7)
interval_set_entry.pack()
interval_set_entry.place(relx=0.8, rely=0.25, anchor=tkinter.CENTER)


# interval_set_entry.bind will send an "Event" input to set_interval
def set_interval(e):
    try:
        input_interval = interval_set_entry.get()
        interval_set_entry.delete(0, tkinter.END)
        print("set interval to: {}ms".format(input_interval))
        global interval
        interval = float(input_interval)
        interval_text.set("Current interval: {}ms".format(interval))
    except Exception as ex:
        print("error: ", ex)


interval_set_entry.bind('<Return>',
                        set_interval)  # press enter, execute "set_interval"

# jump to a frame
frame_text = tkinter.StringVar()
frame_text.set("Current frame: 0/0")
frame_label = tkinter.Label(tools.basewindow.control_panel,
                            textvariable=frame_text,
                            font=tools.basewindow.text_font)
frame_label.pack()
frame_label.place(relx=0.5, rely=0.35, anchor=tkinter.CENTER)
frame_jump_label = tkinter.Label(tools.basewindow.control_panel,
                                 text="Jump to frame:",
                                 font=tools.basewindow.text_font)
frame_jump_label.pack()
frame_jump_label.place(relx=0.35, rely=0.4, anchor=tkinter.CENTER)

frame_jump_entry = tkinter.Entry(tools.basewindow.control_panel,
                                 font=tools.basewindow.text_font,
                                 width=7)
frame_jump_entry.pack()
frame_jump_entry.place(relx=0.8, rely=0.4, anchor=tkinter.CENTER)


# .bind will send an "Event"
def jump_to(e):
    try:
        aimed_frame = frame_jump_entry.get()
        frame_jump_entry.delete(0, tkinter.END)
        if int(aimed_frame) < 1 or int(aimed_frame) > total_frame:
            return
        print("Jump to frame: {}".format(aimed_frame))
        global frame_index
        frame_index_lock.acquire()
        frame_index = int(aimed_frame) - 1
        frame_text.set("Current frame: {}/{}".format(frame_index + 1,
                                                     total_frame))
        frame_index_lock.release()
    except Exception as ex:
        print("error: ", ex)


frame_jump_entry.bind('<Return>', jump_to)  # press enter, execute

# show positions records
record_text = tkinter.StringVar()
record_text.set("Current record:\nUWB: (0, 0)\nRobot: (0, 0)\nDistance: 0m")
record_label = tkinter.Label(tools.basewindow.control_panel,
                             textvariable=record_text,
                             font=tools.basewindow.text_font)
record_label.pack()
record_label.place(relx=0.5, rely=0.6, anchor=tkinter.CENTER)


# resize the map photo according to the size of the window
def resize():
    tools.basewindow.resize_basewindow()

    # create legends
    tools.basewindow.create_legends(tools.basewindow.canvas_map)

    # try resize every 1s
    t_resize = Timer(1, resize)
    t_resize.start()


resize()

uwb_canvas_tag = "uwb"
robot_canvas_tag = "robot"
uwb_color = "blue"
robot_color = "green"

interval = 100.0  # time interval between two frames
interval_text.set("Current interval: {}ms".format(interval))
interval_lock = Lock()
frame_index = 0
frame_index_lock = Lock()
pause = False
pause_lock = Lock()
total_frame = 0


# read positions records from csv file, and show them on the map
def show_positions():
    record_file_name = "generate_cdf/robotexperiment20220817/every_100ms_uwb_robot_dist.csv"
    records = []  # records is a "list", not a "interator"
    with open(record_file_name, 'r+') as record_file:
        records_tmp = csv.reader(record_file)
        next(records_tmp)  # records_tmp is an "iterator", so it can "next"
        for record in records_tmp:
            records.append(record)  # put data from file to records
    global total_frame
    total_frame = len(records)

    # loop, show every frame on the map according to the frame_index.
    # The frame_index will increasing.
    global frame_index, pause
    while True:
        if pause:
            continue
        if frame_index >= len(records):
            frame_index = 0
        frame_index_lock.acquire()  # lock it to avoid other threads change
        robot_x = records[frame_index][1]
        robot_y = records[frame_index][3]
        uwb_x = records[frame_index][5]
        uwb_y = records[frame_index][7]
        dist = math.sqrt(
            pow((float(robot_x) - float(uwb_x)), 2) +
            pow((float(robot_y) - float(uwb_y)), 2))

        print("robot: ({}, {}), uwb: ({}, {}), distance: {}m".format(
            robot_x, robot_y, uwb_x, uwb_y, dist))
        record_text.set(
            "Current record:\nRobot: ({:.2f}, {:.2f})\nUWB: ({:.2f}, {:.2f})\nDistance: {:.2f}m"
            .format(float(robot_x), float(robot_y), float(uwb_x), float(uwb_y),
                    dist))

        # delete the old point on the map, and draw this point
        tools.basewindow.canvas_map.delete(robot_canvas_tag)
        tools.basewindow.canvas_map.delete(uwb_canvas_tag)
        # draw the new points
        robot_x_origin, robot_y_origin = tools.map.reverse_convert_robot_position_for_unification(
            float(robot_x), float(robot_y))

        tools.map.show_position(
            tools.basewindow.canvas_map, tools.basewindow.proportion,
            robot_x_origin, robot_y_origin, robot_canvas_tag, robot_color, "",
            tools.map.convert_robot,
            tools.map.convert_robot_position_for_unification, 0, 7)

        uwb_x_origin, uwb_y_origin = tools.map.reverse_convert_uwb_position_for_unification(
            float(uwb_x), float(uwb_y))
        tools.map.show_position(tools.basewindow.canvas_map,
                                tools.basewindow.proportion, uwb_x_origin,
                                uwb_y_origin, uwb_canvas_tag, uwb_color, "",
                                tools.map.convert_tags,
                                tools.map.convert_uwb_position_for_unification,
                                0, 7)
        frame_text.set("Current frame: {}/{}".format(frame_index + 1,
                                                     len(records)))
        frame_index += 1
        if frame_index == len(records):
            pause_lock.acquire()
            pause = True  # stop at the last frame
            play_pause_text.set(play_text)
            pause_lock.release()
        frame_index_lock.release()
        time.sleep(interval / 1000)


# run "show_positions" in a thread
t_show_positions = Thread(target=show_positions)
t_show_positions.start()

# open the window of the program
tools.basewindow.window.mainloop()
