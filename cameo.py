import cv2

from manager import WindowManager , CaptureManager

class Cameo(object):
    def __init__(self):
        self._windowManager = WindowManager("cameo",self.onKeypress)
        self._captureManager = CaptureManager(cv2.VideoCapture("test3.mp4"), self._windowManager,False)

    def run(self):
        """Run the main loop"""
        self._windowManager.createWindow()
        while self._windowManager.isWindowCreated:
            self._captureManager.enterFrame()
            frame = self._captureManager.frame
            if frame is not None:
                # to DO SOMETHING LEARN IN CHAP 3
                #pass
                self._captureManager.human_detect(frame)
            self._captureManager.exitFrame()
            self._windowManager.processEvents()

    def onKeypress(self,keycode):
        """Handle a keypress
        space -> take a screen shot
        tab -> start/stop screen recording
        escape -> quit
        """
        if keycode == 32: #space
            self._captureManager.writeImage("screenshot.png")
        elif keycode == 9: #tab
            if not self._captureManager.isWritingVideo:
                self._captureManager.startWritingVideo("screencast.avi")

            else:
                self._captureManager.stopWritingVideo()

        elif keycode== 27: #escape
            self._windowManager.destroyWindow()




if __name__=="__main__":
    Cameo().run()
        