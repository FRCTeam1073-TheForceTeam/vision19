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
sensor.set_auto_exposure(False)

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


def close(a, b):
    if abs(a.x2() - b.x2()) > abs(a.x1() - b.x1()):
        return True
    else:
        return False


# Set Up Threshold LBA for Orange
thresholdY_base = [55, 90, -15, 15, 20, 65] # Yellow LAB values
thresholdY = thresholdY_base;

thresholdR_base = [10, 80, 35, 80, 14, 47]    # red LAB values
thresholdR = thresholdR_base;


# Main Loop;
counter = 0
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    markers = []

    isActive = False
    #for blob in img.find_blobs([thresholdY], pixels_threshold=50, area_threshold=200, merge=True, merge_distance=15, margin=10):
     #   isActive = True
      #  img.draw_rectangle(blob.rect())
       # blobPacket["cx"] = blob.cx()
        #blobPacket["cy"] = blob.cy()
        #blobPacket["w"] = blob.w()
        #blobPacket["h"] = blob.h()
        #blobPacket["pixels"] = blob.pixels()
        #blobPacket["color"] = 1
        #print(blobPacket)

    for blob in img.find_blobs([thresholdR], pixels_threshold=45, area_threshold=50, merge=True, merge_distance=5, margin=10):
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 2
        print(blobPacket)
        reg = img.get_regression([thresholdR], roi=blob.rect(), pixels_threshold=45, area_threshold=50)
        if reg:
            img.draw_line(reg.line(), color = 0)
            markers.append(reg)
            print(reg)

        for m in markers:
            if m.theta() > 93:
                for a in markers:
                    if a.theta() < 87 and close(m, a):
                        center = (m.x1() + a.x1()) / 2.0
                        img.draw_line((int(center), 0, int(center), 100), color=(0, 0, 50))

        img.draw_rectangle(blob.rect(), color=(0, 100, 0))

    print(endOfPacket)

    if isActive:
        led2.on()
    else:
        led2.off()

    if counter < 20:
        counter = counter + 1
    else:
        thresholdY = computeThreshold(img, thresholdY_base)
        thresholdR = computeThreshold(img, thresholdR_base)
        counter = 0
