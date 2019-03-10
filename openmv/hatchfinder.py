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


# Update threshold to allow auto gain/exposure changes:
# TODO:
def computeThreshold(img, threshold_base):
    hist = img.get_histogram()
#    return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]
    return threshold_base

# Set Up Threshold LBA for Orange
thresholdY_base = [55, 90, -15, 15, 20, 65] # Yellow LAB values
thresholdY = thresholdY_base;

thresholdO_base = [20, 70, 25, 75, 45, 75]    # Orange LAB values
thresholdO = thresholdO_base;


# Main Loop;
counter = 0
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()

    isActive = False
    for blob in img.find_blobs([thresholdY], pixels_threshold=50, area_threshold=200, merge=True, merge_distance=15, margin=10):
        isActive = True
        img.draw_rectangle(blob.rect())
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 1
        print(blobPacket)

    for blob in img.find_blobs([thresholdO], pixels_threshold=100, area_threshold=100, merge=True, merge_distance=10, margin=10):
        img.draw_rectangle(blob.rect())
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 2
        print(blobPacket)

    print(endOfPacket)

    if isActive:
        led2.on()
    else:
        led2.off()

    if counter < 20:
        counter = counter + 1
    else:
        thresholdY = computeThreshold(img, thresholdY_base)
        thresholdO = computeThreshold(img, thresholdO_base)
        counter = 0
