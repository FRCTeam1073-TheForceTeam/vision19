# Find Lines Example
#
# This example shows off how to find lines in the image. For each line object
# found in the image a line object is returned which includes the line's rotation.

# Note: Line detection is done by using the Hough Transform:
# http://en.wikipedia.org/wiki/Hough_transform
# Please read about it above for more information on what `theta` and `rho` are.

# find_lines() finds infinite length lines. Use find_line_segments() to find non-infinite lines.

enable_lens_corr = False # turn on for straighter lines...

import sensor, image, time
import pyb

fmt = sensor.GRAYSCALE
res = sensor.QQVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)


file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()
sensor.set_pixformat(fmt) # grayscale is faster
sensor.set_framesize(res)
led1.on()
sensor.skip_frames(time = 1500)
led1.off()
clock = time.clock()
min_degree = 0
max_degree = 179
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}

while(True):
    clock.tick()
    img = sensor.snapshot()
    if enable_lens_corr: img.lens_corr(1.8) # for 2.8mm lens...
	
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)

    for l in img.find_lines(threshold = 1000, theta_margin = 16, rho_margin = 16):
        if (min_degree <= l.theta()) and (l.theta() <= max_degree):
            img.draw_line(l.line(), color = (255, 0, 0))
            print(l)

    print(endOfPacket)



