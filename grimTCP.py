#!usr/bin/python

import cv2
import cv2.cv as cv
import numpy as np
import socket as sk
import serial
import threading
import time

#Left Wheel
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

def moveReciever():
    print 'setting up wheels'
    motor1 = MotorControllerOne()
    motor2 = MotorControllerTwo()
    motor1.exitSafeStart()
    motor2.exitSafeStart()
    print 'wheels done'


    serverSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    serverSocket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
    serverSocket.bind(('', 6789))
    serverSocket.listen(1)
    print 'Server is ready'

    try:
        while 1:
            print 'Waiting for connection'
            connectionSocket, addr = serverSocket.accept()
            print 'Connected to the move reciever'
            print 'Connected to ', addr
            while 1:
                sentence =connectionSocket.recv(1024)
                print sentence
                if sentence == 'movL':
                    motor1.setSpeed(int(-1000))
                    motor2.setSpeed(int(0))
                elif sentence == 'movR':
                    motor1.setSpeed(int(0))
                    motor2.setSpeed(int(-1000))
                elif sentence == 'movU':
                    motor1.setSpeed(int(-2000))
                    motor2.setSpeed(int(-2000))
                elif sentence == 'movD':
                    motor1.setSpeed(int(0))
                    motor2.setSpeed(int(0))
                else:
                    motor1.setSpeed(int(0))
                    motor2.setSpeed(int(0))
                if sentence == 'end':
                    motor1.close()
                    motor2.close()
                    break
    except KeyboardInterrupt:
        connectionSocket.close()
        serverSocket.close()
        motor1.close()
        motor2.close()

def imgSender():
    serverSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    serverSocket.setsockopt(sk.SOL_SOCKET, sk.SO_REUSEADDR, 1)
    serverSocket.bind(('', 6788))
    serverSocket.listen(1)
    print 'The server is ready'
    print 'setup cameras'
    width = 640
    height = 480

    leftCam = cv2.VideoCapture()
    leftCam.set(3, width)
    leftCam.set(4, height)
    leftCam.set(5, 5)
    leftCam.open(0)


    rightCam = cv2.VideoCapture()
    rightCam.set(3, width)
    rightCam.set(4, height)
    rightCam.set(5, 5)
    rightCam.open(1)

    try:
        while 1:
            print 'Waiting for connection'
            connectionSocket, addr = serverSocket.accept()
            print 'connected to the img sender'
            print 'Connected to ', addr
            while 1:
                #get the webcam imgs
                 sentence = connectionSocket.recv(1024)
                 print sentence
                 if sentence == '200':
                     print 'attempting to read image'
                     try:
                         ret, imgL = leftCam.read();
                     except:
                         ret = False
                     if ret:
                         print 'Got 200, sending img 1'
                         encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
                         result, imagencode = cv2.imencode('.jpg', imgL, encode_param)
                         data = np.array(imagencode)
                         stringData = data.tostring()
                         connectionSocket.send(str(len(stringData)).ljust(16));
                         connectionSocket.send(stringData)
                     else:
                         print ret
                         print 'send 1 failed'
                         connectionSocket.send(str(4).ljust(16))
                         connectionSocket.send('FAIL')
                 elif sentence == '500':
                     print 'Recieved 500: Closing connection'
                     connectionSocket.close()
                     break
                 sentence = connectionSocket.recv(1024)
                 print sentence
                 if sentence == '200':
                     print 'attempting to read image'
                     
                     try:
                         ret, imgR = rightCam.read();
                     except:
                         ret = False
                     if ret:
                         print 'Got 200, sending img 2'
                         encode_param = [int(cv2.IMWRITE_JPEG_QUALITY),90]
                         result, imagencode = cv2.imencode('.jpg', imgR, encode_param)
                         data = np.array(imagencode)
                         stringData = data.tostring()
                         connectionSocket.send(str(len(stringData)).ljust(16));
                         connectionSocket.send(stringData)
                     else:
                         print ret
                         print 'send 2 failed'
                         connectionSocket.send(str(4).ljust(16))
                         connectionSocket.send('FAIL')
                 elif sentence == '500':
                     print 'Recieved 500: Closing connection'
                     connectionSocket.close()
                     break
    except KeyboardInterrupt:
        connectionSocket.close()
        serverSocket.close()

if __name__ == "__main__":
    moveThread = threading.Thread(target=moveReciever)
    moveThread.daemon = True
    moveThread.start()
    
    imgThread = threading.Thread(target=imgSender)
    imgThread.daemon = True
    imgThread.start()
    
    imgThread.join()
    moveThread.join()
