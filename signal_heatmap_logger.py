import paho.mqtt.client as mqtt
import math
import json
import copy
import numpy as np

robo_x = 0.0
robo_y = 0.0

antennas_strength = {
    "1.1": 0.0,
    "1.2": 0.0,
    "2.1": 0.0,
    "2.2": 0.0,
    "3.1": 0.0,
    "3.2": 0.0,
    "4.1": 0.0,
    "4.2": 0.0,
    "5.1": 0.0,
    "5.2": 0.0,
    "6.1": 0.0,
    "6.2": 0.0
}

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for ant in range(1,7):
        for sub in range(1,3):
            client.subscribe("/sdr/antenna_" + str(ant) + "." + str(sub) + "/rssi")
    client.subscribe("/sdr/signalStrengthPosition")

def on_message(client, userdata, msg):
    global robo_x, robo_y, antennas_strength
    if msg.topic == "/sdr/signalStrengthPosition":
        robo_x = round(json.loads(msg.payload)['x']/1000, 2)
        robo_y = round(json.loads(msg.payload)['y']/1000, 2)
        client.publish("/sdr/heatmap_data", json.dumps({
            "robot_position": {"x": robo_x, "y": robo_y},
            "antennas_strength": antennas_strength }), qos=2)
    else:
        antennas_strength[antenna] = round(float(msg.payload), 2)


# register callbacks and connect to server
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
