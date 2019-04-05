# Find Circles Example
#
# This example shows off how to find circles in the image using the Hough
# Transform. https://en.wikipedia.org/wiki/Circle_Hough_Transform
#
# Note that the find_circles() method will only find circles which are completely
# inside of the image. Circles which go outside of the image/roi are ignored...

import sensor, image, time

sensor.reset()
sensor.set_pixformat(sensor.RGB565) # grayscale is faster
sensor.set_framesize(sensor.QQVGA)
#sensor.set_brightness(-3)
#sensor.set_saturation(2)
sensor.skip_frames(time = 2000)
clock = time.clock()

sensor.set_auto_gain(False, gain_db=1)
sensor.set_auto_exposure(False, exposure_us=14000)
sensor.set_auto_whitebal(False)

# Central band from the image.
mainRoi = (0,int(sensor.height()*0.15),sensor.width(),int(sensor.height()*0.8))



while(True):
    clock.tick()
 #   img = sensor.snapshot().lens_corr(1.8)
    img = sensor.snapshot()

    # Circle objects have four values: x, y, r (radius), and magnitude. The
    # magnitude is the strength of the detection of the circle. Higher is
    # better...

    # `threshold` controls how many circles are found. Increase its value
    # to decrease the number of circles detected...

    # `x_margin`, `y_margin`, and `r_margin` control the merging of similar
    # circles in the x, y, and r (radius) directions.

    # r_min, r_max, and r_step control what radiuses of circles are tested.
    # Shrinking the number of tested circle radiuses yields a big performance boost.

    for c in img.find_circles(roi=mainRoi, threshold = 2400, x_margin = 15, y_margin = 15, r_margin = 8,
            r_min = 15, r_max = 75, r_step = 3):
        img.draw_circle(c.x(), c.y(), c.r(), color = (255, 0, 0))
        print(c)

  #  print("FPS %f" % clock.fps())
    #print("G %f" % sensor.get_gain_db())
    #print("E %f" % sensor.get_exposure_us())
