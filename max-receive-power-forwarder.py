#!/usr/bin/python3

UPDATE_RATE_HZ_MQTT = 1 # desired update rate via mqtt

SAMPLE_RATE_HZ_SDR = .25e6 # sample rate of the SDRs = bandwidth
CENTER_FREQUENCY_SDR = 433e6
GAIN = 0 # configured gain in the sdrs in dB

FFTLENGTH = 1024 # fft-length that is used by max_receive_power
KEEP_ONE_IN_N = 50

# Calculate a few more constants which can be derived from the configuration
NUM_SAMPLES_PER_UPDATE = SAMPLE_RATE_HZ_SDR / FFTLENGTH / KEEP_ONE_IN_N / UPDATE_RATE_HZ_MQTT
FFT_DELTA_F = SAMPLE_RATE_HZ_SDR / FFTLENGTH


import zmq
import bitstring

import paho.mqtt.client as mqtt

import numpy as np
import pandas as pd
import time

# Set up zero-mq context and connect sockets
zmqContext = zmq.Context()
zmqsockets = []
for i in range(6):
    zmqsockets.append( zmqContext.socket(zmq.SUB) )

for i in range(6):
    zmqsockets[i].connect("tcp://localhost:444"+str(i+1))
    # Very important: subscribe for everything!
    zmqsockets[i].setsockopt_string(zmq.SUBSCRIBE, "")

# Set up mqtt
mqttClient = mqtt.Client()
mqttClient.connect("gopher.phynetlab.com", 8883, 60)

"""
# If we have more zmq-updates available than we want to publish via mqtt, we can collect those first and calculate a mean
zmqindexlists = []
zmqvaluelists = []
for i in range(6):
    zmqindexlists.append([])
    zmqvaluelists.append([])
"""

statistic = []
for i in range(6):
    statistic.append(0)

def getFrequencyFromIndex(index):
    frequency = CENTER_FREQUENCY_SDR + index * FFT_DELTA_F
    if index > FFTLENGTH / 2:  # fft-overflow, indexes > N/2 correspond to frequencies below f_0
        frequency -= SAMPLE_RATE_HZ_SDR
    return frequency

def getPowerDbFromValue(value):
    power = (value / FFTLENGTH) ** 2
    power -= GAIN
    powerDb = 10 * np.log10(power)
    return powerDb

while True: # endless loop
    # Uncomment the following line to reduce cpu usage
    #time.sleep(1/UPDATE_RATE_HZ_MQTT/4)
    for i in range(6): # round-robin for each sdr
        try: # read with zmq.DONTWAIT which could throw zmq.error.Again error
            binary=zmqsockets[i].recv(zmq.DONTWAIT) # Alternative: zmqSocket.recv(zmq.DONTWAIT)
        except zmq.error.Again:  # catch the DONTWAIT exception if there is nothing more to read
            continue
        # if we reach this line, we have read data and can interpret the float values and publish them or add them to the lists
        bs = bitstring.BitStream(binary)
        index = bs.read('floatle:32')
        value = bs.read('floatle:32')
        frequency = getFrequencyFromIndex(index)
        powerDb = getPowerDbFromValue(value)
        """
        # If we use the lists, append and check for NUM_SAMPLES_PER_UPDATE
        zmqindexlists[i].append(index)
        zmqvaluelists[i].append(value)
        if len(zmqindexlists[i]) >= NUM_SAMPLES_PER_UPDATE: # desired number of samples for appropriate update rate reached, publish
            # determine the mean of the values gathered so far and convert to power
            value = np.mean(zmqvaluelists[i])
            powerDb = getPowerDbFromValue(value)
            # determine the fft-bin that occurred most often and convert to frequency
            pdseries = pd.Series(zmqindexlists[i]*2) # dirty, dirty hack: In pandas0.17.1 (Ubuntu 16.04), you need at least two values to find a mode
            modes = pdseries.mode()
            index = modes[0]
            frequency = getFrequencyFromIndex(index)
        """
        if True: # NOT USING THE LISTS, otherwise use the other condition
            # create antenna-name-string
            antenna = "antenna_" + str(i + 1) + ".1"
            # print and publish, TODO: Use Json!
            print(antenna + ": " + str(frequency) + " -> " + str(powerDb) + "dB")
            mqttClient.publish(topic="/sdr/"+antenna+"/frequency", payload=str(frequency), qos=0, retain=False)
            mqttClient.publish(topic="/sdr/"+antenna+"/rssi", payload=str(powerDb), qos=0, retain=False)
            # reset the lists
            """
            zmqindexlists[i] = []
            zmqvaluelists[i] = []
            """
            statistic[i] += 1
            print("Stats: " + str(statistic))

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
#client.loop_forever()
