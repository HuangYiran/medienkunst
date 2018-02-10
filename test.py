from StoneFactory import StoneFactory
import cv2
import time
import numpy as np
from Stone import Stone


stone_fact = StoneFactory(500)
stone = stone_fact.create_abs()
mask,_ = stone.get_mask()


cv2.imwrite('./test/mask1.png', mask)
