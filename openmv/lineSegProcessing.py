
# Find Line Segments Example
#
# This example shows off how to find line segments in the image. For each line object
# found in the image a line object is returned which includes the line's rotation.

# find_line_segments() finds finite length lines (but is slow).
# Use find_line_segments() to find non-infinite lines (and is fast).

enable_lens_corr = False # turn on for straighter lines...

import sensor, image, time
import pyb

file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()
fmt = sensor.RGB565
res = sensor.QQVGA
sensor.set_pixformat(fmt) # grayscale is faster
sensor.set_framesize(res)
sensor.set_brightness(0)
sensor.set_saturation(1)
sensor.skip_frames(time = 3000)
sensor.set_auto_whitebal(False)
clock = time.clock()
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}

# All lines also have `x1()`, `y1()`, `x2()`, and `y2()` methods to get their end-points
# and a `line()` method to get all the above as one 4 value tuple for `draw_line()`.

def computeThreshold(img):
    hist = img.get_histogram()
    return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]

def adjustBrightness(img):
    #print("adjust")
    stats = img.get_statistics()
    exposure = sensor.get_exposure_us()
    gain = sensor.get_gain_db()

    if stats.l_mean() < 45:
        exposure = exposure + 200
    elif stats.l_mean() > 75:
        exposure = exposure - 200

    if exposure > 33000:
        gain = gain + 1
        exposure = 20000
    elif exposure < 8000:
        gain = gain - 1
        exposure = 30000

    if gain < 1:
        gain = 1
    elif gain > 16:
        gain = 16

    sensor.set_auto_exposure(False, exposure)
    sensor.set_auto_gain(False, gain)
    #print("lmean = %f" % stats.l_mean())
    #print("gain = %f" % gain)
    #print("exposure = %d" % exposure)


# Initial threshold value
img = sensor.snapshot()

# Adjust auto threshold to exposure settings
thresh = computeThreshold(img)
counter = 0

while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    clock.tick()
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, pixels_threshold=50, area_threshold=90,
                           merge=False, margin=10)


    # `merge_distance` controls the merging of nearby lines. At 0 (the default), no
    # merging is done. At 1, any line 1 pixel away from another is merged... and so
    # on as you increase this value. You may wish to merge lines as line segment
    # detection produces a lot of line segment results.

    # `max_theta_diff` controls the maximum amount of rotation difference between
    # any two lines about to be merged. The default setting allows for 15 degrees.
    linesegs = []
    if counter < 10:
        counter = counter + 1
    else:
        thresh = computeThreshold(img)
        #print(thresh)
        #adjustBrightness(img)
        counter = 0

    for b in blobs:
 #       img.draw_rectangle(b.rect(), color=(0,80,0))
        if b.area() < 1700:
           #img.draw_rectangle(b.rect(), color=(90,0,0))
           roi = (b.x()-2, b.y()-2, b.w()+4, b.h()+4)
           segs = img.find_line_segments(roi=roi, merge_distance = 1, max_theta_diff = 5)
           for seg in segs:
               if  seg.length() > 30:
                   linesegs.append(seg)

    for l in linesegs:
        img.draw_line(l.line(), color = (255, 0, 0))
        print(l)

    print(endOfPacket)


