# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking
# using the OpenMV Cam.

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
fmt = sensor.RGB565
res = sensor.QQVGA
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
sensor.set_brightness(-1)
sensor.set_saturation(1)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
blobPacket = {"cx": 0, "cy": 0, "w": 0, "h": 0, "pixels": 0,"color": 0}
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
clock = time.clock()
led1.off()

threshold = [15, 65, 20, 50, 25, 70]

datafile = open("color.dat","r")
for l in datafile.readlines():
        try:
                thresh.append(int(l))
        except:
                pass

datafile.close()

while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    clock.tick()
    img = sensor.snapshot()

    for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
                if blob.h() > 0:
                        ratio = blob.w() / blob.h()
                        if ratio > 0.9 and ratio < 1.1:
                                img.draw_rectangle(blob.rect())
                                blobPacket["cx"] = blob.cx()
                                blobPacket["cy"] = blob.cy()
                                blobPacket["w"] = blob.w()
                                blobPacket["h"] = blob.h()
                                blobPacket["pixels"] = blob.pixels()
                                blobPacket["color"] = 2
                                print(blobPacket)

    print(endOfPacket)




