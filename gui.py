#!/usr/bin/python
import Tkinter as tk 
from PIL import Image, ImageTk
import cv2
import cv2.cv as cv
import Queue
import threading
import numpy as np
import socket as sk
import time

#Globals
imgSem = threading.BoundedSemaphore(value=1)
imgsChanged = False
imgInL = ""
imgInR = ""

cmdQueue = Queue.Queue()
#stereo = cv2.StereoBM(cv2.STEREO_BM_BASIC_PRESET,ndisparities=16, SADWindowSize=15)
#stereo = cv2.StereoSGBM(0, 16, 7)
#stereo = cv2.StereoSGBM(-64, 192, 5, 5, 5, 4, -64, 1, 150, 2, True)

"""stereo = cv2.StereoSGBM()
stereo.SADWindowSize = 9;
stereo.numberOfDisparities = 96;
stereo.preFilterCap = 63;
stereo.minDisparity = -21;
stereo.uniquenessRatio = 7;
stereo.speckleWindowSize = 0;
stereo.speckleRange = 8;
stereo.disp12MaxDiff = 1;
stereo.fullDP = False;"""

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.grid()
        self.imgL = ImageTk.PhotoImage(Image.open("small.png"))
        self.imgR = ImageTk.PhotoImage(Image.open("small2.png"))
        self.rawL = self.imgL
        self.rawR = self.imgR
        self.cvImgR = ""
        self.cvImgL = ""
        self.showRaw = True
        self.showEdge = False
        self.showDisp = False

        self.Q = cv.Load("Q.xml")
        self.mx1 = np.asarray(cv.Load("mx1.xml"))
        self.my1 = np.asarray(cv.Load("my1.xml"))
        self.mx2 = np.asarray(cv.Load("mx2.xml"))
        self.my2 = np.asarray(cv.Load("my2.xml"))

        self.stereo = cv2.StereoSGBM()
        self.stereo.SADWindowSize = 9;
        self.stereo.numberOfDisparities = 96;
        self.stereo.preFilterCap = 63;
        self.stereo.minDisparity = -21;
        self.stereo.uniquenessRatio = 7;
        self.stereo.speckleWindowSize = 0;
        self.stereo.speckleRange = 8;
        self.stereo.disp12MaxDiff = 1;
        self.stereo.fullDP = False;

        #holder varriables for the sliders
        self.SADWindowSizeScale = 9;
        self.numberOfDisparitiesScale = 96;
        self.preFilterCapScale = 63;
        self.minDisparityScale = -21;
        self.uniquenessRatioScale = 7;
        self.speckleWindowSizeScale = 0;
        self.speckleRangeScale = 8;
        self.disp12MaxDiffScale = 1;
        self.fullDP = False;

        self.createWidgets()

        self.SADWindowSizeSlider.set(self.stereo.SADWindowSize);
        self.numberOfDisparitiesSlider.set(self.stereo.numberOfDisparities);
        self.preFilterCapSlider.set(self.stereo.preFilterCap);
        self.minDisparitySlider.set(self.stereo.minDisparity);
        self.uniquenessRatioSlider.set(self.stereo.uniquenessRatio);
        self.speckleWindowSizeSlider.set(self.stereo.speckleWindowSize);
        self.speckleRangeSlider.set(self.stereo.speckleRange);
        self.disp12MaxDiffSlider.set(self.stereo.disp12MaxDiff);
        
        self.bind("<Up>", self.arwU)
        self.bind("<Down>", self.arwD)
        self.bind("<Left>", self.arwL)
        self.bind("<Right>", self.arwR)
        self.bind("<Button-1>", self.mouseCallback)
        self.bind("<Key>", self.keyCallback)
        self.after(500, self.updateCamera)

    def mouseCallback(self, event):
        print "clicked at", event.x, event.y

    def keyCallback(self, event):
        print "pressed", repr(event.char), event.char
        if event.char == 'q':
            sendCmd("end")

    def arwU(self, event):
        sendCmd("movU")
    def arwD(self, event):
        sendCmd("movD")
    def arwL(self, event):
        sendCmd("movL")
    def arwR(self, event):
        sendCmd("movR")
    
    def createWidgets(self):
	#Row 1
	self.titleText = tk.Label(self, text='The Grim GUI')
	self.titleText.grid(row=1, column=2)
	
	#Row 2	
	self.img1 = tk.Label(self, image=self.imgL)
	self.img1.grid(row=2, column=2)
	self.img2 = tk.Label(self, image=self.imgR)
	self.img2.grid(row=2, column=3)
	
	#Row 3
	self.rawImgBtn = tk.Button(self, text='Raw Imgs', command=self.rawImgBtnCallback)
	self.rawImgBtn.grid(row=3, column=1)

        #Row 4
	self.edgeImgBtn = tk.Button(self, text='Edge Img', command=self.edgeImgBtnCallback)
	self.edgeImgBtn.grid(row=4, column=1)
	
	#Row 5
	self.distanceImgBtn = tk.Button(self, text='Distance Img', command=self.dispImgBtnCallback)
	self.distanceImgBtn.grid(row=5, column=1)
    
	self.upBtn = tk.Button(self, text='up', command=self.moveU)
	self.upBtn.grid(row=5, column=5)
	
	#Row 6
	self.leftBtn = tk.Button(self, text='left', command=self.moveL)
	self.leftBtn.grid(row=6, column=4)
	self.downBtn = tk.Button(self, text='down', command=self.moveD)
	self.downBtn.grid(row=6, column=5)
	self.rightBtn = tk.Button(self, text='right', command=self.moveR)
	self.rightBtn.grid(row=6, column=6)

	self.focus_set() #needed so the arrow keys will bind properly

	#Row 7
	self.SADWindowSizeSlider = tk.Scale(self, from_=1, to=1000, resolution=1,
                                                 label="SADWindowSize", orient=tk.HORIZONTAL,
                                                 variable=self.SADWindowSizeScale)
	self.SADWindowSizeSlider.grid(row=7, column=1)

	self.numberOfDisparitiesSlider = tk.Scale(self, from_=1, to=1600, resolution=16,
                                                 label="numberOfDisparities", orient=tk.HORIZONTAL,
                                                 variable=self.numberOfDisparitiesScale)
	self.numberOfDisparitiesSlider.grid(row=7, column=2)

	self.preFilterCapSlider = tk.Scale(self, from_=0, to=1000, resolution=1,
                                                 label="preFilterCap", orient=tk.HORIZONTAL,
                                                 variable=self.preFilterCapScale)
	self.preFilterCapSlider.grid(row=7, column=3)

	self.minDisparitySlider = tk.Scale(self, from_=-100, to=1000, resolution=1,
                                                 label="minDisparity", orient=tk.HORIZONTAL,
                                                 variable=self.minDisparityScale)
	self.minDisparitySlider.grid(row=7, column=4)

        #Row 8
	self.uniquenessRatioSlider = tk.Scale(self, from_=0, to=1000, resolution=1,
                                                 label="uniquenessRatio", orient=tk.HORIZONTAL,
                                                 variable=self.uniquenessRatioScale)
	self.uniquenessRatioSlider.grid(row=8, column=1)

	self.speckleWindowSizeSlider = tk.Scale(self, from_=0, to=200, resolution=1,
                                                 label="speckleWindowSize", orient=tk.HORIZONTAL,
                                                 variable=self.speckleWindowSizeScale)
	self.speckleWindowSizeSlider.grid(row=8, column=2)

	self.speckleRangeSlider = tk.Scale(self, from_=0, to=1000, resolution=1,
                                                 label="speckleRange", orient=tk.HORIZONTAL,
                                                 variable=self.speckleRangeScale)
	self.speckleRangeSlider.grid(row=8, column=3)

	self.disp12MaxDiffSlider = tk.Scale(self, from_=-1, to=1000, resolution=1,
                                                 label="disp12MaxDiff", orient=tk.HORIZONTAL,
                                                 variable=self.disp12MaxDiffScale)
	self.disp12MaxDiffSlider.grid(row=8, column=4)

    def rawImgBtnCallback(self):
        self.showRaw = True
        self.showEdge = False
        self.showDisp = False

    def edgeImgBtnCallback(self):
        self.showRaw = False
        self.showEdge = True
        self.showDisp = False

    def dispImgBtnCallback(self):
        self.showRaw = False
        self.showEdge = False
        self.showDisp = True

    def updateStereo(self):
        self.stereo.SADWindowSize = self.SADWindowSizeSlider.get();
        self.stereo.numberOfDisparities = self.numberOfDisparitiesSlider.get();
        self.stereo.preFilterCap = self.preFilterCapSlider.get();
        self.stereo.minDisparity = self.minDisparitySlider.get();
        self.stereo.uniquenessRatio = self.uniquenessRatioSlider.get();
        self.stereo.speckleWindowSize = self.speckleWindowSizeSlider.get();
        self.stereo.speckleRange = self.speckleRangeSlider.get();
        self.stereo.disp12MaxDiff = self.disp12MaxDiffSlider.get();
        self.stereo.fullDP = False;

    def loadRawImgs(self):
        imgSem.acquire()
        if imgInL == "":
             imgSem.release()
             return
        self.cvImgL = imgInL
        self.cvImgR = imgInR
        imgSem.release()
        #self.cvImgL = cv2.remap(self.cvImgL, self.mx1, self.my1, cv.CV_INTER_LINEAR)
        #self.cvImgR = cv2.remap(self.cvImgR, self.mx2, self.my2, cv.CV_INTER_LINEAR)
        #self.rawR = ImageTk.PhotoImage(Image.fromarray(self.cvImgR))
        #self.rawL = ImageTk.PhotoImage(Image.fromarray(self.cvImgL))

    def loadEdgeImgs(self):
        if not self.cvImgR == "":
            self.edgeR = ImageTk.PhotoImage(Image.fromarray(cv2.Canny(self.cvImgR, 125, 125)))
            self.edgeL = ImageTk.PhotoImage(Image.fromarray(cv2.Canny(self.cvImgL, 125, 125)))
    
    def loadDistanceImg(self):
        if not self.cvImgR == "":
            temp = self.stereo.compute(cv2.cvtColor(self.cvImgR, cv2.COLOR_BGR2RGB),
                                  cv2.cvtColor(self.cvImgL, cv2.COLOR_BGR2RGB))
            #temp = stereo.compute(self.cvImgL, self.cvImgR)
            #temp = cv2.cvtColor(temp, cv2.COLOR_BGR2RGB)
            self.disMap = ImageTk.PhotoImage(Image.fromarray(temp))
            #temp2 = cv2.normalize(temp, alpha=0, beta=255, norm_type=cv2.cv.CV_MINMAX, dtype=cv2.cv.CV_8U)
            #self.disMap = ImageTk.PhotoImage(Image.fromarray(temp2))
            

    def updateCamera(self):
        self.updateStereo()
        self.loadRawImgs()
        #self.loadEdgeImgs()
        #self.loadDistanceImg()
        if not self.cvImgR == "":
            if self.showRaw == True:
                #self.imgL = self.rawL
                #self.imgR = self.rawR
                cv2.imshow('left', self.cvImgL)
                cv2.imshow('right', self.cvImgR)
            elif self.showEdge == True:
                #self.imgL = self.edgeL
                #self.imgR = self.edgeR
                cv2.imshow('left', cv2.Canny(self.cvImgL, 125, 125))
                cv2.imshow('right', cv2.Canny(self.cvImgR, 125, 125))
            elif self.showDisp == True:
                cv2.imshow('left', self.stereo.compute(self.cvImgR, self.cvImgL))
                cv2.imshow('right', self.cvImgR)
        #self.createWidgets()
        self.after(50, self.updateCamera)

    def moveU(self):
        sendCmd("movU")
    def moveL(self):
        sendCmd("movL")
    def moveD(self):
        sendCmd("movD")
    def moveR(self):
        sendCmd("movR")

def sendCmd(cmd):
    cmdQueue.put(cmd)

def sendCmdThread():
    clientSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    clientSocket.connect(('192.168.1.127', 6789))
    while True:
        while not cmdQueue.empty():
            try:
                # get the msg
                message = cmdQueue.get()
                # send over the internet to The Grim
                print 'sending', message
                clientSocket.send(message)
            except Empty:
                continue


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def recieveImgThread():
    clientSocket = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    clientSocket.connect(('192.168.1.127', 6788))
    try:
        count = 0
        while 1:
            #print 'Sending a 200...'
            time.sleep(.01)
            clientSocket.send('200')
            #print 'rcv length...'
            length = recvall(clientSocket,16)
            if (int(length) > 4):
                print 'rcv img'
                stringData = recvall(clientSocket, int(length))
                data = np.fromstring(stringData, dtype='uint8')
                decimg = cv2.imdecode(data,1)
                count = (count + 1) % 2
                if (count == 0):
                    try:
                        imgSem.acquire()
                        global imgInL
                        imgInL  = decimg
                        imgSem.release()
                        #cv2.imwrite('imgL.jpg', decimg)
                        print 'img 1 written'
                    except:
                        print 'save image 1 failed'
                else:
                    try:
                        imgSem.acquire()
                        global imgInR
                        imgInR = decimg
                        imgSem.release()
                        #cv2.imwrite('imgR.jpg', decimg)
                        print 'img 2 written'
                    except:
                        print 'save image 2 failed'
            else:
                stringData = recvall(clientSocket, int(length))
                if (count == 0):
                    print 'img 1 wasnt taken'
                else:
                    print 'img 2 wasnt taken'
                count = (count + 1) % 2
    except KeyboardInterrupt:
        print '\n^C received, shutting down server'
        sentence = '500'
        clientSocket.send(sentence)
        clientSocket.close()

            
cam = cv2.VideoCapture(1)
cam2 = cv2.VideoCapture(2)

def capImg():
    while True:
        ret, img = cam.read()
        if ret:
            ret2, img2 = cam2.read()
            if ret2:
                return img, img2
	print 'Warming the camera'

if __name__ == "__main__":
    cmdThread = threading.Thread(target=sendCmdThread)
    cmdThread.daemon = True
    cmdThread.start()

    rcvImgThread = threading.Thread(target=recieveImgThread)
    rcvImgThread.daemon = True
    rcvImgThread.start()
   
    app = Application()
    app.master.title('The Grim') 
    app.mainloop()  
