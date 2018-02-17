import cv2
import time

class TextBoard():

    def __init__(self, bg):
        self.bg = bg
        self.cnt =7 

    def count_down(self):
        self.cnt -= 1
        m, n, _ = self.bg.shape
        m = int(m*3/4)
        n = int(n/2)

        new_bg = self.bg.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(new_bg, str(self.cnt), (n, m), font, 4, (0, 0, 0), 4, cv2.LINE_AA)
        time.sleep(2)
        return new_bg, self.cnt
        



