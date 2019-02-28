# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking using the OpenMV Cam.

import sensor, image, time
print("Letting auto algorithms run. Don't put anything in front of the camera!")

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_brightness(-2)
sensor.set_saturation(1)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(True) # must be turned off for color tracking
sensor.set_auto_whitebal(True) # must be turned off for color tracking
clock = time.clock()


redthresh = [60, 70, 40, 70, 10, 40]
bluethresh = [50, 80, -20, 10, -45, -30]

while(True):
    clock.tick()
    img = sensor.snapshot()
    print("r")
    for blob in img.find_blobs([redthresh], pixels_threshold=60, area_threshold=60, merge=True, margin=20):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        print(blob)
    print("b")
    for blob in img.find_blobs([bluethresh], pixels_threshold=60, area_threshold=60, merge=True, margin=20):
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        print(blob)
    print(clock.fps())
