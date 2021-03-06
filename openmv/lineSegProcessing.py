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
sensor.skip_frames(time = 1500)
led1.off()
sensor.set_auto_whitebal(False)

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}

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

# Main Loop:
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    isActive = False;

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, pixels_threshold=45, area_threshold=75,
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

    for b in blobs:
        #img.draw_rectangle(b.rect(), color=(0,80,0))
        if b.area() < 1700:
           roi = (b.x()-4, b.y()-4, b.w()+8, b.h()+8)
           img.draw_rectangle(roi, color=(90,0,0))
           segs = img.find_line_segments(roi=roi, merge_distance = 1, max_theta_diff = 5)
           for seg in segs:
               if  seg.length() > 20:
                   isActive = True
                   linesegs.append(seg)

    for l in linesegs:
        img.draw_line(l.line(), color = (255, 0, 0))
        print(l)

    print(endOfPacket)

    if isActive:
        led2.on()
    else:
        led2.off()
