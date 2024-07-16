from utils import Plank_counter
from utils import get_treshholds_plank_beginner
import cv2

thresh = get_treshholds_plank_beginner()
plank_counter = Plank_counter(thresh)

cap = cv2.VideoCapture('plank1.mp4')

while cap.isOpened():
    ret, frame = cap.read()
    frame,*ex = plank_counter.process(frame)
    print(ex)
    cv2.imshow('frame',frame)
    cv2.waitKey(1)


