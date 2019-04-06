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
#sensor.set_brightness(0)
#sensor.set_saturation(0)
led1.on()
sensor.skip_frames(time = 2000)
led1.off()
sensor.set_auto_whitebal(False)
sensor.set_auto_gain(False)
sensor.set_auto_exposure(False)

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
targetPacket = {"xc": 0, "yc": 0, "length": 0, "separation": 0}


# Update threshold to allow auto gain/exposure changes:
def computeThreshold(img):
    #hist = img.get_histogram()
    #return [(0,hist.get_percentile(0.2).l_value()),(-40,40),(-40,40)]
    return [(0, 25), (-20,20), (-20,20)]

#finding the score of potential line matches based on separation, angles, and y center points
def score(la, lb):
    cost = 0.0
    if abs(la.x1() - lb.x1()) > 350: # too far
        return 100000.0
    if abs(la.x1() - lb.x1()) < 40:  # too close
        return 100000.0

    cost = cost + (abs(la.y1() - lb.y1()) * 20) # adds the difference on the vertical plane
    cost = cost + (abs(la.length() - lb.length()) * 5)  # length
    cost = cost + (abs(abs(la.x1() - lb.x1()) - abs(la.x2() - lb.x2())) * 2) #parallelism
    print("cost %f" %cost)
    return cost

#finding lines that are the "best match" for eacher (at the right distance and angle)
def bestMatch(ls, lmatch, li):
    cost = 100000.0
    best = -1
    for lj in range(li+1, len(ls)):
        if lmatch[lj] < 0:
            s = score(ls[li], ls[lj])
            if s < cost:
                best = lj
                #print("best %d" %best)
                cost = s

    if cost > 400:
        return -1
    else:
        return best

# Search key allows ordering lines by x1:
def x1(line):
    return line.x1()

# TODO: Insure line ordering


# Initial threshold value from first picture:
img = sensor.snapshot()

# Adjust auto threshold to exposure settings;
thresh = computeThreshold(img)

# Set the region of the image that we will search:
searchroi = (int(sensor.width()* 0.0),int(sensor.height()*0.15),
             int(sensor.width()* 1.0),int(sensor.height()*0.7))

counter = 0

# Main Loop:
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()

    if enable_lens_corr:
        img.lens_corr(1.8) # for 2.8mm lens...

    isActive = False

    if counter < 10:
        counter = counter + 1
    else:
        thresh = computeThreshold(img)
        counter = 0

    # Locate blobs to create a set of ROIs to use for line searching:
    blobs = img.find_blobs(thresh, roi=searchroi, pixels_threshold=50, area_threshold=70,
                           merge=False, margin=5)

    linesegs = []

    for b in blobs:
        if b.area() < 30000 and b.h() > (b.w() * 1.4):
            roi = (b.x()-2, b.y()-2, b.w()+4, b.h()+4)
            img.draw_rectangle(roi, color=(0,200,0))
            regLine = img.get_regression(thresh, roi=roi, pixels_threshold=20, area_threshold=40)
            if regLine and (regLine.theta() > 150 or regLine.theta() < 30):
                linesegs.append(regLine)

    # Now sort through our best "black lines" in x1 coordinate order:
    linesegs = sorted(linesegs, key=x1)
    lmatch = [-1 for i in range(len(linesegs))]

    # Loop over all but last line.
    # Search for matches from this line onward, makes sure you don't compare
    # line to itself or create 'double answers'.
    if linesegs:
        for li in range(0, len(linesegs) - 1):
            lmatch[li] = bestMatch(linesegs, lmatch, li)
            lmatch[lmatch[li]] = li
            #print("%d matched %d" %(li, lmatch[li]))

    print(linesegs)
    print(lmatch)

    for l in range(0, len(lmatch)):
        if lmatch[l] != -1:
            la = linesegs[l]
            lb = linesegs[lmatch[l]]
            center = int((la.x1() + lb.x1()) / 2.0)
            targetPacket["xc"] = center - sensor.width()/2
            targetPacket["yc"] = int((la.y1() + la.y2())/2.0)
            targetPacket["length"] = la.length()
            targetPacket["separation"] = abs(la.x1() - lb.x1())
            img.draw_line((center,0,center,sensor.height()), color = (0,255,0))
            img.draw_line((la.x1(), int((la.y1()+la.y2())/2), lb.x1(), int((lb.y1()+lb.y2())/2)), color = (0,255,0))
            print(targetPacket)
            lmatch[l] = -1
            lmatch[lmatch[l]] = -1
            continue

    for l in linesegs:
        img.draw_line(l.line(), color = (255, 255, 255))
        #print(l)

    print(endOfPacket)
    sensor.flush()

    if isActive:
        led2.on()
    else:
        led2.off()
