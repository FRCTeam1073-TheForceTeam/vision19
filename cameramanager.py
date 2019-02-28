#!/usr/bin/env python
# This file is part of the OpenMV project.
# Copyright (c) 2013/2014 Ibrahim Abdelkader <i.abdalkader@gmail.com>
# This work is licensed under the MIT license, see the file LICENSE for details.
#
# Openmv module.

import struct
import sys,time
import serial
import platform
import numpy as np
from PIL import Image
import threading



class CameraManager:

    __FB_HDR_SIZE   =12
    
    # USB Debug commands
    __USBDBG_CMD            = 48
    __USBDBG_FW_VERSION     = 0x80
    __USBDBG_FRAME_SIZE     = 0x81
    __USBDBG_FRAME_DUMP     = 0x82
    __USBDBG_ARCH_STR       = 0x83
    __USBDBG_SCRIPT_EXEC    = 0x05
    __USBDBG_SCRIPT_STOP    = 0x06
    __USBDBG_SCRIPT_SAVE    = 0x07
    __USBDBG_SCRIPT_RUNNING = 0x87
    __USBDBG_TEMPLATE_SAVE  = 0x08
    __USBDBG_DESCRIPTOR_SAVE= 0x09
    __USBDBG_ATTR_READ      = 0x8A
    __USBDBG_ATTR_WRITE     = 0x0B
    __USBDBG_SYS_RESET      = 0x0C
    __USBDBG_FB_ENABLE      = 0x0D
    __USBDBG_TX_BUF_LEN     = 0x8E
    __USBDBG_TX_BUF         = 0x8F

    ATTR_CONTRAST   =0
    ATTR_BRIGHTNESS =1
    ATTR_SATURATION =2
    ATTR_GAINCEILING=3

    __BOOTLDR_START         = 0xABCD0001
    __BOOTLDR_RESET         = 0xABCD0002
    __BOOTLDR_ERASE         = 0xABCD0004
    __BOOTLDR_WRITE         = 0xABCD0008

    def __init__(self, port, baudrate=921600, timeout=0.3):
        # open CDC port
        self.__serial =  serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.waitingForCycle = True
        self.firstPacket = True
        self.data = []
        self.width = 0
        self.height = 0
        self.packetBuffer = bytearray(1000)
        self.readIndex = 0
        self.lock = threading.Lock()
        self.cam = 0
        self.image = None

    def disconnect(self):
        try:
            if (self.__serial):
                self.__serial.close()
                self.__serial = None
        except:
            pass

    def set_timeout(self, timeout):
        self.__serial.timeout = timeout
    
    def fb_size(self):
        # read fb header
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_FRAME_SIZE, CameraManager.__FB_HDR_SIZE))
        return struct.unpack("III", self.__serial.read(12))

    def fb_update(self):
        self.lock.acquire()
        fb = self.fb_dump()
        if fb != None:
            self.image = Image.fromarray(fb[2])
    
        self.lock.release()

    def get_image(self, buffer):
        self.lock.acquire()
        self.image.save(buffer, format = "JPEG")
        self.lock.release()
        
    def fb_dump(self):
        size = self.fb_size()

        if (not size[0]):
            # frame not ready
            return None

        if (size[2] > 2): #JPEG
            num_bytes = size[2]
        else:
            num_bytes = size[0]*size[1]*size[2]

        # read fb data
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_FRAME_DUMP, num_bytes))
        buff = self.__serial.read(num_bytes)

        if size[2] == 1:  # Grayscale
            y = np.fromstring(buff, dtype=np.uint8)
            buff = np.column_stack((y, y, y))
        elif size[2] == 2: # RGB565
            arr = np.fromstring(buff, dtype=np.uint16).newbyteorder('S')
            r = (((arr & 0xF800) >>11)*255.0/31.0).astype(np.uint8)
            g = (((arr & 0x07E0) >>5) *255.0/63.0).astype(np.uint8)
            b = (((arr & 0x001F) >>0) *255.0/31.0).astype(np.uint8)
            buff = np.column_stack((r,g,b))
        else: # JPEG
            try:
                buff = np.asarray(Image.frombuffer("RGB", size[0:2], buff, "jpeg", "RGB", ""))
            except Exception as e:
                print ("JPEG decode error (%s)"%(e))
                return None

        if (buff.size != (size[0]*size[1]*3)):
            print("FB Size error.")
            return None

        return (size[0], size[1], buff.reshape((size[1], size[0], 3)))

    def exec_script(self, buf):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_SCRIPT_EXEC, len(buf)))
        self.__serial.write(buf.encode())

    def stop_script(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_SCRIPT_STOP, 0))

    def script_running(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_SCRIPT_RUNNING, 4))
        return struct.unpack("I", self.__serial.read(4))[0]

    def save_template(self, x, y, w, h, path):
        buf = struct.pack("IIII", x, y, w, h) + path
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_TEMPLATE_SAVE, len(buf)))
        self.__serial.write(buf)

    def save_descriptor(self, x, y, w, h, path):
        buf = struct.pack("HHHH", x, y, w, h) + path
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, __USBDBG_DESCRIPTOR_SAVE, len(buf)))
        self.__serial.write(buf)

    def set_attr(self, attr, value):
        self.__serial.write(struct.pack("<BBIhh", CameraManager.__USBDBG_CMD, __USBDBG_ATTR_WRITE, 0, attr, value))

    def get_attr(self, attr):
        self.__serial.write(struct.pack("<BBIh", CameraManager.__USBDBG_CMD, __USBDBG_ATTR_READ, 1, attr))
        return self.__serial.read(1)

    def reset(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, __USBDBG_SYS_RESET, 0))

    def bootloader_start(self):
        self.__serial.write(struct.pack("<I", __BOOTLDR_START))
        return struct.unpack("I", self.__serial.read(4))[0] == __BOOTLDR_START

    def bootloader_reset(self):
        self.__serial.write(struct.pack("<I", CameraManager.__BOOTLDR_RESET))

    def flash_erase(self, sector):
        self.__serial.write(struct.pack("<II", CameraManager.__BOOTLDR_ERASE, sector))

    def flash_write(self, buf):
        self.__serial.write(struct.pack("<I", CameraManager.__BOOTLDR_WRITE) + buf)

    def tx_buf_len(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_TX_BUF_LEN, 4))
        return struct.unpack("I", self.__serial.read(4))[0]

    def tx_buf(self, bytes):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_TX_BUF, bytes))
        return self.__serial.read(bytes)

    def fw_version(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_FW_VERSION, 12))
        return struct.unpack("III", self.__serial.read(12))

    def enable_fb(self, enable):
        self.__serial.write(struct.pack("<BBIH", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_FB_ENABLE, 0, enable))

    def arch_str(self):
        self.__serial.write(struct.pack("<BBI", CameraManager.__USBDBG_CMD, CameraManager.__USBDBG_ARCH_STR, 64))
        return self.__serial.read(64).split('\0', 1)[0]

    def parseBuffer(self, buffer):
        #print(buffer)
        if self.firstPacket:
            self.firstPacket = False
            return True
        try:
            packet = eval(buffer)
        except:
            return False
        
        #print(packet)
        if self.waitingForCycle:
            if 'cam' in packet:
                self.cam = packet['cam']
                self.height = packet['height']
                self.width = packet['width']
                self.fmt = packet['fmt']
                self.timestamp = packet['time']
                self.waitingForCycle = False
                self.data = []
        else:
            packet = eval(buffer)
            if 'end' in packet:
                self.waitingForCycle = True
            else:
                self.data.append(packet)
        return True


    def processData(self):
        endOfPacket = bytes(b'\r\n')
        self.lock.acquire()
        view = memoryview(self.packetBuffer);
        bytesRead = self.tx_buf_len()

        if bytesRead:
            view[self.readIndex:self.readIndex+bytesRead] = self.tx_buf(bytesRead)
            self.readIndex += bytesRead
            parts = self.packetBuffer[0:self.readIndex].partition(endOfPacket)
            self.lock.release()

            while len(parts[1]) > 0:
                self.parseBuffer(parts[0])
                view[0:len(parts[2])] = parts[2]
                self.readIndex = len(parts[2])
                parts = self.packetBuffer[0:self.readIndex].partition(endOfPacket)
        else:
            self.lock.release()

if __name__ == '__main__':
    if len(sys.argv)!= 3:
        print ('usage: pyopenmv.py <port> <script>')
        sys.exit(1)

    with open(sys.argv[2], 'r') as fin:
        buf = fin.read()

##    cam = CameraManager(sys.argv[1])
    cam.stop_script()
    cam.exec_script(buf)
    tx_len = cam.tx_buf_len()
    time.sleep(0.250)
    if (tx_len):
        print(cam.tx_buf(tx_len).decode())
    cam.disconnect()
