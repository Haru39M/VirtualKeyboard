import threading
import queue
import cv2

class ThreadedCamera:
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.q = queue.Queue()
        self.running = True
        
    def start(self):
        self.thread = threading.Thread(target=self.update)
        self.thread.start()
        
    def update(self):
        while self.running:
            ret, frame = self.capture.read()
            if not self.q.empty():
                self.q.get()
            self.q.put(frame)
            
    def read(self):
        return self.q.get()
        
    def stop(self):
        self.running = False
        self.thread.join()