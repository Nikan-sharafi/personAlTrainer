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
        
cap = cv2.VideoCapture('test/situp2.mp4')
a = bodyDetector()

while cap.isOpened():
    ret, frame = cap.read()
    landmarks = a.prosses(frame)
    h, w, _ = frame.shape
    left_shoulder, left_elbow, left_wrist, left_hip, left_knee, left_ankle, left_foot = [[landmarks[11].x*w, landmarks[11].y*h],
             [landmarks[13].x*w, landmarks[13].y*h],[landmarks[15].x*w, landmarks[15].y*h],[landmarks[23].x*w, landmarks[23].y*h],[landmarks[25].x*w, landmarks[25].y*h],
             [landmarks[27].x*w, landmarks[27].y*h],[landmarks[31].x*w, landmarks[31].y*h]]
    
    right_shoulder, right_elbow, right_wrist, right_hip, right_knee, right_ankle, right_foot = [[landmarks[12].x*w, landmarks[12].y*h],
            [landmarks[14].x*w, landmarks[14].y*h],[landmarks[16].x*w, landmarks[16].y*h],[landmarks[24].x*w, landmarks[24].y*h],[landmarks[26].x*w, landmarks[26].y*h],
            [landmarks[28].x*w, landmarks[28].y*h],[landmarks[32].x*w, landmarks[32].y*h]]

    # qqprint(left_shoulder,left_hip,left_knee)
    print(calculateangel(left_knee,left_hip,left_shoulder))
    
    cv2.imshow('framw', frame)
    if chr(cv2.waitKey(0)) == 'q':
        break
# a.prosses(img)
# cv2.imshow('frame', img)
cv2.waitKey(0)