#!/usr/bin/python
import serial
import time
class MotorControllerOne(object):
    def __init__(self, port="/dev/ttyACM0"):
        self.ser=serial.Serial()
        self.ser.port= port
    def exitSafeStart(self):
        command = chr(0x83)
        self.ser.open()
        self.ser.write(command)
        self.ser.flush()
        self.ser.close()
    def setSpeed(self, speed):
        if speed > 0:
            channelByte = chr(0x85)
        else:
            channelByte = chr(0x86)
        lowTargetByte = chr(speed & 0x1F)
        highTargetByte = chr((speed >> 5) & 0x7F)
        command = channelByte + lowTargetByte + highTargetByte
        self.ser.open()
        self.ser.write(command)
        self.ser.flush()
        self.ser.close()
    def reset(self):
        self.ser.reset()
    def close(self):
        self.ser.close()
class MotorControllerTwo(object):
    def __init__(self, port="/dev/ttyACM1"):
        self.ser=serial.Serial()
        self.ser.port = port
    def exitSafeStart(self):
        command = chr(0x83)
        self.ser.open()
        self.ser.write(command)
        self.ser.flush()
        self.ser.close()
    def setSpeed(self, speed):
        if speed > 0:
            channelByte = chr(0x85)
        else:
            channelByte = chr(0x86)
        lowTargetByte = chr(speed & 0x1F)
        highTargetByte = chr((speed >> 5) & 0x7F)
        command = channelByte + lowTargetByte + highTargetByte
        self.ser.open()
        self.ser.write(command)
        self.ser.flush()
        self.ser.close()
    def reset(self):
        self.ser.reset()
    def close(self):
        self.ser.close()

if __name__=="__main__":
    motor1 = MotorControllerOne()
    motor2 = MotorControllerTwo()
    print 'Ports created'
    motor1.exitSafeStart()
    motor2.exitSafeStart()
    print 'SafeStart'
    motor1.setSpeed(int(2000))
    motor2.setSpeed(int(-2000))
    print 'setSpeed'
    time.sleep(.5)
    motor1.setSpeed(int(0))
    motor2.setSpeed(int(0))
    time.sleep(.5)
    print 'at the end'
    motor1.close()
    motor2.close()
    print 'done'
