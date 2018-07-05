import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import matplotlib as mtp
mtp.use("TkAgg")
import math
import json
import copy
import numpy as np
# position of antenna in the vicon coordinate system
antenna_positions = {
    "1.1": [-6.45, -2.67],
    "1.2": [-6.45, -7.76],
    "3.2": [13.34, -11.11],
    "6.2": [-2.61, 0.79],
    "6.1": [2.49, 0.79],
    "3.1": [8.46, -11.11],
    "2.2": [2.34, -11.11],
    "2.1": [-2.7, -11.11],
    "5.1": [13.46, 0.79],
    "5.2": [8.38, 0.79],
    "4.1": [20.45, -8.04],
    "4.2": [20.45, -2.42]
}
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



def calculate_relative_signal_strength(rssi):
    # -60 bis -100
    MIN_STRENGTH = -105
    MAX_STRENGTH = -60
    RANGE_STRENGTH = MAX_STRENGTH - MIN_STRENGTH
    return round((1./RANGE_STRENGTH)+((-MIN_STRENGTH + min(MAX_STRENGTH, max(MIN_STRENGTH,float(rssi))))/RANGE_STRENGTH),2)



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
        arrow_start_x = round(robo_x + (normalized_directions[key][0] * 0.3),3)
        arrow_start_y = round(robo_y + (normalized_directions[key][1] * 0.3),3)

        relative_strength = calculate_relative_signal_strength(antennas_strength[key])
        print key, str(relative_strength)
        arrow_end_x = round(arrow_start_x + (normalized_directions[key][0] * relative_strength),3)
        arrow_end_y = round(arrow_start_y + (normalized_directions[key][1] * relative_strength),3)
        points.append({"antenna":str(key),"start": {"x": arrow_start_x, "y": arrow_start_y},
                        "end": {"x": arrow_end_x, "y": arrow_end_y}})
        print key
        # print "start: ", points[key]["start"]
        # print "end:   ", points[key]["end"]
        print ('Robo X: ',robo_x, 'Robo Y: ',robo_y)
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
    client.publish("/sdr/signalStrengthIndicators", json.dumps({"data":points}), qos=2)
    # print(json.dumps())

# debugging for plot
# plt.figure('RSSI_Visualization')
# plt.plot((arrow_start_x, arrow_end_x),(arrow_start_y, arrow_end_y))
# plt.plot(robo_x,robo_y,'o')
# plt.show()
# debugging for plot

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
