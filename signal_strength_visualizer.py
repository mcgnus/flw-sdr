import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib as mtp
mtp.use("TkAgg")
import math
import json
import copy
import numpy as np
import subprocess
from collections import deque
from copy import deepcopy




# position of antenna in the vicon coordinate system
antenna_positions = {
    "1.1": [-11.7, 2.51],
    "1.2": [-11.7, -2.57],
    "2.1": [-7.83, -5.71],
    "2.2": [-2.99, -5.77],
    "3.1": [3.08, -5.89],
    "3.2": [8.13, -5.91],
    "4.1": [14.92, -2.81],
    "4.2": [15.05, 2.82],
    "5.1": [8.25, 6.02],
    "5.2": [3.80, 6.11],
    "6.1": [-2.93, 6.04],
    "6.2": [-7.82, 6.02]
}

counter = 0
counter_max = 1
robo_x = 0.0
robo_y = 0.0
# arrow_start_x = 3
# arrow_start_y = 3
# arrow_end_x = 7
# arrow_end_y = 7
normalized_directions = {}
antennas_strength = {}
antennas_state = {}
# HIST INIT
hist_length = 5
nAntennas = 6
strength_hist = deque()
for i in range(hist_length):
    strength_hist.append(0.0)

antennas_strength_hist = {
    "1.1": deepcopy(strength_hist),
    "1.2": deepcopy(strength_hist),
    "2.1": deepcopy(strength_hist),
    "2.2": deepcopy(strength_hist),
    "3.1": deepcopy(strength_hist),
    "3.2": deepcopy(strength_hist),
    "4.1": deepcopy(strength_hist),
    "4.2": deepcopy(strength_hist),
    "5.1": deepcopy(strength_hist),
    "5.2": deepcopy(strength_hist),
    "6.1": deepcopy(strength_hist),
    "6.2": deepcopy(strength_hist)
}

# DEQUE EXAMPLE
# >>> d['a'].append(3)
# >>> print(d)
# {'a': deque([0.0, 0.0, 0.0, 0.0, 0.0, 3])}
# >>> d['a'].popleft()
# 0.0
# >>> print(d)
# {'a': deque([0.0, 0.0, 0.0, 0.0, 3])}
# >>> d['a'].popleft()
# 0.0
# >>> print(d)
# {'a': deque([0.0, 0.0, 0.0, 3])}


# PLOT INIT
plt.ion()
# fig1 = mtp.figure.Figure('RSSI_Visualization')




def calculate_normalized_direction(robot_position):
    global normalized_directions
    _normalized_directions = {}
    for key in antenna_positions:
        antenna_x, antenna_y = antenna_positions[key]

        # calculate difference in each dimension
        direction = [antenna_x - robot_position[0], antenna_y - robot_position[1]]
        # calculate arc length
        length = math.sqrt(direction[0]**2 + direction[1]**2)
        # normalize vector
        direction[0] = round(direction[0] / length, 2)
        direction[1] = round(direction[1] / length, 2)

        _normalized_directions[key] = direction

    normalized_directions = copy.deepcopy(_normalized_directions)
    #print normalized_directions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    for ant in range(1,7):
        for sub in range(1,3):
            client.subscribe("/sdr/antenna_" + str(ant) + "." + str(sub) + "/rssi")

    client.subscribe("/sdr/signalStrengthPosition")

def on_message(client, userdata, msg):
    global robo_x, robo_y
    global counter, counter_max
    # global antennas_strength_hist
    #print "on message"
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "/sdr/signalStrengthPosition":
        # print "got robot position"
        robo_x = round(json.loads(msg.payload)['x']/1000, 2)
        robo_y = round(json.loads(msg.payload)['y']/1000, 2)
        # print('RX: ',robo_x,'RY: ',robo_y)
        calculate_normalized_direction([robo_x, robo_y])
    else:
        antenna = msg.topic[13:16]
        antennas_strength[antenna] = round(float(msg.payload), 2)
        antennas_strength_hist[antenna].popleft()
        antennas_strength_hist[antenna].append(round(float(msg.payload), 2))
        # print(msg.topic+" "+str(msg.payload))
    counter += 1
    if counter == counter_max:
        calculate_indicator_points()
        counter = 0



def calculate_relative_signal_strength(antenna, rssi):
    max_str = [-81.497267865, -63.1750439141, -82.0347329295, -63.1761792973, -81.4817976987, -63.2243993028]
    min_str = [-108.484741889, -108.24486421, -113.920822794, -109.096477399, -112.451717955, -109.54849841]

    # old:
    # max_str = [-61.497267865, -63.1750439141, -82.0347329295, -63.1761792973, -81.4817976987, -63.2243993028]
    # min_str = [-108.484741889, -108.24486421, -113.920822794, -109.096477399, -112.451717955, -109.54849841]

    MIN_STRENGTH = min_str[int(antenna[:1])-1]
    MAX_STRENGTH = max_str[int(antenna[:1])-1]
    RANGE_STRENGTH = MAX_STRENGTH - MIN_STRENGTH
    rel_signal_strength = round((1./RANGE_STRENGTH)+((-MIN_STRENGTH + min(MAX_STRENGTH, max(MIN_STRENGTH,float(rssi))))/RANGE_STRENGTH),2)

    # print("Range",RANGE_STRENGTH)
    # print(antenna, "Min rssi", MIN_STRENGTH)
    # print(antenna, "Max rssi", MAX_STRENGTH)
    # print("Vector Length", rel_signal_strength,"Current RSSI",rssi)

    return rel_signal_strength



def calculate_indicator_points():
    global robo_x,robo_y

    # for each antenna
    # calculate starting point: robot point + vector * some radius offset
    # calculate end point: start point + vector * signal_strength
    # publish the start/end point pairs to laser system / visualization system
    points = []
    for key in antennas_strength:
        # print('Key: ', key)
        if not key in normalized_directions.keys(): break
        arrow_start_x = round((normalized_directions[key][0] * 0.4),3)
        arrow_start_y = round((normalized_directions[key][1] * 0.4),3)
        #arrow_start_x = round(robo_x + (normalized_directions[key][0] * 0.3),3) +0.1
        #arrow_start_y = round(robo_y + (normalized_directions[key][1] * 0.3),3) - 0.5

        relative_strength = calculate_relative_signal_strength(key, antennas_strength[key])
        #print key, str(relative_strength)
        arrow_end_x = round(arrow_start_x + (normalized_directions[key][0] * relative_strength),3)
        arrow_end_y = round(arrow_start_y + (normalized_directions[key][1] * relative_strength),3)

        # CHECK whether the antenna values are still incoming
        if len(set(list(antennas_strength_hist[key]))) == 1:
            antennas_state[key] = 'no_connection'
        else:
            antennas_state[key] = 'running'
        points.append({"antenna":str(key),"antenna_id":int(key[:1]),"antenna_state":antennas_state[key],"start": {"x": arrow_start_x, "y": arrow_start_y},
                        "end": {"x": arrow_end_x, "y": arrow_end_y}})
        # print points
        #print key
        # print "start: ", points[key]["start"]
        # print "end:   ", points[key]["end"]
        #print ('Robo X: ',robo_x, 'Robo Y: ',robo_y)
        # plot_visualization(robo_x,robo_y)
        # print(points)
        # publish_indicator([arrow_start_x, arrow_start_y],[arrow_end_x, arrow_end_y])
    publish_indicators(points)
    # print "-----"
    # print points
    # print "-----"
def plot_visualization(robo_pos_x, robo_pos_y):
    # global fig1

    ax = fig1.add_subplot(111)
    # ax.set_xlim(-8,8)
    # ax.set_ylim(-5,5)
    line1, = ax.plot(robo_pos_x, robo_pos_y, 'or')
    line1.set_ydata(robo_pos_y)
    line1.set_xdata(robo_pos_x)

    fig1.canvas.draw()
    # plt.close(fig1)

def publish_indicators(points):

    print "sending"
    # print points
    client.publish("/sdr/signalStrengthIndicators", json.dumps({"data":points, "robot_position": {"x": robo_x, "y": robo_y}}), qos=2)
    print({"data":points, "robot_position": {"x": robo_x, "y": robo_y}})

def rssi_statistics():
    print "blubb"

    # p = subprocess.Popen(['python', 'script.py', 'arg1', 'arg2'])
    # # continue with your code then terminate the child
    # p.terminate()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
