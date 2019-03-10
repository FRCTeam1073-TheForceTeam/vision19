#
# Automatic Hatch Blob finder
#

import sensor, image, time
import pyb

# Camera/Hardware Objects:
fmt = sensor.RGB565
res = sensor.QVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)

# Get Camera ID:
file = open("camId.txt")
cam = int(file.readline())
file.close()

# Set Up Sensor:
sensor.reset()
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
sensor.set_brightness(-1)
sensor.set_saturation(1)
led1.on()
sensor.skip_frames(time = 1500)
led1.off()
sensor.set_auto_gain(False)     # Must be turned off for color tracking
sensor.set_auto_whitebal(False) # Must be turned off for color tracking

# Set Up Packets:
blobPacket = {"cx": 0, "cy": 0, "w": 0, "h": 0, "pixels": 0,"color": 0}
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}


threshold1 = [35,  65, -15, 15, 20, 80] # Yellow LAB values
threshold2 = [0, 45, 30, 60, 30, 60]    # Orange LAB values

# Main Loop;
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()

    isActive = False
    for blob in img.find_blobs([threshold1], pixels_threshold=100, area_threshold=100, merge=True, merge_distance=10, margin=10):
        isActive = True
        img.draw_rectangle(blob.rect())
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 1
        print(blobPacket)

   # for blob in img.find_blobs([threshold2], pixels_threshold=100, area_threshold=100, merge=True, merge_distance=10, margin=10):
    #    img.draw_rectangle(blob.rect())
     #   blobPacket["cx"] = blob.cx()
      #  blobPacket["cy"] = blob.cy()
       # blobPacket["w"] = blob.w()
        #blobPacket["h"] = blob.h()
        #blobPacket["pixels"] = blob.pixels()
        #blobPacket["color"] = 2
        #print(blobPacket)

    print(endOfPacket)

    if isActive:
        led2.on()
    else:
        led2.off()

