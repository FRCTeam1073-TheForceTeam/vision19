from networktables import NetworkTables
import sys
import time

#network number = 127.0.0.1

if len(sys.argv) < 3:
    print("Error: specify an IP to connect to!")
    print("Error: specify a boolean!")
    exit(0)

ip = sys.argv[1]

NetworkTables.initialize(server=ip)

table = NetworkTables.getTable("CameraFeedback")

dataEnable = table.getEntry("data_enable")

if sys.argv[2] == "True":
    dataEnable.setBoolean(True)
else:
    dataEnable.setBoolean(False)
    
time.sleep(0.3)
