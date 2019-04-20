from cameramanager import CameraManager			#see cameramanager.py
from networktables import NetworkTables
import time
import sys
import io
import os
# Allows us to send images over HTTP
import http.server
# Allows us to run HTTP server in a separate thread so we can poll camera
import threading
# Allows us to convert camera image to JPEG for HTTP Client
from PIL import Image



def give_script(mode):
        if mode == "id":
                return "./openmv/id.py"
        elif mode == "wline":
                return "./openmv/wline.py"
        elif mode == "bline":
                return "./openmv/bline.py"
        elif mode == "video":
                return "./openmv/video.py"


def set_mode(cam, mode):
        script = ""
        with open(give_script(mode), 'r') as fin:
                script = fin.read()
#       print(script)
        cam.stop_script()
        cam.enable_fb(True)        
        cam.exec_script(script)

# camera initialization, GLOBAL
cam = []

class ImageHandler(http.server.BaseHTTPRequestHandler):

        def do_GET(self):
                global cam
                try:
                        basepath = self.path.partition('?')
                        if basepath[0] == "/test.html":
                                print("Loading test page.")
                                self.send_response(200)
                                self.send_header("Content-Type", 'text/html')
                                self.send_header('Cache Control', 'no-cache')
                                fdata = open('./test.html', 'r')
                                testpage = fdata.read()
                                self.send_header('Content-Length',
                                                 len(testpage))
                                self.end_headers()
                                fdata.close()
                                self.wfile.write(bytes(testpage, 'utf-8'))
                                return
                                
                        ci = -1
                        camnum = basepath[0]
                        ci = int(camnum[1])

                        if ci >= 0:
                                imgData = io.BytesIO()
                                for jj in range(0, len(cam)):
                                        if cam[jj].get_id() == ci and cam[jj].get_ready():
                                               # print(">")
                                                cam[jj].get_image(imgData)
                                               # print("<")
                                                self.send_response(200)

                                                self.send_header('Content-Type','image/jpeg')
                                                self.send_header('Content-Length', imgData.tell())
                                                self.send_header('Cache Control', 'no-cache')
                                                self.end_headers()
                                                self.wfile.write(imgData.getvalue())
                                                return


                        self.send_response(404)
                        return
                except:
                        print("Web handler exception.")
                        self.send_response(404)
                        return

        # This stops it spewing output all the time.
        def log_message(self, format, *args):
                return



#  MAIN PROGRAM ENTRY:

# Check for available camera ports:
cam_devices = []

# Set predefined modes for the robot:
# These are indexed by camera ID
cam_mode = ["bline", "wline", "video", "video", "video", "video", "video"]

for ii in range(0, 8):
        device = "/dev/ttyACM%d" % ii
        if os.path.exists(device):
                cam_devices.append(device)

print("STARTING CAMERA DEVICES:")
print(cam_devices)
if len(cam_devices) == 0:
        print("No Cameras")
        exit(-1)
else:
        print("Starting...")

# Create all our camera managers and set default modes
for dev in cam_devices:
        cam.append(CameraManager(dev))


# Parse our video port argument
videoPort = sys.argv[1]

# networkTables initialization for our CameraFeedback table
serverIP = sys.argv[2]
NetworkTables.initialize(server=serverIP)
nt = NetworkTables.getTable("CameraFeedback")


#main loop
cam_frame = []

print("RUNNING ID ON CAMERA DEVICES:")
maxCamId = -1
for ci in range(0,len(cam)):
        set_mode(cam[ci], "id")
        while cam[ci].get_id() < 0:
                try:
                        cam[ci].processData()
                except:
                        pass

        if maxCamId < cam[ci].get_id():
                        maxCamId = cam[ci].get_id()
                        
# Now each camera knows its ID, deals with losing a cam0 for example

                
print("LOADED ALL CAMERA IDs:")
for ci in range(0, len(cam)):
        print("Cam device %s with ID = %d"%(cam_devices[ci], cam[ci].get_id()))
                

print("Setting camera modes...")
for ci in range(0,len(cam)):
        cami = cam[ci].get_id()
        print("Cam ID %d mode: %s"%(cami, cam_mode[cami]))
        set_mode(cam[ci], cam_mode[cami])
        cam_frame.append(0)
        nt.putString("cam_%d_mode" %cami, cam_mode[cami])

# create image webserver running on separate thread:
server_address = ('', int(videoPort))
httpd = http.server.HTTPServer(server_address, ImageHandler)
httpdThread = threading.Thread(target = httpd.serve_forever)
print("Starting video server thread...")
httpdThread.start()

# TOP OF LOOP
loopCounter = 0
sendNTables = True
disableCounter = 0

while True:
        tempSendNTables = nt.getBoolean("data_enable", True)
        if tempSendNTables == False and sendNTables == True:
                disableCounter = 5
        elif tempSendNTables == True:
                disableCounter = 0
                
        sendNTables = tempSendNTables
        
        for ci in range(0,len(cam)):
                # Mapped camera index value:
                cami = cam[ci].get_id()
                try:
                        cam[cami].processData()
                        cam_frame[cami] = cam_frame[cami] + 1
                except:
                        pass

                if cam_mode[cami] == "wline":
                        data = []
                        newCamData = cam[cami].readNewData()
                        for line in newCamData:
                                data.append(line["x1"])
                                data.append(line["y1"])
                                data.append(line["x2"])
                                data.append(line["y2"])
                                data.append(line["theta"])
                                data.append(line["length"])
                                data.append(line["area"])
                        if sendNTables == True:
                                nt.putNumberArray("cam_%d_wline" %cami, data)
#                                nt.putNumberArray("cam_%d_lineseg" %cami, [])
#                                nt.putNumberArray("cam_%d_bottomline" %cami, [])
#                                nt.putNumberArray("cam_%d_bline" %cami, [])
#                                nt.putNumberArray("cam_%d_greentarget" %cami, [])
#                                nt.putNumberArray("cam_%d_video" %cami, [])


                elif cam_mode[cami] == "bline":
                        data = []
                        newCamData = cam[cami].readNewData()
                        for target in newCamData:
                                #print("bline %d" %cami)
                                #print("bline: ", target)
                                data.append(target["xc"])
                                data.append(target["yc"])
                                data.append(target["length"])
                                data.append(target["separation"])
                        if sendNTables == True:
                                nt.putNumberArray("cam_%d_bline" %cami, data)
#                                nt.putNumberArray("cam_%d_bottomline" %cami, [])
#                                nt.putNumberArray("cam_%d_lineseg" %cami, [])
#                                nt.putNumberArray("cam_%d_wline" %cami, [])
#                                nt.putNumberArray("cam_%d_greentarget" %cami, [])
#                                nt.putNumberArray("cam_%d_video" %cami, [])


                elif cam_mode[cami] == "video":
                        data = []
#                        nt.putNumberArray("cam_%d_video" %cami, data) 
#                        nt.putNumberArray("cam_%d_greentarget" %cami, [])                                        
#                        nt.putNumberArray("cam_%d_bline" %cami, [])
#                        nt.putNumberArray("cam_%d_bottomline" %cami, [])
#                        nt.putNumberArray("cam_%d_lineseg" %cami, [])
#                        nt.putNumberArray("cam_%d_wline" %cami, [])

                if cam_frame[ci] % 3 == 0:
#                        nt.putString("cam_%d_status" %cami, "ok")
#                        nt.putNumber("cam_%d_frame" %cami, cam_frame[ci])
#                        nt.putNumber("cam_%d_width" %cami, cam[cami].width)
#                        nt.putNumber("cam_%d_height" %cami, cam[cami].height)

                        pass


                if disableCounter > 0:
                        nt.putNumberArray("cam_%d_bline" %cami, [])
                        nt.putNumberArray("cam_%d_wline" %cami, [])
                        disableCounter = disableCounter - 1
                if cam[ci].get_ready():
                        cam[ci].fb_update()

        if False:
                for c in range(0, len(cam)):
                        if cam[c].get_ready():
                                try:
                                        imgData = io.BytesIO()
                                        cam[c].get_image(imgData)
                                        outf = open("./img_cam_%d_%d.jpeg" % (cam[c].get_id(), (loopCounter/200)), "wb")
                                        outf.write(imgData.getvalue())
                                        outf.close()
                                except:
                                        pass

                                  
        loopCounter = loopCounter + 1
