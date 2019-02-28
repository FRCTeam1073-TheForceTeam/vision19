from networktables import NetworkTables
import sys
import time

#network number = 127.0.0.1

if len(sys.argv) < 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]

NetworkTables.initialize(server=ip)

table = NetworkTables.getTable("CameraFeedback")

if len(sys.argv) > 2:
    table.putString("cam_0_mode", sys.argv[2])

while True:
    print("cam_0_frame", table.getNumber("cam_0_frame", -1))
    print("cam_0_mode", table.getString("cam_0_mode", "<no mode>"))
    print("cam_0_width", table.getNumber("cam_0_width", -1))
    print("cam_0_height", table.getNumber("cam_0_height", -1))
    print("cam_0_status", table.getString("cam_0_status", "<no status>"))
    lineseg = table.getNumberArray("cam_0_lineseg", [])
    blobs = table.getNumberArray("cam_0_blobs",[])
    if len(lineseg) > 0:
        print("cam_0_lineseg", lineseg)
    if len(blobs) > 0:
        print("cam_0_blobs", blobs)
