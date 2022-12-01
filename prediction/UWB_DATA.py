from threading import Thread
import robotHumanClass
import json
import tools.map
import paho.mqtt.client as mqtt
import csv
import time


firstTime = time.time()
host = "192.168.100.153"  # Broker (Server) IP Address
port = 1883
topic = "tags"  # Defining a Topic on server
def on_message_tags(client, userdata, msg):  # defining the functions, humannumber added 

    string_from_mqtt_stream = msg.payload.decode()
    json_object_from_mqtt = json.loads(string_from_mqtt_stream)
    success_from_json = json_object_from_mqtt[0]["success"]
    tag_id_from_json = json_object_from_mqtt[0]["tagId"]
    if (success_from_json):
        coordinates_from_json = json_object_from_mqtt[0]["data"]["coordinates"]

       # print("[{}] Coordinates from UWB tag id:".format(time_log_str),
        #      tag_id_from_json, coordinates_from_json)
        # write data into influxdb
        # use unified coordinates to write influxdb
        influxdb_x, influxdb_y = tools.map.convert_uwb_position_for_unification(
            float(coordinates_from_json["x"]),
            float(coordinates_from_json["y"]))
       # print(str(influxdb_x), str(influxdb_y),str(tag_id_from_json))

        if (str(tag_id_from_json) == "5329"): 
           # human1.xPath.append(influxdb_x) #human1 honek bariable moduan izan biadia
           # human1.yPath.append(influxdb_y)
            human1.xPath.append(influxdb_x) #human1 honek bariable moduan izan biadia
            human1.yPath.append(influxdb_y)
            human1.xPredictions.append(time.time()-firstTime)
            print(human1.xPath)
            print(human1.xPredictions)
            
            
            if (time.time()-firstTime > 10):
                notHere = False
                stopThread()
                time.sleep(50)



    #time.sleep(1/4)
def on_connect(client, userdata, flags, rc):  # defining the functions
    print(mqtt.connack_string(rc))
    pass
def on_subscribe(client, userdata, mid, granted_qos):  # defining the functions
    print("Subscribed to topic")

def run_tag():
    client = mqtt.Client()
    client.on_connect = on_connect  # set callbacks
    client.on_message = on_message_tags
    client.on_subscribe = on_subscribe
    client.connect(host, port=port)
    client.subscribe(topic)
    try:  # Here we are making a loop to run above program forever untill there is a KBD intrrupt occurs
        client.loop_forever()
    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()
        print("disconnected")

human1=robotHumanClass.human("5329")

def stopThread():
    fields = ["xPosition", "yPosition", "TimeStamp"]
    rows = []
    index = 0
    while index <= len(human1.xPath)-1:
        newRow = [human1.xPath[index], human1.yPath[index], human1.xPredictions[index]]
        rows.append(newRow)
        index = index+1

    with open("C:\Maila_4\Project\OurGitRepo/ForwardNBack3WithTime.csv", "w+") as f:
        write = csv.writer(f)
        write.writerow(fields)
        write.writerows(rows)
    print("DONE!")

t_tag = Thread(target=run_tag)
t_tag.start()