#
# Cargo ball tracking program.
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
sensor.set_auto_gain(False)     # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking

# Set Up Packets:
blobPacket = {"cx": 0, "cy": 0, "w": 0, "h": 0, "pixels": 0,"color": 0}
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
led1.off()


# Update threshold to allow auto gain/exposure changes:
# TODO:
def computeThreshold(img, threshold_base):
    hist = img.get_histogram()
#    return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]
    return threshold_base

# Set Up Threshold LBA for Orange
threshold_base = [20, 80, 0, 80, 30, 75]
threshold = threshold_base;


# Main Loop:
counter = 0

while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()

    isActive = False
    for blob in img.find_blobs([threshold], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
                if blob.h() > 0:
                        ratio = blob.w() / blob.h()
                        if ratio > 0.9 and ratio < 1.1:
                                isActive = True
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
        threshold = computeThreshold(img, threshold_base)
        counter = 0
