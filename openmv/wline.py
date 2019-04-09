#
# Find white alignment lines on floor /w size limits and auto thresholder.
#

enable_lens_corr = False # turn on for straighter lines...

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
sensor.skip_frames(time = 2000)
led1.off()
sensor.set_auto_whitebal(False)

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
targetPacket = {"x1": 0, "y1": 0, "x2": 0, "y2": 0, "theta": 0, "length": 0, "area": 0}

# All lines also have `x1()`, `y1()`, `x2()`, and `y2()` methods to
# get their end-points and a `line()` method to get all the above as
# one 4 value tuple for `draw_line()`.

# Update threshold to allow auto gain/exposure changes:
def computeThreshold(img):
    hist = img.get_histogram()
#   return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]
    return [(90, 100), (-10, 10), (-10, 10)]

# Initial threshold value from first picture:
img = sensor.snapshot()

# Adjust auto threshold to exposure settings;
thresh = computeThreshold(img)
counter = 0

# Only search bottom portion of the image:
searchroi = (0,int(sensor.height()*0.0),sensor.width(),int(sensor.height()*0.4))


# Main Loop:
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    isActive = False;

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, roi=searchroi, pixels_threshold=40, area_threshold=75,
                           merge=False, margin=10)

    linesegs = []
    if counter < 10:
        counter = counter + 1
    else:
        thresh = computeThreshold(img)
        counter = 0

    for b in blobs:
        #img.draw_rectangle(b.rect(), color=(0,255,0))
        if b.area() < 10000 and b.h() > b.w()*1.3:
            roi = (b.x()-2, b.y()-2, b.w()+4, b.h()+4)
            img.draw_rectangle(roi, color=(0,255,0))
            regLine = img.get_regression(thresh, roi=roi, pixels_threshold=40, area_threshold=40)
            if regLine and (regLine.theta() > 110 or regLine.theta() < 70) and regLine.length() > 30:
                center = int((regLine.x1() + regLine.x2()) / 2.0)
                targetPacket["x1"] = regLine.x1()
                targetPacket["y1"] = regLine.y1()
                targetPacket["x2"] = regLine.x2()
                targetPacket["y2"] = regLine.y2()
                targetPacket["theta"] = regLine.theta()
                targetPacket["length"] = regLine.length()
                targetPacket["area"] = b.area()
                print(targetPacket)
                linesegs.append(regLine)


    for l in linesegs:
        img.draw_line(l.line(), color = (0, 255, 0))
        #print(l)

    # Draw hatch lines
    #img.draw_line((100,215, 100, 240), color= (0,255,0))
    #img.draw_line((244,215, 244, 240), color= (0,255,0))

    print(endOfPacket)
    sensor.flush()

    if isActive:
        led2.on()
    else:
        led2.off()
