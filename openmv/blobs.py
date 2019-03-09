# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking using the OpenMV Cam.

import sensor, image, time
import pyb
#print("Letting auto algorithms run. Don't put anything in front of the camera!")

fmt = sensor.RGB565
res = sensor.QVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)


file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
led1.on()
sensor.skip_frames(time = 1500)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
led1.off()


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

thresh = []

datafile = open("color.dat","r")
for l in datafile.readlines():
        try:
                thresh.append(int(l))
        except:
                pass

datafile.close()

while(True):
    clock.tick()
    img = sensor.snapshot()
    adjustBrightness(img)
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)

    for blob in img.find_blobs([thresh], pixels_threshold=100, area_threshold=100, merge=True, margin=10):
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(), blob.cy())
                print(blob)
                print(endOfPacket)




