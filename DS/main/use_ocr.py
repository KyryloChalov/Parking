import cv2
import os
import re
# from keras.models import load_model
# import matplotlib.pyplot as plt
import numpy as np

# from paddleocr import PaddleOCR
from constants import IMAGES, NOT_NUMBER
from functions import *

# Initialize PaddleOCR with English language model
# ocr = PaddleOCR(
#     use_angle_cls=True,
#     lang="en",
#     use_gpu=True,
#     total_process_num=os.cpu_count() * 2 - 1,
#     show_log=False,
# )

# plate_cascade = cv2.CascadeClassifier("../models/haarcascade_ua_license_plate.xml")
print(IMAGES)
print(NOT_NUMBER)
