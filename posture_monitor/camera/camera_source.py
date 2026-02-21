import cv2

class CameraSource:
    def __init__(self, index=0, width=320, height=240):
        self.cap = cv2.VideoCapture(index)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
    
    def read(self):
        ret, frame = self.cap.read()
        return ret, cv2.flip(frame, 1)  # Mirror for selfie view
    
    def release(self):
        self.cap.release()
