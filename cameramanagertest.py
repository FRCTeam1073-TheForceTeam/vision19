#!/usr/bin/env python
import sys
import numpy as np
import cameramanager
from time import sleep
from PIL import Image

if len(sys.argv)!= 3:
    print ('usage: cam_fb.py <serial port> <script>')
    sys.exit(1)

with open(sys.argv[2], 'r') as fin:
    script = fin.read()

portname = sys.argv[1]
connected = False
cam = cameramanager.CameraManager(portname)
connected = True

if not connected:
    print ( "Failed to connect to OpenMV's serial port.\n"
            "Please install OpenMV's udev rules first:\n"
            "sudo cp openmv/udev/50-openmv.rules /etc/udev/rules.d/\n"
            "sudo udevadm control --reload-rules\n\n")
    sys.exit(1)

# Set higher timeout after connecting for lengthy transfers.
cam.set_timeout(1*2) # SD Cards can cause big hicups.
cam.stop_script()
cam.enable_fb(True)
cam.exec_script(script)

# init screen
running = True
counter = 0
while running:
    
    # read framebuffer
    fb = cam.fb_dump()
    if fb != None:
        #print(fb)
        capName = "cap%d.jpg" % counter
        image = Image.fromarray(fb[2])
        image.save(capName, quality=80)
        
    cam.processData()

        
    counter = counter+1
        
cam.stop_script()
