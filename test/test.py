import cv2
import mediapipe as mp
from main import calculateangel
class bodyDetector():
    def __init__(self, detectionCon=0.5, trackCon=0.5):
        self.mpDrow = mp.solutions.drawing_utils 
        self.mpPose = mp.solutions.pose 
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.pose = mp.solutions.pose.Pose(min_detection_confidence=self.detectionCon, min_tracking_confidence=self.trackCon)

    def prosses(self, img):
        RGBimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        RGBimg.flags.writeable  = False
 
        results = self.pose.process(RGBimg)
        self.mpDrow.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        try:
            return results.pose_landmarks.landmark
        except:
            return None
        
cap = cv2.VideoCapture('plank1.mp4')
a = bodyDetector()

while cap.isOpened():
    ret, frame = cap.read()
    landmarks = a.prosses(frame)
    h, w, _ = frame.shape
    left_shoulder, left_elbow, left_wrist, left_hip, left_knee, left_ankle, left_foot = [[landmarks[11].x*w, landmarks[11].y*h],
             [landmarks[13].x*w, landmarks[13].y*h],[landmarks[15].x*w, landmarks[15].y*h],[landmarks[23].x*w, landmarks[23].y*h],[landmarks[25].x*w, landmarks[25].y*h],
             [landmarks[27].x*w, landmarks[27].y*h],[landmarks[31].x*w, landmarks[31].y*h]]
    print(left_shoulder,left_hip,left_knee)
    print(calculateangel(left_shoulder,left_hip,left_knee))
    
    cv2.imshow('framw', frame)
    if chr(cv2.waitKey(0)) == 'q':
        break
# a.prosses(img)
# cv2.imshow('frame', img)
cv2.waitKey(0)