# Automatic RGB565 Color Tracking Example
#
# This example shows off single color automatic RGB565 color tracking using the OpenMV Cam.

import sensor, image, time
import pyb
print("Letting auto algorithms run. Don't put anything in front of the camera!")

file = open("camId.txt")
cam = int(file.readline())
file.close()
sensor.reset()
fmt = sensor.RGB565
res = sensor.QQVGA
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
blobPacket = {"cx": 0, "cy": 0, "w": 0, "h": 0, "pixels": 0,"color": 0}
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
clock = time.clock()


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
    #print("exposure = %d" % exposure)def adjustBrightness(img):
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

threshold1 = [50,  78, -5, 5, 40, 60] # Yellow LAB values
threshold2 = [45, 60, 40, 60, 40, 60] # Yellow LAB values

while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs([threshold1], pixels_threshold=100, area_threshold=100, merge=True, merge_distance=10, margin=10):
        img.draw_rectangle(blob.rect())
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 1
        print(blobPacket)

    for blob in img.find_blobs([threshold2], pixels_threshold=100, area_threshold=100, merge=True, merge_distance=10, margin=10):
        img.draw_rectangle(blob.rect())
        blobPacket["cx"] = blob.cx()
        blobPacket["cy"] = blob.cy()
        blobPacket["w"] = blob.w()
        blobPacket["h"] = blob.h()
        blobPacket["pixels"] = blob.pixels()
        blobPacket["color"] = 2
        print(blobPacket)

    print(endOfPacket)
