# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking using the OpenMV Cam.

import sensor, image, time
import pyb
#print("Letting auto algorithms run. Don't put anything in front of the camera!")

fmt = sensor.RGB565
res = sensor.QVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)


file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
led1.on()
sensor.skip_frames(time = 1500)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
led1.off()
	
# Capture the color thresholds for whatever was in the center of the image.
r = [(320//2)-(50//2), (240//2)-(50//2), 50, 50] # 50x50 center of QVGA.


#print("Learning thresholds...")
threshold = [50, 50, 0, 0, 0, 0] # Middle L, A, B values.

led2.on()
for i in range(60):
        img = sensor.snapshot()
        hist = img.get_histogram(roi=r)
	lo = hist.get_percentile(0.01) # Get the CDF of the histogram at the 1% range (ADJUST AS 	NECESSARY)!
        hi = hist.get_percentile(0.99) # Get the CDF of the histogram at the 99% range (ADJUST AS 	NECESSARY)!
	# Average in percentile values.
	threshold[0] = (threshold[0] + lo.l_value()) // 2
	threshold[1] = (threshold[1] + hi.l_value()) // 2
	threshold[2] = (threshold[2] + lo.a_value()) // 2
	threshold[3] = (threshold[3] + hi.a_value()) // 2
	threshold[4] = (threshold[4] + lo.b_value()) // 2
	threshold[5] = (threshold[5] + hi.b_value()) // 2
	for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, 	margin=10):
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())
                img.draw_rectangle(r)
led2.off()	
	#print("Thresholds learned...")
	#print("Tracking colors...")



datafile = open("color.dat", "w")
#output.write("%d %d %d %d %d %d" % (threshold[0], threshold[1], threshold[2], threshold[3], threshold[4] threshold[5]))
for t in threshold:
    datafile.write("%d\n" % t)
    
datafile.close()


colorPacket = { 'threshold': threshold } 
while(True):
    clock.tick()                    # Update the FPS clock.
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    print(colorPacket)
    img = sensor.snapshot()         # Take a picture and return the image.
    print(endOfPacket)




