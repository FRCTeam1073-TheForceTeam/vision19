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
        elif mode == "lines":
                return "./openmv/lineSegProcessing.py"
        elif mode == "cargo":
                return "./openmv/cargo.py"
        elif mode == "video":
                return "./openmv/video.py"
        elif mode == "learncolor":
                return "./openmv/learncolor.py"
        elif mode == "hatch":
                return "./openmv/hatchfinder.py"
                
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
cam_names = []
# Set predefined modes for the robot:
cam_mode = ["hatch", "hatch", "video", "video", "video", "video", "video"]

for ii in range(0, 8):
        name = "/dev/ttyACM%d" % ii
        if os.path.exists(name):
                cam_names.append(name)

print("STARTING CAMERA DEVICES:")
print(cam_names)
if len(cam_names) == 0:
        print("No Cameras")
        exit(-1)
else:
        print("Starting...")

# Create all our camera managers and set default modes
for name in cam_names:
        cam.append(CameraManager(name))


# Parse our video port argument
videoPort = sys.argv[1]

# networkTables initialization for our CameraFeedback table
serverIP = sys.argv[2]
NetworkTables.initialize(server=serverIP)
nt = NetworkTables.getTable("CameraFeedback")

              
#main loop
cam_frame = []

print("RUNNING ID ON CAMERA DEVICES:")
for ci in range(0,len(cam)):
        set_mode(cam[ci], "id")
        while cam[ci].get_id() < 0:
                try:
                        cam[ci].processData()
                except:
                        pass
                
                
print("LOADED ALL CAMERA IDs:")
for ci in range(0, len(cam)):
        print("Cam port %d with ID = %d"%(ci, cam[ci].get_id()))
                

print("Setting camera modes...")
for ci in range(0,len(cam)):
        print("Cam ID %d mode: %s"%(cam[ci].get_id(), cam_mode[cam[ci].get_id()]))
        set_mode(cam[ci], cam_mode[cam[ci].get_id()])
        cam_frame.append(0)
        nt.putString("cam_%d_mode" %ci, cam_mode[cam[ci].get_id()])

# create image webserver running on separate thread:
server_address = ('', int(videoPort))
httpd = http.server.HTTPServer(server_address, ImageHandler)
httpdThread = threading.Thread(target = httpd.serve_forever)
print("Starting video server thread...")
httpdThread.start()

loopCounter = 0
while True:
        for ci in range(0,len(cam)):
                try:
                        cam[ci].processData()
                        cam_frame[ci] = cam_frame[ci] + 1
                except:
                        pass
                
                if len(cam[ci].data) > 0:
                        if cam_mode[ci] == "lines":
                                data = []
                                for line in cam[ci].data:
                                        data.append(line["x1"])
                                        data.append(line["y1"])
                                        data.append(line["x2"])
                                        data.append(line["y2"])
                                        data.append(line["theta"])
                                        data.append(line["magnitude"])
                                        data.append(line["length"])
                                nt.putNumberArray("cam_%d_lineseg" %cam[ci].cam, data)
                                nt.putNumberArray("cam_%d_cargo" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_hatch" %cam[ci].cam, [])
                        
                        elif cam_mode[ci] == "cargo":
                                data = []
                                for blob in cam[ci].data:
                                        data.append(blob["cx"])
                                        data.append(blob["cy"])
                                        data.append(blob["w"])
                                        data.append(blob["h"])
                                        data.append(blob["pixels"])
                                        data.append(blob["color"])
                                nt.putNumberArray("cam_%d_cargo" %cam[ci].cam, data)
                                nt.putNumberArray("cam_%d_lineseg" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_hatch" %cam[ci].cam, [])

                        elif cam_mode[ci] == "video":
                                data = []
                                nt.putNumberArray("cam_%d_cargo" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_lineseg" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_hatch" %cam[ci].cam, [])

                        elif cam_mode[ci] == "learncolor":
                                data = []
                                nt.putNumberArray("cam_%d_cargo" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_lineseg" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_hatch" %cam[ci].cam, [])


                        elif cam_mode[ci] == "hatch":
                                data = []
                                for blob in cam[ci].data:
                                        data.append(blob["tx"])
                                        # data.append(blob["ty"])
                                        data.append(blob["trange"])
                                        #data.append(blob["tconfidence"])
                                nt.putNumberArray("cam_%d_cargo" %cam[ci].cam, [])
                                nt.putNumberArray("cam_%d_hatch" %cam[ci].cam, data)
                                nt.putNumberArray("cam_%d_lineseg" %cam[ci].cam, [])

                nt.putString("cam_%d_status" %cam[ci].cam, "ok")
                nt.putNumber("cam_%d_frame" %cam[ci].cam, cam_frame[ci])
                nt.putNumber("cam_%d_width" %cam[ci].cam, cam[ci].width)
                nt.putNumber("cam_%d_height" %cam[ci].cam, cam[ci].height)

                newmode = nt.getString("cam_%d_mode" %cam[ci].cam, cam_mode[ci])
                if newmode != cam_mode[ci]:
                        cam_mode[ci] = newmode
                        set_mode(cam[ci], cam_mode[ci])
                
                if cam[ci].get_ready():
                        cam[ci].fb_update()

        if loopCounter %1200 == 0:
                for c in range(0, len(cam)):
                        if cam[c].get_ready():
                                try:
                                        imgData = io.BytesIO()
                                        cam[c].get_image(imgData)
                                        outf = open("./img_cam_%d_%d.jpeg" % (cam[c].get_id(), (loopCounter/1200)), "wb")
                                        outf.write(imgData.getvalue())
                                        outf.close()
                                except:
                                        pass

                                  
        loopCounter = loopCounter + 1


