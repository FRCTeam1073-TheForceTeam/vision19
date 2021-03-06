#
# Find white alignment lines on floor /w size limits and auto thresholder.
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
sensor.set_brightness(0)
sensor.set_saturation(2)
sensor.set_vflip(True)
led1.on()
sensor.skip_frames(time = 1500)
led1.off()
sensor.set_auto_whitebal(False)

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
targetPacket = {"xc": 0, "yc": 0, "theta": 0, "length": 0, "area": 0}

# All lines also have `x1()`, `y1()`, `x2()`, and `y2()` methods to
# get their end-points and a `line()` method to get all the above as
# one 4 value tuple for `draw_line()`.

# Update threshold to allow auto gain/exposure changes:
def computeThreshold(img):
    hist = img.get_histogram()
    return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]
    #hist = [0. 0. 0. 0. 0 .0]

# Initial threshold value from first picture:
img = sensor.snapshot()

# Adjust auto threshold to exposure settings;
thresh = computeThreshold(img)
counter = 0

searchroi = (0,int(sensor.height()*0.5),sensor.width(),int(sensor.height()*0.5))


# Main Loop:
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    isActive = False;

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, roi=searchroi, pixels_threshold=45, area_threshold=75,
                           merge=False, margin=10)

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

    # Search through blobs for maxmim area and taller than width.
    for b in blobs:
        if b.area() < 15000 and b.h() > b.w():
            roi = (b.x()-2, b.y()-2, b.w()+4, b.h()+4)
            img.draw_rectangle(roi, color=(90,0,0))
            regLine = img.get_regression(thresh, roi=roi, pixels_threshold=40, area_threshold=40)
            if regLine and (regLine.theta() > 130 or regLine.theta() < 50) and regLine.length() > 50:
                center = int((regLine.x1() + regLine.x2()) / 2.0)
                targetPacket["xc"] = center - sensor.width()/2
                targetPacket["yc"] = int((regLine.y1()+regLine.y2())/2.0)
                targetPacket["theta"] = regLine.theta()
                targetPacket["length"] = regLine.length()
                targetPacket["area"] = b.area()
                print(targetPacket)
                linesegs.append(regLine)


    for l in linesegs:
        img.draw_line(l.line(), color = (255, 0, 0))
        #print(l)

    print(endOfPacket)
    sensor.flush()

    if isActive:
        led2.on()
    else:
        led2.off()
