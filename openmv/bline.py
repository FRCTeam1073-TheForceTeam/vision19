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
sensor.set_saturation(2)
led1.on()
sensor.skip_frames(time = 1500)
led1.off()
sensor.set_auto_whitebal(False)

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
targetPacket = {"xc": 0, "yc": 0, "length": 0, "separation": 0}

# All lines also have `x1()`, `y1()`, `x2()`, and `y2()` methods to
# get their end-points and a `line()` method to get all the above as
# one 4 value tuple for `draw_line()`.

# Update threshold to allow auto gain/exposure changes:
def computeThreshold(img):
    #hist = img.get_histogram()
    #return [(0,hist.get_percentile(0.04).l_value()),(0,0),(0,0)]
    return [(0, 20, -5, 5, -5, 5)]

# Initial threshold value from first picture:
img = sensor.snapshot()

# Adjust auto threshold to exposure settings;
thresh = computeThreshold(img)
counter = 0

searchroi = (0,int(sensor.height()*0.15),sensor.width(),int(sensor.height()*0.7))

# Search key allows ordering lines by x1:
def x1(line):
    return line.x1()



# Main Loop:
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    isActive = False

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, roi=searchroi, pixels_threshold=45, area_threshold=75,
                           merge=True, margin=10)

    # `merge_distance` controls the merging of nerby lines. At 0 (the
    # default), no merging is done. At 1, any line 1 pixel away from
    # another is merged... and so on as you increase this value. You
    # may wish to merge lines as line segment detection produces a lot
    # of line segment results.

    # `max_theta_diff` controls the maximum amount of rotation
    # difference between any two lines about to be merged. The default
    # setting allows for 15 degrees.
    linesegs = []
    if counter < 10:
        counter = counter + 1
    else:
        thresh = computeThreshold(img)
        counter = 0

    for b in blobs:
        if b.area() < 15000:
            roi = (b.x()-2, b.y()-2, b.w()+4, b.h()+4)
            img.draw_rectangle(roi, color=(90,0,0))
            regLine = img.get_regression(thresh, roi=roi, pixels_threshold=40, area_threshold=40)
            if regLine and (regLine.theta() > 165 or regLine.theta() < 15):
                linesegs.append(regLine)

    # Now sort through our best "black lines" in x1 coordinate order:
    linesegs = linesegs.sort(key=x1)

    # Loop over all but last line.
    # Search for matches from this line onward, makes sure you don't compare
    # line to itself or create 'double answers'.
    if linesegs:
        for l1 in range(0, len(linesegs) - 1):
            for l2 in range(l1+1, len(linesegs)):
                # Not the "double" line:
                if abs(linesegs[l1].x1() - linesegs[l2].x1()) > 30:
                    center = int((linesegs[l1].x1() + linesegs[l2].x1()) / 2.0)
                    targetPacket["xc"] = center - sensor.width()/2
                    targetPacket["yc"] = int((linesegs[l1].y1() + linesegs[l1].y2())/2.0)
                    targetPacket["length"] = linesegs[l1].length()
                    targetPacket["separation"] = abs(linesegs[l1].x1() - linesegs[l2].x1())
                    img.draw_line((center,0,center,sensor.height()), color = (0,255,0))
                    print(targetPacket)
                    continue


        for l in linesegs:
            img.draw_line(l.line(), color = (255, 0, 0))
            #print(l)

    print(endOfPacket)

    if isActive:
        led2.on()
    else:
        led2.off()
