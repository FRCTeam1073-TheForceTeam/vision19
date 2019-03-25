= visionmanager design

(overarching visual)

                      protocol		   networktables
      CAMERA #N  <-------------->  RPI  <--------------------> RIO
	  		   visionmanager.py		     Robot Code

= NetworkTables API   INTERFACE:

	- (N cameras) each cam has set of keys in nt that match this pattern:

		- cam_#_mode displayed as a string, can be "blob" or
                  "line" and dictates the structure of the array in
                  later bits
		
        	- cam_#_frame      a coutner that will run constantly
		
		- cam_#_status string, the feedback for the driver
                  station (aka "this camera died, this one caught on
                  fire, and this camera never, calls me")
		
		- cam_#_lineseg number array [x1, y1, x2, y2, theta,
                  score, length] <-- "n" number of times
		
		- cam_#_hatch number array [tx, tx, trange, tconfidence]
		<-- "n" number of times for n blobs
		
		- cam_#_cargo number array [cx, cy, width, height,
                  pixels, color] <-- "n" number of times for n blos
		
		- cam_#_?(etc.)  number array [ ~~fill~in~the~blank~~]
                  <-- "n" number of times
		
	- inputs: cam_mode
	- outputs: cam_frame, cam_status, cam_lineseg, cam_blobs, cam_etc.


= openmv serial protocol:

After each vision cycle, the camera sends a start of frame packet,
followed by n data packets for each frame.  startOfFrame = '{"cam":
<number>, "time": <number2>, "res": <num3>, "fmt": <num4>}' where
number is the assigned camera number and time is the timestamp of the
frame in the camera. Res and fmt are the resolution and format.  At
the end of each vision cycle we send the endOfFrame packet.
endOfFrame '{"end": 0}'.

example packet from openmv: bytearray(b'{"x":0, "y":0, "w":319,
"h":239, "pixels":22589, "cx":122, "cy":111, "rotation":1.326613,
"code":1, "count":6}')

imports (from all programs):
    -from cameramanager import CameraManager
    -from networktables import NetworkTables
    -time
    -sys
    -io
    -os
    -http.server
    -threading
    -from PIL import Image
    -struct
    -serial
    -platform
    -numpy as np
    -sensor
    -pyb
    
