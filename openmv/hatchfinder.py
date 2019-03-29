#
# Automatic Hatch Blob finder
#

import sensor, image, time
import pyb
from pyb import SPI

# Camera/Hardware Objects:
fmt = sensor.RGB565
res = sensor.QVGA
led1 = pyb.LED(1)
led2 = pyb.LED(2)

# SPI bus for lighting
spi = SPI(2, SPI.MASTER, 500000, polarity=1, phase=0, crc=None)
ledreset = bytearray(24)
# Reset the LED strip
spi.write(ledreset)

# Turn on Green lighting:
ledgreen = bytearray(24)
for ii in range(0,len(ledgreen)):
    ledgreen[ii] = 128

intensity = 110;

for ii in range(0,8):
    ledgreen[ii*3] = 128 + intensity;


spi.write(ledgreen)
spi.write(ledreset)


# Get Camera ID:
file = open("camId.txt")
cam = int(file.readline())
file.close()

# Set Up Sensor:
sensor.reset()
sensor.set_pixformat(fmt)
sensor.set_framesize(res)
sensor.set_brightness(-2)
sensor.set_saturation(2)
led1.on()
sensor.skip_frames(time = 1500)
led1.off()
sensor.set_auto_gain(False)     # Must be turned off for color tracking
sensor.set_auto_whitebal(False) # Must be turned off for color tracking
#sensor.set_auto_exposure(False) # Turning off to track down problem

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": fmt, "height": sensor.height(), "width": sensor.width()}
endOfPacket = { "end": 0}
targetPacket = {"tx": 0, "ty": 0, "trange": 0, "tconfidence": 0}


# Update threshold to allow auto gain/exposure changes:
# TODO:
def computeThreshold(img, threshold_base):
    hist = img.get_histogram()
#    return [(hist.get_percentile(0.97).l_value(),100),(0,0),(0,0)]
    return threshold_base


# Figure out if two markers are associated with single hatch target:
def close(a, b):
    if abs(a.x2() - b.x2()) > abs(a.x1() - b.x1()):
        if abs(a.x1() - b.x1()) < 120:
            return True
        else:
            return False
    else:
        return False

# Compute a range estimate based on separation of markers:
def rangeFunction(a, b):
    return abs(a.x1() - m_b.x1())


# Set Up Threshold LBA for Green Markers
thresholdM_base = [75, 100, -60, -30, -10, 10]
thresholdM = thresholdM_base;


# Set up for main loop
# Green LED on:
led2.on()
counter = 0
# Main Loopq
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    img = sensor.snapshot()
    markers = []

    isActive = False

    for blob in img.find_blobs([thresholdM], pixels_threshold=45, area_threshold=50, merge=True, merge_distance=5, margin=10):
        regLine = img.get_regression([thresholdM], roi=blob.rect(), pixels_threshold=45, area_threshold=50)
        if regLine:
            img.draw_line(regLine.line(), color = 0)
            markers.append(regLine)

        #img.draw_rectangle(blob.rect(), color=(0, 100, 0))


    for m_a in markers:
        if m_a.theta() > 93:
            for m_b in markers:
                if m_b.theta() < 87 and close(m_a, m_b):
                    center = int((m_a.x1() + m_b.x1()) / 2.0)
                    targetPacket["tx"] = center - sensor.width()/2
                    targetPacket["ty"] = m_a.y1()
                    targetPacket["trange"] = rangeFunction(m_a, m_b)
                    targetPacket["tconfidence"] = m_a.length()
                    print(targetPacket)
                    img.draw_line((center, 0, center, sensor.height()), color=(0, 0, 0))
                    #print("dist = %d" %(abs(m_a.x1() - m_b.x1())))
                    break


    print(endOfPacket)

    if counter < 20:
        counter = counter + 1
    else:
        thresholdM = computeThreshold(img, thresholdM_base)
        counter = 0
