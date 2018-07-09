import paho.mqtt.client as mqtt

import math
import json
import copy
import numpy as np

from collections import deque
from copy import deepcopy




# position of antenna in the vicon coordinate system
antenna_keys = ("1.1","3.1","5.1") # odd
print(antenna_keys)
# antenna_keys = ("2.1","4.1","6.1") # even
