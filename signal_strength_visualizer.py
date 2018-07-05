import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import math
import json
import copy
# position of antenna in the vicon coordinate system
antenna_positions = {
    "1.1": [-6.45, -18.37],
    "1.2": [-6.45, -18.37],
    "3.2": [13.34, 1.42],
    "6.2": [-2.61, -14.53],
    "6.1": [2.49, -9.43],
    "3.1": [8.46, -3.46],
    "2.2": [2.34, -9.58],
    "2.1": [-2.7, -14.62],
    "5.1": [13.46, 1.54],
    "5.2": [8.38, -3.54],
    "4.1": [20.45, 8.53],
    "4.2": [20.45, 8.53]
}
robo_x = 0.0
robo_y = 0.0
arrow_start_x = 3
arrow_start_y = 3
arrow_end_x = 7
arrow_end_y = 7
normalized_directions = {}
antennas_strength = {}



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

    client.subscribe("/signalStrengthPosition")

def on_message(client, userdata, msg):
    #print "on message"
    print(msg.topic+" "+str(msg.payload))
    if msg.topic == "/signalStrengthPosition":
        #print "got robot position"
        robo_x = round(json.loads(msg.payload)['x']/1000, 2)
        robo_y = round(json.loads(msg.payload)['y']/1000, 2)
        calculate_normalized_direction([robo_x, robo_y])
    else:
        antenna = msg.topic[13:16]
        antennas_strength[antenna] = round(float(msg.payload), 2)
    calculate_indicator_points()



def calculate_relative_signal_strength(rssi):
    # -60 bis -100
    return min(1.0, (-60 - min(-60, rssi))/30)


def calculate_indicator_points():
    # for each antenna
    # calculate starting point: robot point + vector * some radius offset
    # calculate end point: start point + vector * signal_strength
    # publish the start/end point pairs to laser system / visualization system
    points = {}
    for key in antennas_strength:
        # print('Key: ', key)
        if not key in normalized_directions.keys(): break
        arrow_start_x = round(robo_x + (normalized_directions[key][0] * 0.3),3)
        arrow_start_y = round(robo_y + (normalized_directions[key][1] * 0.3),3)

        relative_strength = calculate_relative_signal_strength(antennas_strength[key])
        arrow_end_x = round(arrow_start_x + (normalized_directions[key][0] * relative_strength),3)
        arrow_end_y = round(arrow_start_y + (normalized_directions[key][1] * relative_strength),3)
        points[key] = {"start": {"x": arrow_start_x, "y": arrow_start_y},
                        "end": {"x": arrow_end_x, "y": arrow_end_y}}
        print key
        print "start: ", points[key]["start"]
        print "end:   ", points[key]["end"]
        plt.figure('RSSI_Visualization')
        plt.plot((arrow_start_x, arrow_end_x),(arrow_start_y, arrow_end_y))
        plt.plot(robo_x,robo_y,'o')
        plt.show()
        publish_indicator([arrow_start_x, arrow_start_y],[arrow_end_x, arrow_end_y])
    publish_indicators(points)
    # print "-----"
    # print points
    # print "-----"

def publish_indicators(points):
    client.publish("/signalStrengthIndicators", json.dumps(points), qos=2)

# debugging for plot
plt.figure('RSSI_Visualization')
plt.plot((arrow_start_x, arrow_end_x),(arrow_start_y, arrow_end_y))
plt.plot(robo_x,robo_y,'o')
plt.show()
# debugging for plot

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
