# Hello World Example
#
# Welcome to the OpenMV IDE! Click on the gear button above to run the script!

import sensor, image, time
import pyb

fmt = sensor.RGB565
res = sensor.QVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)

file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()                      # Reset and initialize the sensor.
sensor.set_pixformat(fmt) # Set pixel format to RGB565
sensor.set_framesize(res)  # Set frame size to QVGA (320x240)
led1.on()
sensor.skip_frames(time = 1500)     # Wait for settings take effect.
led1.off()
clock = time.clock()                # Create a clock object to track the FPS.
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}


while(True):
    clock.tick()                    # Update the FPS clock.
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()         # Take a picture and return the image.
    print(endOfPacket)
