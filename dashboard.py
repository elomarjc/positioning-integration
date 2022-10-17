# Program for Positioning Integration of UWB, CV, Robot and InfluxDB
# This program takes input from UWB tags, CV tags, Robots and sends then onto InfluxDB database and Plots their positions on two maps
# In this program, we have defined 7 threads for multiple processes running simultaneously:
# Thread 1. window.mainloop(): Main thread, opens a window to show the maps, the titles, and logos;
# Thread 2. t_cv: Processes the data from CV (receive data, draw the position on the map, save the data into the influxDB);
# Thread 3. t_tag: Processes the data from UWB (receive data, draw the position on the map, save the data into the influxDB);
# Thread 4. t_robot: Processes the data from Robot (receive data, draw the position on the map, save the data into the influxDB);
# Thread 5. t_delete_cv: One thread does some cleaning work about CV;
# Thread 6. t_delete_tags: One thread does some cleaning work about UWB.
# Thread 7. t_ffplay: Open the window of video from camera using ffplay
# Thread 8. t_resize: check the size of the window, and resize the map
# Thread 9. t_clean_limit_influxdb: clean old records for the limitation of influxDB writing rate, avoiding too many records
import paho.mqtt.client as mqtt  # Paho is a Python library to get data from CV and UWB using MQTT protocol (MAC NEED THIS LIB)
import json  # json is data format to be used for differnt objects (javascript object notation)
from threading import Thread
from threading import Lock
from threading import Timer # Jacob is cool

from PIL import ImageTk  # put a picture (lab map) in the window   (MAC NEED PILLOW LIB.)
import tkinter  # Python GUI tool, to open a window
import tkinter.font  # to change the font size of titles
import tools.adjustable_text_size
import tools.map

import robot.robot_api  # use API to get data from Robot
import robot.controller
import robot.monitor
import tools.tools
import tools.basewindow
import tools.influxdb_tools
import tools.alarm
import tools.right_bottom

import time  # to record the time that we receive data from CV, UWB and Robot
import datetime
import rfc3339
import pytz # MAC NEED THIS LIB

import os  # to use ffplay command of linux operating system

# we need to write the positions into influxdb, the influxdb related code is according to https://docs.influxdata.com/influxdb/v2.3/api-guide/client-libraries/python/
import influxdb_client # MAC NEED THIS LIB
from influxdb_client.domain.write_precision import WritePrecision
import influxdb_client.client.write_api

person_icon_photo = ImageTk.PhotoImage(tools.map.new_person_icon)
uwbtag_icon_photo = ImageTk.PhotoImage(tools.map.new_uwbtag_icon)
robot_icon_photo = ImageTk.PhotoImage(tools.map.new_robot_icon)

# this variable is a dict, key of the dict is UWBtagID, value of the dict is the (x,y) position and the time that we receive the (x,y) position from UWB system.
tags_lock = Lock()
tags = dict()

# for cleaning old dots on the map
cids_lock = Lock()
cids = dict()

# record all robots
robot_id_records_lock = Lock()
robot_id_records = dict()

# To generate alarms when an object is too close to an robot
r_alarms = tools.alarm.robot_alarms(tools.basewindow.control_panel, cids,
                                    cids_lock, tags, tags_lock,
                                    robot_id_records, robot_id_records_lock)

# To control robots
robot_control = robot.controller.robot_controller(
    tools.basewindow.right_control_panel, robot_id_records,
    robot_id_records_lock, tools.basewindow.canvas_map)

# To show the information of robots
robot_monit = robot.monitor.robot_monitor(tools.basewindow.control_panel,
                                          tools.basewindow.right_control_panel,
                                          robot_id_records,
                                          robot_id_records_lock)

# right bottom corner
right_bottom = tools.right_bottom.right_bottom_corner(
    tools.basewindow.right_control_panel)


# resize the map photo according to the size of the window
def resize():
    tools.basewindow.resize_basewindow()

    # create legends
    tools.basewindow.canvas_map.delete("legend")
    if right_bottom.text_on.get():
        tools.basewindow.create_unit_legend(tools.basewindow.canvas_map)

    # try resize every 1s
    t_resize = Timer(1, resize)
    t_resize.start()


resize()

# variables to limit infuxdb writing rate
limit_influxdb = tools.tools.last_influxDB_records()
limit_influxdb_lock = Lock()
# max data writing rates, unit: Hz
max_cv_rate = 25
max_uwb_rate = 20
max_robot_rate = 10
# min data writing intervals, unit: millisecond
min_cv_interval = 1 / (float(max_cv_rate)) * 1000
min_uwb_interval = 1 / (float(max_uwb_rate)) * 1000
min_robot_interval = 1 / (float(max_robot_rate)) * 1000

# some configuration that we use to access the CV and UWB system to get position data
host = "192.168.100.153"
port = 1883
topic_cv = "cv"
topic_tags = "tags"


# a function to connect to the CV system through paho.mqtt
def on_connect_cv(client, userdata, flags, rc):
    print(mqtt.connack_string(rc))


# a function to receive message from the CV system through paho.mqtt
def on_message_cv(client, userdata, msg):
    try:
        string_from_mqtt_stream = msg.payload.decode()
        json_object_from_mqtt = json.loads(string_from_mqtt_stream)
        success_from_json = json_object_from_mqtt[0]["success"]
        cid = json_object_from_mqtt[0][
            "tagId"]  # get the id assigned by camera
        if (success_from_json):
            process_cv_data(json_object_from_mqtt, cid)
    except Exception as e:
        print("on_message_cv, error:\n" + e)


# process the data from CV according to cid
def process_cv_data(json_object_from_mqtt, cid):
    coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]

    # print log with time
    time_log = datetime.datetime.now(tz=pytz.timezone("CET"))
    time_log_str = rfc3339.format_microsecond(time_log,
                                              utc=False,
                                              use_system_timezone=False)

    print('[{}] Coordinates from CV ID: {} {{'.format(time_log_str, cid), "x:",
          coordinates_from_json["x"], "y:", coordinates_from_json["y"], "}")

    # write data into influxdb
    t_ns = time.time_ns()  # use ns as the unit to write the time in influxdb
    # use unified coordinates to write influxdb
    influxdb_x, influxdb_y = tools.map.convert_cv_position_for_unification(
        float(coordinates_from_json["x"]), float(coordinates_from_json["y"]))
    limit_influxdb_lock.acquire()
    global limit_influxdb
    this_record = tools.tools.coor(influxdb_x, influxdb_y, time_log)
    # judge whether we should write this record
    write_influxdb = False
    if str(cid) not in limit_influxdb.cv:
        write_influxdb = True  # if last record does not exist, write this one
        limit_influxdb.cv[str(cid)] = this_record  # update the last record
        print(
            '[{}] [Time interval from last write: larger than {}ms] Write influxDB CV ID: {} {{'
            .format(time_log_str, min_cv_interval,
                    cid), "x:", influxdb_x, "y:", influxdb_y, "}")
    else:
        last_record = limit_influxdb.cv[str(cid)]
        time_diff = this_record.t - last_record.t
        time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
        if time_diff_ms > min_cv_interval and (this_record.x != last_record.x
                                               or
                                               this_record.y != last_record.y):
            # if time interval is larger than the minimum interval, and the position changes, write this one
            write_influxdb = True
            limit_influxdb.cv[str(cid)] = this_record  # update the last record
            print(
                '[{}] [Time interval from last write: {}ms] Write influxDB CV ID: {} {{'
                .format(time_log_str, time_diff_ms,
                        cid), "x:", influxdb_x, "y:", influxdb_y, "}")
    limit_influxdb_lock.release()
    if write_influxdb:
        # creat a point of influxdb, a point is a data item.
        # measurement: "cv", tag: "cvid"=<id assigned by camera>, field1: x=<x>, field2: y=<y>, time: now
        inf_point = influxdb_client.Point("cv").tag("cvid", str(cid)).field(
            "x", influxdb_x).field("y", influxdb_y).time(
                t_ns, write_precision=WritePrecision.NS)
        # write data and process the excepthon when error
        try:
            tools.influxdb_tools.inf_write_api.write(
                bucket=tools.influxdb_tools.bucket,
                org=tools.influxdb_tools.org,
                record=inf_point)
        except Exception as e:
            print("Write influxdb error:\n", e)

    # draw the dot on the map
    canvas_tag = tools.tools.cv_canvas_tag(cid)
    canvas_text = tools.tools.cv_canvas_text(cid)

    # record them, for cleaning old dots on the map
    t = time.localtime()
    coordinate = tools.tools.coor(influxdb_x, influxdb_y, t, canvas_text)
    cids_lock.acquire()
    global cids
    cids[canvas_tag] = coordinate
    cids_lock.release()

    # delete the old CV point on the map, and draw the newest point
    tools.basewindow.canvas_map.delete(canvas_tag)

    # draw the person on the map
    tools.map.show_position_icon(tools.basewindow.canvas_map,
                                 tools.basewindow.proportion,
                                 coordinates_from_json["x"],
                                 coordinates_from_json["y"],
                                 canvas_tag,
                                 person_icon_photo,
                                 "{}".format(canvas_text),
                                 tools.map.convert_cv,
                                 tools.map.convert_cv_position_for_unification,
                                 print_text=right_bottom.text_on.get())

    # refresh the alarm
    if write_influxdb:
        r_alarms.refresh_alarm()


# a function that we need in paho.mqtt
def on_subscribe_cv(client, userdata, mid, granted_qos):
    print("Subscribed to topic Computer Vision (cv)!\n")


# a function to run the paho.mqtt for CV, to read data from CV and process
def run_cv():
    client = mqtt.Client()

    # set callbacks
    client.on_connect = on_connect_cv
    client.on_message = on_message_cv
    client.on_subscribe = on_subscribe_cv
    client.connect(host, port=port)
    client.subscribe(topic_cv)
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        pass
    client.disconnect()
    client.loop_stop()
    print("disconnected")


# run the thread to process data from CV.
t_cv = Thread(target=run_cv)
t_cv.start()


# a function that we need in paho.mqtt
def on_connect_tags(client, userdata, flags, rc):  # defining the functions
    print(mqtt.connack_string(rc))


# the function to get data from UWB system through paho.mqtt, and process it
def on_message_tags(client, userdata, msg):  # defining the functions
    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    success_from_json = json_object_from_mqtt[0]["success"]
    tag_id_from_json = json_object_from_mqtt[0]["tagId"]
    if (success_from_json):
        coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]

        # print log with time
        time_log = datetime.datetime.now(tz=pytz.timezone("CET"))
        time_log_str = rfc3339.format_microsecond(time_log,
                                                  utc=False,
                                                  use_system_timezone=False)

        print("[{}] Coordinates from UWB tag id:".format(time_log_str),
              tag_id_from_json, coordinates_from_json)
        t = time.localtime()

        # write data into influxdb
        t_ns = time.time_ns(
        )  # use ns as the unit to write the time in influxdb

        # use unified coordinates to write influxdb
        influxdb_x, influxdb_y = tools.map.convert_uwb_position_for_unification(
            float(coordinates_from_json["x"]),
            float(coordinates_from_json["y"]))
        limit_influxdb_lock.acquire()
        global limit_influxdb
        this_record = tools.tools.coor(influxdb_x, influxdb_y, time_log)
        # judge whether we should write this record
        write_influxdb = False
        if str(tag_id_from_json) not in limit_influxdb.uwb:
            write_influxdb = True  # if last record does not exist, write this one
            limit_influxdb.uwb[str(
                tag_id_from_json)] = this_record  # update the last record
            print(
                '[{}] [Time interval from last write: larger than {}ms] Write influxDB UWB ID: {} {{'
                .format(time_log_str, min_uwb_interval, tag_id_from_json),
                "x:", influxdb_x, "y:", influxdb_y, "}")
        else:
            last_record = limit_influxdb.uwb[str(tag_id_from_json)]
            time_diff = this_record.t - last_record.t
            time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
            if time_diff_ms > min_uwb_interval and (
                    this_record.x != last_record.x
                    or this_record.y != last_record.y):
                # if time interval is larger than the minimum interval, and the position changes, write this one
                write_influxdb = True
                limit_influxdb.uwb[str(
                    tag_id_from_json)] = this_record  # update the last record
                print(
                    '[{}] [Time interval from last write: {}ms] Write influxDB UWB ID: {} {{'
                    .format(time_log_str, time_diff_ms, tag_id_from_json),
                    "x:", influxdb_x, "y:", influxdb_y, "}")
        limit_influxdb_lock.release()
        if write_influxdb:
            # creat a point of influxdb, a point is a data item.
            # measurement: "uwb", tag: "uwbtagid"=<uwb tag id>, field1: x=<x>, field2: y=<y>, time: now
            inf_point = influxdb_client.Point("uwb").tag(
                "uwbtagid",
                str(tag_id_from_json)).field("x", influxdb_x).field(
                    "y", influxdb_y).time(t_ns,
                                          write_precision=WritePrecision.NS)

            # write data and process the excepthon when error
            try:
                tools.influxdb_tools.inf_write_api.write(
                    bucket=tools.influxdb_tools.bucket,
                    org=tools.influxdb_tools.org,
                    record=inf_point)
            except Exception as e:
                print("Write influxdb error:\n", e)

        # use UWBtagID to sign the points and text that we draw in the map
        canvas_tag = tools.tools.uwb_canvas_tag(tag_id_from_json)
        canvas_text = tools.tools.uwb_canvas_text(tag_id_from_json)

        # combine the x, y, and time into one variable
        coordinate = tools.tools.coor(influxdb_x, influxdb_y, t, canvas_text)
        # to change the value of a global value, we need to use the keyword "global" to claim that
        global tags
        # record the x,y and time of this UWBtag
        tags_lock.acquire()
        tags[canvas_tag] = coordinate
        tags_lock.release()

        # delete the old point and text on the map of this UWBtag
        tools.basewindow.canvas_map.delete(canvas_tag)

        # draw the uwbtag on the map
        tools.map.show_position_icon(
            tools.basewindow.canvas_map,
            tools.basewindow.proportion,
            coordinates_from_json["x"],
            coordinates_from_json["y"],
            canvas_tag,
            uwbtag_icon_photo,
            "{}".format(canvas_text),
            tools.map.convert_tags,
            tools.map.convert_uwb_position_for_unification,
            0,
            20,
            print_text=right_bottom.text_on.get())
        # refresh the alarm
        if write_influxdb:
            r_alarms.refresh_alarm()

    else:
        print("Unsuccesful positioning from UWB tags.............")


# a function that we need in paho.mqtt
def on_subscribe_tags(client, userdata, mid,
                      granted_qos):  # defining the functions
    print("Subscribed to topic Pozyx tags\n")


# a function to run the paho.mqtt for UWB, to read data from UWB and process
def run_tag():
    client = mqtt.Client()
    client.on_connect = on_connect_tags  # set callbacks
    client.on_message = on_message_tags
    client.on_subscribe = on_subscribe_tags
    client.connect(host, port=port)
    client.subscribe(topic_tags)
    try:  # Here we are making a loop to run above program forever untill there is a KBD intrrupt occurs
        client.loop_forever()
    except KeyboardInterrupt:
        pass
    client.disconnect()
    client.loop_stop()
    print("disconnected")


# run the thread to process data from UWB.
t_tag = Thread(target=run_tag)
t_tag.start()


# get position from robot and plot them on the map, and write them into influxdb
def process_robot_data(
        canvas: tkinter.Canvas,
        influxdb_write_api: influxdb_client.client.write_api.WriteApi):
    while True:  # execute every 1 second
        # use API to get the IDs of all robots in the fleet-manager
        robot_ids = []
        try:
            robots = robot.robot_api.get_robots()
            for one_robot in robots:
                robot_ids.append(str(one_robot["id"]))
        except Exception as e:
            print(e)

        # filter available robots
        available_robot_ids = dict()
        try:
            for robot_id in robot_ids:
                # use API to get robot information
                robot_info = robot.robot_api.get_robot_info(robot_id)
                # jump the unavailable robots
                # it seems that when "fleet_state_text" is "unavailable", "fleet_state" is 1
                if robot_info["fleet_state"] != 1:
                    available_robot_ids[robot_id] = robot_info
        except Exception as e:
            print(e)

        # Add the a Robots not connected to the fleet-manager
        for robot_id in tools.tools.extra_robots_conf.keys():
            robot_info = tools.tools.extra_robots_conf[robot_id]
            status_direct, status_code = robot.robot_api.robot_status_with_code(
                robot_info['ip'])
            # If the robot API can be accessed, we consider it existing
            if robot.robot_api.resp_code_successful(status_code):
                available_robot_ids[robot_id] = robot_info

        r_alarms.alarm_lock.acquire(
        )  # do not refresh alarm when the "robot_id_records" is in transient states

        # clear the non-existing robots on the map and the records
        need_to_delete = []
        robot_id_records_lock.acquire()
        for key in robot_id_records.keys():
            if tools.tools.robot_canvas_tag_to_id(
                    key) not in available_robot_ids.keys():
                print("Robot {} disappears.".format(key))
                canvas.delete(key)
                need_to_delete.append(key)
        for key in need_to_delete:
            del robot_id_records[key]
        robot_id_records_lock.release()

        need_refresh_alarm = False

        # get the detailed information of all robots
        for robot_id in available_robot_ids.keys():
            try:
                # get robot information
                robot_info = available_robot_ids[robot_id]
                robot_ip = robot_info['ip']
                # status = robot_info['status']
                # position = status['position']
                # directly use robot api instead of fleet-manager api to get the positions, because the refresh rate is higher
                status_direct = robot.robot_api.robot_status_direct(robot_ip)
                position_direct = status_direct['position']

                # print log with time
                time_log = datetime.datetime.now(tz=pytz.timezone("CET"))
                time_log_str = rfc3339.format_microsecond(
                    time_log, utc=False, use_system_timezone=False)

                print(
                    "[{}] Coordinates from Robot ID: {}, IP: {} ".format(
                        time_log_str, robot_id, robot_ip),
                    "{{ x: {}, y: {} }}".format(position_direct["x"],
                                                position_direct["y"]))

                # write data into influxdb
                t_ns = time.time_ns(
                )  # use ns as the unit to write the time in influxdb

                # use unified coordinates to write influxdb
                influxdb_x, influxdb_y = tools.map.convert_robot_position_for_unification(
                    float(position_direct["x"]), float(position_direct["y"]))
                limit_influxdb_lock.acquire()
                global limit_influxdb
                this_record = tools.tools.coor(influxdb_x, influxdb_y,
                                               time_log)
                # judge whether we should write this record
                write_influxdb = False
                if str(robot_id) not in limit_influxdb.robot:
                    write_influxdb = True  # if last record does not exist, write this one
                    limit_influxdb.robot[str(
                        robot_id)] = this_record  # update the last record
                    print(
                        '[{}] [Time interval from last write: larger than {}ms] Write influxDB Robot ID: {}, IP: {} {{'
                        .format(time_log_str, min_robot_interval, robot_id,
                                robot_ip), "x:", influxdb_x, "y:", influxdb_y,
                        "}")
                else:
                    last_record = limit_influxdb.robot[str(robot_id)]
                    time_diff = this_record.t - last_record.t
                    time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
                    if this_record.x != last_record.x or this_record.y != last_record.y:
                        # if time interval is larger than the minimum interval, and the position changes, write this one
                        write_influxdb = True
                        limit_influxdb.robot[str(
                            robot_id)] = this_record  # update the last record
                        print(
                            '[{}] [Time interval from last write: {}ms] Write influxDB Robot ID: {}, IP: {} {{'
                            .format(time_log_str, time_diff_ms, robot_id,
                                    robot_ip), "x:", influxdb_x, "y:",
                            influxdb_y, "}")
                limit_influxdb_lock.release()
                if write_influxdb:
                    # creat a point of influxdb, a point is a data item.
                    # measurement: "robot", tag: "robotid"=<robot id>, field1: x=<x>, field2: y=<y>, time: now
                    inf_point = influxdb_client.Point("robot").tag(
                        "robotid", str(robot_id)).field("x", influxdb_x).field(
                            "y",
                            influxdb_y).time(t_ns,
                                             write_precision=WritePrecision.NS)
                    # write data and process the excepthon when error
                    try:
                        influxdb_write_api.write(
                            bucket=tools.influxdb_tools.bucket,
                            org=tools.influxdb_tools.org,
                            record=inf_point)
                    except Exception as e:
                        print("Write influxdb error:\n", e)

                # record this robot
                t = time.localtime()
                canvas_tag = tools.tools.robot_canvas_tag(robot_id)
                canvas_text = tools.tools.robot_canvas_text(robot_id)
                # combine the x, y, and time into one variable
                coordinate = tools.tools.coor(
                    influxdb_x, influxdb_y, t, canvas_text, robot_ip,
                    str(status_direct['velocity']['linear']))
                robot_id_records_lock.acquire()
                robot_id_records[canvas_tag] = coordinate
                robot_id_records_lock.release()

                canvas.delete(
                    canvas_tag)  # before ploting, delete the old dots
                tools.map.show_position_icon(
                    tools.basewindow.canvas_map,
                    tools.basewindow.proportion,
                    position_direct["x"],
                    position_direct["y"],
                    canvas_tag,
                    robot_icon_photo,
                    canvas_text,
                    tools.map.convert_robot,
                    tools.map.convert_robot_position_for_unification,
                    print_text=right_bottom.text_on.get())

                # draw the alarm areas
                if r_alarms.area_on.get():
                    r_alarms.show_areas(tools.basewindow.canvas_map,
                                        tools.basewindow.proportion,
                                        position_direct["x"],
                                        position_direct["y"], canvas_tag)

                # when any robot needs to write influxDB, we refresh the alarm
                need_refresh_alarm = need_refresh_alarm or write_influxdb
            except Exception as e:
                print(
                    "Get position form Robot ID {}, error: ".format(robot_id),
                    e)
        r_alarms.alarm_lock.release()
        # refresh robot velocity display
        robot_monit.refresh_linear_velocity()
        # refresh the robot_ids stored in the robot_control
        robot_control.update_id_option(available_robot_ids.keys())
        # refresh the alarm
        if need_refresh_alarm:
            r_alarms.refresh_alarm()
        time.sleep(min_robot_interval / 1000)


# run the thread to process data from robot.
t_robot = Thread(target=process_robot_data,
                 args=(tools.basewindow.canvas_map,
                       tools.influxdb_tools.inf_write_api))
t_robot.start()


# For cleaning the map every 1 seconds, we delete the CV old points on the map
def delete_cv():
    while True:
        time.sleep(1)
        t = time.localtime()
        need_to_delete = []
        cids_lock.acquire()
        for key in cids:
            if int(time.mktime(t) - time.mktime(cids[key].t)) > 1:
                tools.basewindow.canvas_map.delete(key)
                need_to_delete.append(key)
        for key in need_to_delete:
            del cids[key]
        cids_lock.release()
        # refresh the alarm
        if len(need_to_delete) != 0:
            r_alarms.refresh_alarm()


# run "delete_cv" in a thread
t_delete_cv = Thread(target=delete_cv)
t_delete_cv.start()


# if we does not receive the signal of one UWBtag for 5 seconds, we delete its point on the map
def delete_tags():
    while True:
        time.sleep(5)
        t = time.localtime()
        need_to_delete = []
        tags_lock.acquire()
        for key in tags:
            if int(time.mktime(t) - time.mktime(tags[key].t)) > 5:
                tools.basewindow.canvas_map.delete(key)
                need_to_delete.append(key)
        for key in need_to_delete:
            del tags[key]
        tags_lock.release()
        # refresh the alarm
        if len(need_to_delete) != 0:
            r_alarms.refresh_alarm()


# run "delete_tags" in a thread
t_delete_tags = Thread(target=delete_tags)
t_delete_tags.start()


# clean old records for the limitation of influxDB writing rate, avoiding too many records
def clean_limit_influxdb():
    t = datetime.datetime.now(tz=pytz.timezone("CET"))
    # clean the records before min time interval
    limit_influxdb_lock.acquire()
    global limit_influxdb
    # clean cv records
    need_clean_ids = []
    for id in limit_influxdb.cv.keys():
        time_diff = t - limit_influxdb.cv[id].t
        time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
        if time_diff_ms > min_cv_interval:
            need_clean_ids.append(id)
    print("<clean_limit_influxdb> Clean CV IDs: ", need_clean_ids)
    for id in need_clean_ids:
        del limit_influxdb.cv[id]
    # clean uwb records
    need_clean_ids = []
    for id in limit_influxdb.uwb.keys():
        time_diff = t - limit_influxdb.uwb[id].t
        time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
        if time_diff_ms > min_uwb_interval:
            need_clean_ids.append(id)
    print("<clean_limit_influxdb> Clean UWB IDs: ", need_clean_ids)
    for id in need_clean_ids:
        del limit_influxdb.uwb[id]
    # clean robot records
    need_clean_ids = []
    for id in limit_influxdb.robot.keys():
        time_diff = t - limit_influxdb.robot[id].t
        time_diff_ms = time_diff.seconds * 1000 + time_diff.microseconds / 1000
        if time_diff_ms > min_robot_interval:
            need_clean_ids.append(id)
    print("<clean_limit_influxdb> Clean Robot IDs: ", need_clean_ids)
    for id in need_clean_ids:
        del limit_influxdb.robot[id]

    limit_influxdb_lock.release()

    # try clean every 180s
    t_clean_limit_influxdb = Timer(180, clean_limit_influxdb)
    t_clean_limit_influxdb.start()


clean_limit_influxdb()

# open the window of video from camera
t_ffplay = Thread(
    target=os.system,
    args=
    ('ffplay -window_title "Real-time Camera View" -x 600 -y 350 rtsp://AAU:Fibiger14@192.168.1.102:554 -nostats -loglevel 0',
     ))
t_ffplay.start()

# open the window of the program
tools.basewindow.window.mainloop()
