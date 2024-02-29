import cv2
import mediapipe as mp
import numpy as np
import time 

def calculateangel(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angel = np.abs(radians * 180.0 / np.pi) 

    if angel > 180.0:
        angel = 360 - angel
    return angel

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

class Squad_couner():
    def __init__(self, thresholds):
        self.thresholds = thresholds
        self.pose = bodyDetector()
        self.body_state = []
        self.Squad_Count = 0
        self.WrongSquad_Count = 0
        self.current_state = ''
        self.Incorrect_Posture = False
        self.msgs = []
    
    def get_state(self, knee_angle):
        state = ''
        if (self.thresholds['HIP_KNEE_VERT']['NORMAL'][0] <= knee_angle <= self.thresholds['HIP_KNEE_VERT']['NORMAL'][1]):
            state = 's1'
        elif (self.thresholds['HIP_KNEE_VERT']['TRANS'][0] <= knee_angle <= self.thresholds['HIP_KNEE_VERT']['TRANS'][1]):
            state = 's2'
        elif (self.thresholds['HIP_KNEE_VERT']['PASS'][0] <= knee_angle <= self.thresholds['HIP_KNEE_VERT']['PASS'][1]):
            state = 's3'
        
        return state
    
    def create_seq(self, state):
        if state == 's2':
            if ((('s3' not in self.body_state) and
                (self.body_state.count('s2')) == 0) or
                    (('s3' in self.body_state) and
                     (self.body_state.count('s2') == 1))):
                self.body_state.append('s2')

        elif state == 's3':
            if ((state not in self.body_state) and
                    's2' in self.body_state):
                self.body_state.append('s3')
    
    def process(self, frame):
        h, w, _ = frame.shape
        self.msgs = []
        
        landmarks = self.pose.prosses(frame)
 
        if landmarks:
            nose = [landmarks[0].x*w, landmarks[0].y*h]
            left_shoulder, left_elbow, left_wrist, left_hip, left_knee, left_ankle, left_foot = [[landmarks[11].x*w, landmarks[11].y*h],
             [landmarks[13].x*w, landmarks[13].y*h],[landmarks[15].x*w, landmarks[15].y*h],[landmarks[23].x*w, landmarks[23].y*h],[landmarks[25].x*w, landmarks[25].y*h],
             [landmarks[27].x*w, landmarks[27].y*h],[landmarks[31].x*w, landmarks[31].y*h]]

            right_shoulder, right_elbow, right_wrist, right_hip, right_knee, right_ankle, right_foot = [[landmarks[12].x*w, landmarks[12].y*h],
             [landmarks[14].x*w, landmarks[14].y*h],[landmarks[16].x*w, landmarks[16].y*h],[landmarks[24].x*w, landmarks[24].y*h],[landmarks[26].x*w, landmarks[26].y*h],
             [landmarks[28].x*w, landmarks[28].y*h],[landmarks[32].x*w, landmarks[32].y*h]]
            
            #محاسبه کدام طرف بودن بدن کاربر
            dist_l_sh_hip = abs(left_foot[1] - left_shoulder[1])
            dist_r_sh_hip = abs(right_foot[1] - right_shoulder[1])
            if dist_l_sh_hip > dist_r_sh_hip:
                shoulder_coord = left_shoulder
                elbow_coord = left_elbow
                wrist_coord = left_wrist
                hip_coord = left_hip
                knee_coord = left_knee
                ankle_coord = left_ankle
                foot_coord = left_foot

                multiplier = -1

            else:
                shoulder_coord = right_shoulder
                elbow_coord = right_elbow
                wrist_coord = right_wrist
                hip_coord = right_hip
                knee_coord = right_knee
                ankle_coord = right_ankle
                foot_coord = right_foot

                multiplier = 1
            #محاسبه زاویه عمودی لگن
            hip_vertical_angle = calculateangel(shoulder_coord, hip_coord, np.array([hip_coord[0], 0]))
            # cv2.ellipse(frame, hip_coord, (30, 30),
            # angle=0, startAngle=-90, endAngle=-90 + multiplier * hip_vertical_angle, thickness=3)
            #
            # محاسبه زاویه عمودی زانو
            # dot = [knee[0], knee[1]- 0.1]
            knee_vertical_angle = calculateangel(hip_coord, knee_coord, np.array([knee_coord[0], 0]))
            # frame = cv2.circle(frame, tuple(np.multiply(dot2, [1280, 720]).astype(int)), 10, (255, 0, 0), -1)
            # print(np.array([knee_coord[0], 0]))
            ankle_vertical_angle = calculateangel(knee_coord, ankle_coord, np.array([ankle_coord[0], 0]))

            current_state = self.get_state(int(knee_vertical_angle))
            # print(hip_coord)
            self.current_state = current_state
            self.create_seq(current_state)
            if current_state == 's1':
                # اگر طول توالی ۳ باشد و وضعیت نادرست نباشد، شمارنده حرکات صحیح را افزایش ده
                if (len(self.body_state) == 3 and not self.Incorrect_Posture):

                    self.Squad_Count += 1

                # اگر 's2' در توالی وضعیت وجود داشته باشد و
                # طول توالی ۱ باشد، شمارنده حرکات نادرست را افزایش ده
                elif ('s2' in self.body_state and len(self.body_state) == 1):

                    self.Squad_Count += 1

                # اگر وضعیت نادرست باشد، شمارنده حرکات نادرست را افزایش ده
                elif self.Incorrect_Posture:
                    self.WrongSquad_Count += 1

                # تنظیمات مربوط به توالی وضعیت را صفر کن
                self.body_state = []
                self.Incorrect_Posture = False

            else:
                if hip_vertical_angle > self.thresholds['HIP_THRESH'][1]:
                    self.msgs.append('کمر خود را کمتر خم کنید')

                # اگر زاویه عمودی  کمتر از حد پایینی
                # تعیین شده باشد و در توالی s2 وجود داشته باشد
                elif (hip_vertical_angle < self.thresholds['HIP_THRESH'][0] and
                        self.self.body_state.count('s2') == 1):

                    self.msgs.append('کمر خود را بیشتر خم کنید')

                # اگر زاویه عمودی زانو در محدوده تعیین شده در توالی s2 باشد
                if (self.thresholds['KNEE_THRESH'][0] < knee_vertical_angle <
                        self.thresholds['KNEE_THRESH'][1] and
                        self.body_state.count('s2') == 1):

                    # self.state_tracker['LOWER_HIPS'] = True
                    pass

                # اگر زاویه عمودی زانو بیشتر از حد تعیین شده باشد
                elif knee_vertical_angle > self.thresholds['KNEE_THRESH'][2]:
                    self.msgs.append('زانو های خود را کمتر خم کنید')
                    self.Incorrect_Posture = True

                # اگر زاویه عمودی مچ پا بیشتر از حد تعیین شده باشد
                # if ankle_vertical_angle > self.thresholds['ANKLE_THRESH']:
                #     self.state_tracker['DISPLAY_TEXT'][2] = True
                #     self.state_tracker['INCORRECT_POSTURE'] = True
            return frame, self.Squad_Count, self.WrongSquad_Count, self.msgs
        else:
            self.body_state = []
            self.current_state = ''
            self.Incorrect_Posture = False
            self.msgs = []

