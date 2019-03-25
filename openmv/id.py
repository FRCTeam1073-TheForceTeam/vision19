# ID only script:
#
import time
import pyb

# Camera/Hardware Objects:
led3 = pyb.LED(3)

# Get Camera ID:
led3.on();
file = open("camId.txt")
cam = int(file.readline())
file.close()

# Set Up Packets:
startOfPacket = { "cam": cam, "time": pyb.elapsed_millis(0), "fmt": 0, "height": 0, "width": 0}
endOfPacket = { "end": 0}

pyb.delay(100)
led3.off()
counter = 0
while(True):
    startOfPacket["time"] = pyb.elapsed_millis(0)
    print(startOfPacket)
    print(endOfPacket)
    counter = counter + 1
    
