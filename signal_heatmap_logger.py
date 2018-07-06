import paho.mqtt.client as mqtt
import math
import json
import copy
import numpy as np

robo_x = 0.0
robo_y = 0.0
# arrow_start_x = 3
# arrow_start_y = 3
# arrow_end_x = 7
# arrow_end_y = 7
normalized_directions = {}
antennas_strength = {}

plt.ion()
# fig1 = mtp.figure.Figure('RSSI_Visualization')

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for ant in range(1,7):
        for sub in range(1,3):
            client.subscribe("/sdr/antenna_" + str(ant) + "." + str(sub) + "/rssi")
    client.subscribe("/sdr/signalStrengthPosition")

def on_message(client, userdata, msg):
    global robo_x, robo_y
    #print "on message"
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "/sdr/signalStrengthPosition":
        #print "got robot position"
        robo_x = round(json.loads(msg.payload)['x']/1000, 2)
        robo_y = round(json.loads(msg.payload)['y']/1000, 2)
        # print('RX: ',robo_x,'RY: ',robo_y)
        calculate_normalized_direction([robo_x, robo_y])
    else:
        antenna = msg.topic[13:16]
        antennas_strength[antenna] = round(float(msg.payload), 2)
    calculate_indicator_points()




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
