import paho.mqtt.client as mqtt
import sys

maxs = [-120] * 6
mins = [0] * 6

def on_connect(client, userdata, flags, rc):
    #client.subscribe("/sdr/signalStrengthIndicators")
    #for x in range(7):

    client.subscribe("/sdr/antenna_" + sys.argv[1] + ".1/rssi")
    

def on_message(client, userdata, msg):
    #global maxs
    #global mins
    #maxs[int(msg.topic[13:14])-1] = max( maxs[int(msg.topic[13:14])-1], float(msg.payload))
    #mins[int(msg.topic[13:14])-1] = min( mins[int(msg.topic[13:14])-1], float(msg.payload))
    print(str(msg.payload))
    #print maxs
    #print mins


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("gopher.phynetlab.com", 8883, 60)
client.loop_forever()
