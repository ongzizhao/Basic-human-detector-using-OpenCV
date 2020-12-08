import cv2
import numpy as np
import time

class CaptureManager(object):
    def __init__(self,capture,previewWindowManager= None,shouldMirrorPreivew=False):
        self.previewWindowManager = previewWindowManager
        self.shouldMirrorPreivew = shouldMirrorPreivew
        self._capture= capture
        self._channel=0
        self._enteredFrame = False
        self._frame = None
        self._imageFilename = None
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None
        self._startTime = None
        self._framesElapsed = 0
        self._fpsEstimate=None

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self,value):
        if self._channel != value:
            self._channel = value
            self._frame = None
    
    @property
    def frame(self):
        if self._enteredFrame and self._frame is None:
            _, self._frame =self._capture.retrieve(self.channel) # self._capture.retrieve(self._frame,self.channel)
        return self._frame

    @property
    def isWritingImage(self):
        return self._imageFilename is not None

    @property
    def isWritingVideo(self):
        return self._videoFilename is not None
    
    def enterFrame(self):
        """Capture the next frame if any."""
        # First check if any previous frame was exited. assert not self._enteredFrame 
        if self._capture is not None:
            self._enteredFrame = self._capture.grab() # is only a boolean, require cvs.VideoCapture.retrieve(0 for frame)

    
    def exitFrame(self):
        """Draw to the window. write to the files. release the frame"""
        #check whether grabbed frame is retrievable
        #the getter may retrieve and cache the frame
        if self._frame is None:
            self._enteredFrame = False
            return 
        #update the fps estimate and related variable
        if self._framesElapsed == 0:
            self._startTime = time.time()
        else:
            timeElapsed=time.time() - self._startTime
            self._fpsEstimate = self._framesElapsed / timeElapsed
        self._framesElapsed += 1
        #draw to the window if any
        if self.previewWindowManager is True:
            mirroredFrame= np.fliplr(self._frame)
            self.previewWindowManager.show(mirroredFrame)
        else:
            self.previewWindowManager.show(self._frame)
        #write to the image if any
        if self.isWritingImage:
            cv2.imwrite(self._imageFilename,self._frame)
            self._imageFilename = None
        #write to video file if any
        self._writeVideoFrame()
        #release the frame
        self._frame = None
        self._enteredFrame = False

    def writeImage(self,filename):
        """write the next exited frame to an image file"""
        self._imageFilename = filename

    def startWritingVideo(self,filename,encoding = cv2.VideoWriter_fourcc("M","J","P","G")):
        """Start writing exited frame to a video file"""
        self._videoFilename = filename
        self._videoEncoding = encoding

    def stopWritingVideo(self):
        """stop writing exited frame to video file"""
        self._videoFilename = None
        self._videoEncoding = None
        self._videoWriter = None

    def _writeVideoFrame(self):
        if not self.isWritingVideo: 
            return
        if self._videoWriter is None:
            fps = self._capture.get(cv2.CAP_PROP_FPS)
            if fps <=0.0:
                # the capture fps is unknown so use an estimate
                if self._framesElapsed < 0:
                    #wait for more frames to elapsed so the estimate is more stable
                    return
                else:
                    fps=self._fpsEstimate
            size= (int(self._capture.get(cv2.CAP_PROP_FRAME_WIDTH))) , (int(self._capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))
            self._videoWriter = cv2.VideoWriter(self._videoFilename,self._videoEncoding,fps,size)
        self._videoWriter.write(self._frame
        
        )
    
    def human_detect(self,frame):
        """ Detect human in the frame"""

        def is_inside (i ,o):
            ix,iy,iw,ih= i
            ox,oy,ow,oh = o
            return ix> ox and ix+iw<ox+ow and iy>oy and iy+ih<oy+oh
        
        hog=cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        found_rects,found_weights=hog.detectMultiScale(frame,winStride=(4,4),scale=1.02,finalThreshold=1.9)
        found_rects_filtered=[]
        found_weights_filtered=[]
        for ri,r in enumerate(found_rects):
            for qi , q in enumerate(found_rects):
                if ri!=qi and is_inside(r,q):
                    break
                else:
                    found_rects_filtered.append(r)
                    found_weights_filtered.append(found_weights[ri])

        for ri, r in enumerate(found_rects_filtered):
            x,y,w,h, = r
            cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,255),2)
            text="%.2f" % found_weights_filtered[ri]
            cv2.putText(frame,text,(x,y-20),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)


class WindowManager(object):
    def __init__ (self,windowName,keypressCallback = None):
        self.keypressCallback = keypressCallback
        self._windowName = windowName
        self._isWindowCreated = False

    @property
    def isWindowCreated(self):
        return self._isWindowCreated
    
    def createWindow(self):
        cv2.namedWindow(self._windowName)
        self._isWindowCreated = True

    def show(self,frame):
        cv2.imshow("self._windowName",frame)

    def destroyWindow(self):
        cv2.destroyWindow(self._windowName)
        self._isWindowCreated = False
    
    def processEvents(self):
        keycode=cv2.waitKey(1)
        if self.keypressCallback is not None and keycode != -1:
            self.keypressCallback(keycode)


                    

