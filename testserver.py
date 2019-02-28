from networktables import NetworkTables
import time
import sys

NetworkTables.initialize()
sd = NetworkTables.getTable("CameraFeedback")

while True:
    time.sleep(10000) 
