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
    def __init__(self, detectionCon=0.7, trackCon=0.7):
        self.mpDrow = mp.solutions.drawing_utils 
        self.mpPose = mp.solutions.pose 
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.pose = mp.solutions.pose.Pose(min_detection_confidence=self.detectionCon, min_tracking_confidence=self.trackCon)

    def prosses(self, img):
        RGBimg = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        RGBimg.flags.writeable  = False
 
        results = self.pose.process(RGBimg)
        # self.mpDrow.draw_landmarks(img, results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)
        try:
            return results.pose_landmarks.landmark
        except:
            return None        


# تنظیم آستانه حرکتی برای مبتدی
def get_thresholds_squat_beginner():

    ANGLE_HIP_KNEE_VERT = {
                            'NORMAL': (0,  32),
                            'TRANS': (35, 65),
                            'PASS': (70, 95)
                           }
        
    thresholds = {
                    'HIP_KNEE_VERT': ANGLE_HIP_KNEE_VERT,
                    'HIP_THRESH': [10, 50],
                    'ANKLE_THRESH': 45,
                    'KNEE_THRESH': [50, 70, 95],
                }
    return thresholds

def get_tresholds_plank_beginner():
    thresholds = {'SHOULDER_HIP_KNEE': [150,200], 'HIP_KNEE_ANKLE': [150, 180]}
    return thresholds

def get_thresholds_pushup_beginner():
    ANGLE_SHOULDER_ELBOW_WRIST = {
                        'NORMAL': (150,  180),
                        'TRANS': (100, 140),
                        'PASS': (50,90)
                        }
    
    thresholds = {
                    'SHOULDER_ELBOW_WRIST': ANGLE_SHOULDER_ELBOW_WRIST,
                    'SHOULDER_HIP_ANKLE': [130, 180],
                    'HIP_KNEE_ANKLE': [150, 180],
                    'WRIST_THRESH': 45,
                }
    return thresholds

def get_thresholds_situp_beginner():

    thresholds = {
                    'SHOULDER_HIP_KNEE': (120, 100),
                    'KNEE_THRESH': 90
                }
    return thresholds

# برای حالت pro آستانه حرکتی تنظیم می شود
def get_thresholds_squat_pro():

    ANGLE_HIP_KNEE_VERT = {
                            'NORMAL': (0,  32),
                            'TRANS': (35, 65),
                            'PASS': (80, 95)
                           }
    thresholds = {
                    'HIP_KNEE_VERT': ANGLE_HIP_KNEE_VERT,
                    'HIP_THRESH': [15, 50],
                    'ANKLE_THRESH': 30,
                    'KNEE_THRESH': [50, 80, 95],
                    'OFFSET_THRESH': 35.0,
                    'INACTIVE_THRESH': 15.0,
                    'CNT_FRAME_THRESH': 50
                 }
    return thresholds

def get_tresholds_plank_pro():
    thresholds = {'SHOULDER_HIP_KNEE' : [160,190], 'HIP_KNEE_ANKLE': [160, 180]}
    return thresholds

def get_thresholds_pushup_pro():
    ANGLE_SHOULDER_ELBOW_WRIST = {
                        'NORMAL': (150,  180),
                        'TRANS': (90, 140),
                        'PASS': (50,80)
                        }
    
    thresholds = {
                    'SHOULDER_ELBOW_WRIST': ANGLE_SHOULDER_ELBOW_WRIST,
                    'SHOULDER_HIP_ANKLE': [150, 180],
                    'HIP_KNEE_ANKLE': [150, 180],
                    'WRIST_THRESH': 45,
                }
    return thresholds

def get_thresholds_situp_pro():
    thresholds = {
                    'SHOULDER_HIP_KNEE': (110, 95),
                    'KNEE_THRESH': 90
                }
    return thresholds

    return thresholds

# تشخیص و شمارش اسکات
class Squad_couner():
    def __init__(self, mode):
        if mode == 'مبتدی':
            self.thresholds = get_thresholds_squat_beginner()
        elif mode == 'حرفه‌ای':
            self.thresholds = get_thresholds_squat_pro()
        self.pose = bodyDetector()
        self.body_state = []
        self.Squad_Count = 0
        self.WrongSquad_Count = 0
        self.current_state = ''
        self.sound = ''
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
    
    def draw(self, frame, start, end, color, draw_start = True, draw_end = True):
        start = (int(start[0]),int(start[1]))
        end = (int(end[0]),int(end[1]))
        if draw_start:
            cv2.circle(frame, start, 6, (0,255,255), -1)
        if draw_end:
            cv2.circle(frame, end, 6, (0,255,255), -1)
            
        cv2.line(frame, start, end, color,3)


    def process(self, frame):
        h, w, _ = frame.shape
        self.msgs = []
        self.sound = ''
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

            # محاسبه زاویه عمودی زانو
            knee_vertical_angle = calculateangel(hip_coord, knee_coord, np.array([knee_coord[0], 0]))
            
            ankle_vertical_angle = calculateangel(knee_coord, ankle_coord, np.array([ankle_coord[0], 0]))
            self.draw(frame, foot_coord, ankle_coord, (255,200,0))
            self.draw(frame, ankle_coord, knee_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, hip_coord, shoulder_coord, (255,200,0))
            
            self.draw(frame, hip_coord,([hip_coord[0], hip_coord[1] - 50]), (255,100,0), draw_end=False)
            self.draw(frame, knee_coord, np.array([knee_coord[0], knee_coord[1]-50]), (255,100,0), draw_end=False)
            
            cv2.ellipse(frame, (int(hip_coord[0]), int(hip_coord[1])), (30, 30),
                        angle=0, startAngle=-90, endAngle=-90 + multiplier * hip_vertical_angle,
                        color=(255, 255, 255), thickness=3, lineType=cv2.LINE_AA)
            cv2.ellipse(frame, (int(knee_coord[0]), int(knee_coord[1])), (20, 20),
                        angle=0, startAngle=-90, endAngle=-90 - multiplier * knee_vertical_angle,
                        color=(255,255,255), thickness=3, lineType=cv2.LINE_AA)
            
            current_state = self.get_state(int(knee_vertical_angle))
            self.current_state = current_state
            self.create_seq(current_state)
            if current_state == 's1':
                # اگر طول توالی ۳ باشد و وضعیت نادرست نباشد، شمارنده حرکات صحیح را افزایش ده
                if (len(self.body_state) == 3 and not self.Incorrect_Posture):

                    self.Squad_Count += 1
                    self.sound = 'correct'

                # اگر 's2' در توالی وضعیت وجود داشته باشد و
                # طول توالی ۱ باشد، شمارنده حرکات نادرست را افزایش ده
                elif ('s2' in self.body_state and len(self.body_state) == 1):

                    self.WrongSquad_Count += 1

                # اگر وضعیت نادرست باشد، شمارنده حرکات نادرست را افزایش ده
                elif self.Incorrect_Posture:
                    self.WrongSquad_Count += 1
                    self.sound = 'wrong'

                # تنظیمات مربوط به توالی وضعیت را صفر کن
                self.body_state = []
                self.Incorrect_Posture = False

            else:
                if hip_vertical_angle > self.thresholds['HIP_THRESH'][1]:
                    self.msgs.append('کمر خود را کمتر خم کنید')

                # اگر زاویه عمودی  کمتر از حد پایینی
                # تعیین شده باشد و در توالی s2 وجود داشته باشد
                elif (hip_vertical_angle < self.thresholds['HIP_THRESH'][0] and
                        self.body_state.count('s2') == 1):

                    self.msgs.append('کمر خود را بیشتر خم کنید')

                # اگر زاویه عمودی زانو بیشتر از حد تعیین شده باشد
                elif knee_vertical_angle > self.thresholds['KNEE_THRESH'][2]:
                    self.msgs.append('زانو های خود را کمتر خم کنید')
                    self.Incorrect_Posture = True

                # اگر زاویه عمودی مچ پا بیشتر از حد تعیین شده باشد
                if ankle_vertical_angle > self.thresholds['ANKLE_THRESH']:
                    self.msgs.append('مچ پا را کمتر خم کنید')
                    self.Incorrect_Posture = True

            return frame, self.Squad_Count, self.WrongSquad_Count,self.sound ,self.msgs
        else:
            self.body_state = []
            self.current_state = ''
            self.Incorrect_Posture = False
            self.msgs = []
            return frame, 0, 0, '', []


# تشخیص و شمارش پلانک
class Plank_counter():
    def __init__(self, mode):
        self.pose = bodyDetector()
        if mode == 'مبتدی':
            self.thresholds = get_tresholds_plank_beginner()
        elif mode == 'حرفه‌ای':
            self.thresholds = get_tresholds_plank_pro()

        self.Plank_Count = 0
        self.WrongPlank_Count = 0
        self.correct_start_time = -1
        self.incorrect_start_time = -1
        self.current_state = ''
        self.Incorrect_Posture = False
        self.msgs = []
        
    def get_state(self, hip_angle):
        isInorrect = True
        if (self.thresholds['SHOULDER_HIP_KNEE'][0] <= hip_angle <= self.thresholds['SHOULDER_HIP_KNEE'][1] and
            self.thresholds['HIP_KNEE_ANKLE'][0] <= hip_angle <= self.thresholds['HIP_KNEE_ANKLE'][1]):
            isInorrect = False
            
        return isInorrect            

    def draw(self, frame, start, end, color, draw_start = True, draw_end = True):
        start = (int(start[0]),int(start[1]))
        end = (int(end[0]),int(end[1]))
        if draw_start:
            cv2.circle(frame, start, 6, (0,255,255), -1)
        if draw_end:
            cv2.circle(frame, end, 6, (0,255,255), -1)
            
        cv2.line(frame, start, end, color,3)

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
            if left_foot[0] > nose[0]:
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

            #محاسبه زاویه لگن
            hip_angle = calculateangel(shoulder_coord, hip_coord, ankle_coord)

            #محاسبه زاویه زانو
            knee_angle = calculateangel(hip_coord, knee_coord, ankle_coord)

            self.draw(frame, foot_coord, ankle_coord, (255,200,0))
            self.draw(frame, ankle_coord, knee_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, hip_coord, shoulder_coord, (255,200,0))
                        
            
            self.Incorrect_Posture = current_state = self.get_state(int(hip_angle))
            
            endTime = time.perf_counter()

            if self.Incorrect_Posture:
                self.correct_start_time = -1
                if self.incorrect_start_time == -1:
                    self.incorrect_start_time = time.perf_counter()
                else:
                    if endTime - self.incorrect_start_time >=1:
                        self.WrongPlank_Count += 1  
                        self.incorrect_start_time = endTime
                self.msgs.append('بدن خود را خم نکنید')
            else:
                self.incorrect_start_time = -1
                if self.correct_start_time == -1:
                    self.correct_start_time = time.perf_counter()
                else:
                    if endTime - self.correct_start_time >=1:
                        self.Plank_Count += 1  
                        self.correct_start_time = endTime



            return frame, self.Plank_Count, self.WrongPlank_Count, '', self.msgs
        else:
            self.body_state = []
            self.current_state = ''
            self.Incorrect_Posture = False
            self.msgs = []
            return frame, 0, 0, []

class Pushup_counter():
    def __init__(self, mode):
        if mode == 'مبتدی':
            self.thresholds = get_thresholds_pushup_beginner()
        elif mode == 'حرفه‌ای':
            self.thresholds = get_thresholds_pushup_pro()
        self.pose = bodyDetector()
        self.body_state = []
        self.Pushup_Count = 0
        self.WrongPushp_Count = 0
        self.current_state = ''
        self.sound = ''
        self.Incorrect_Posture = False
        self.msgs = []
    
    def get_state(self, elbow_angle):
        state = ''
        if (self.thresholds['SHOULDER_ELBOW_WRIST']['NORMAL'][0] <= elbow_angle <= self.thresholds['SHOULDER_ELBOW_WRIST']['NORMAL'][1]):
            state = 's1'
        elif (self.thresholds['SHOULDER_ELBOW_WRIST']['TRANS'][0] <= elbow_angle <= self.thresholds['SHOULDER_ELBOW_WRIST']['TRANS'][1]):
            state = 's2'
        elif (self.thresholds['SHOULDER_ELBOW_WRIST']['PASS'][0] <= elbow_angle <= self.thresholds['SHOULDER_ELBOW_WRIST']['PASS'][1]):
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
    
    def draw(self, frame, start, end, color, draw_start = True, draw_end = True):
        start = (int(start[0]),int(start[1]))
        end = (int(end[0]),int(end[1]))
        if draw_start:
            cv2.circle(frame, start, 6, (0,255,255), -1)
        if draw_end:
            cv2.circle(frame, end, 6, (0,255,255), -1)
            
        cv2.line(frame, start, end, color,3)


    def process(self, frame):
        h, w, _ = frame.shape
        self.msgs = []
        self.sound = ''
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
            if left_foot[0] > nose[0]:
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
            
            # محاسبه زاویه آرنج
            shoulder_elbow_wrist_angle = calculateangel(shoulder_coord, elbow_coord, wrist_coord)
            # محاسبه زاویه زانو
            hip_knee_ankle_angle = calculateangel(hip_coord, knee_coord, ankle_coord)

            #محاسبه زاویه لگن
            shoulder_hip_ankle_angle = calculateangel(shoulder_coord, hip_coord, ankle_coord)
            
            self.draw(frame, foot_coord, ankle_coord, (255,200,0))
            self.draw(frame, ankle_coord, knee_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, hip_coord, shoulder_coord, (255,200,0))
            self.draw(frame, shoulder_coord, elbow_coord, (255,200,0))
            self.draw(frame, elbow_coord, wrist_coord, (255,200,0))

            
            current_state = self.get_state(int(shoulder_elbow_wrist_angle))
            self.current_state = current_state
            self.create_seq(current_state)
            if current_state == 's1':
                # اگر طول توالی ۳ باشد و وضعیت نادرست نباشد، شمارنده حرکات صحیح را افزایش ده
                if (len(self.body_state) == 3 and not self.Incorrect_Posture):
                    self.Pushup_Count += 1
                    self.sound = 'correct'

                # اگر 's2' در توالی وضعیت وجود داشته باشد و
                # طول توالی ۱ باشد، شمارنده حرکات نادرست را افزایش ده
                elif ('s2' in self.body_state and len(self.body_state) == 1):

                    self.WrongPushp_Count += 1
                    self.sound = 'wrong'

                # اگر وضعیت نادرست باشد، شمارنده حرکات نادرست را افزایش ده
                elif self.Incorrect_Posture:
                    self.sound = 'wrong'
                    self.WrongPushp_Count += 1

                # تنظیمات مربوط به توالی وضعیت را صفر کن
                self.body_state = []
                self.Incorrect_Posture = False

            else:
                if not(self.thresholds['SHOULDER_HIP_ANKLE'][0] < shoulder_hip_ankle_angle < self.thresholds['SHOULDER_HIP_ANKLE'][1]):
                    self.msgs.append('کمر خود را خم نکنید')
                    self.Incorrect_Posture = True

                if not(self.thresholds['HIP_KNEE_ANKLE'][0] < hip_knee_ankle_angle < self.thresholds['HIP_KNEE_ANKLE'][1]):
                    self.msgs.append('زانو های خود را خم نکنید')
                    self.Incorrect_Posture = True
                
            return frame, self.Pushup_Count, self.WrongPushp_Count, self.sound, self.msgs
        else:
            self.body_state = []
            self.current_state = ''
            self.Incorrect_Posture = False
            self.msgs = []
            return frame, 0, 0,'', []

class Situp_counter():
    def __init__(self, mode):
        if mode == 'مبتدی':
            self.thresholds = get_thresholds_situp_beginner()
        elif mode == 'حرفه‌ای':
            self.thresholds = get_thresholds_situp_pro()

        self.pose = bodyDetector()
        self.Situp_Count = 0
        self.WrongSitup_Count = 0
        self.current_state = ''
        self.sound = ''
        self.body_state = []
        self.Incorrect_Posture = False
        self.msgs = []
    
    def get_state(self, hip_angle):
        state = ''
        if (self.thresholds['SHOULDER_HIP_KNEE'][0] <= hip_angle):
            state = 's1'
        elif (self.thresholds['SHOULDER_HIP_KNEE'][1] >= hip_angle):
            state = 's2'
        
        return state

    
    def create_seq(self, state):
        if state == 's1' and not('s1' in self.body_state):
            self.body_state.append('s1')

        if state == 's2' and not('s2' in self.body_state):
            self.body_state.append('s2')
    
    def draw(self, frame, start, end, color, draw_start = True, draw_end = True):
        start = (int(start[0]),int(start[1]))
        end = (int(end[0]),int(end[1]))
        if draw_start:
            cv2.circle(frame, start, 6, (0,255,255), -1)
        if draw_end:
            cv2.circle(frame, end, 6, (0,255,255), -1)
            
        cv2.line(frame, start, end, color,3)


    def process(self, frame):
        h, w, _ = frame.shape
        self.msgs = []
        self.sound = ''
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
            if left_foot[0] < nose[0]:
                shoulder_coord = left_shoulder
                elbow_coord = left_elbow
                wrist_coord = left_wrist
                hip_coord = left_hip
                knee_coord = left_knee
                ankle_coord = left_ankle
                foot_coord = left_foot


            else:
                shoulder_coord = right_shoulder
                elbow_coord = right_elbow
                wrist_coord = right_wrist
                hip_coord = right_hip
                knee_coord = right_knee
                ankle_coord = right_ankle
                foot_coord = right_foot
    
            
            # محاسبه زاویه زانو
            hip_knee_ankle_angle = calculateangel(hip_coord, knee_coord, ankle_coord)

            #محاسبه زاویه لگن
            shoulder_hip_knee_angle = calculateangel(knee_coord, hip_coord, shoulder_coord)
            
            self.draw(frame, ankle_coord, knee_coord, (255,200,0))
            self.draw(frame, knee_coord, hip_coord, (255,200,0))
            self.draw(frame, hip_coord, shoulder_coord, (255,200,0))
            
            
            current_state = self.get_state(int(shoulder_hip_knee_angle))
            self.current_state = current_state
            self.create_seq(current_state)

            if self.thresholds['KNEE_THRESH'] < hip_knee_ankle_angle:
                self.msgs.append('زانو خود را باز نکنید')
                self.Incorrect_Posture = True

            # اگر s1 و s2 در توالی حرکت باشد و حرکت نادرست نباشد
            if current_state == 's1' and self.body_state == ['s1','s2']:
                if  not self.Incorrect_Posture:
                    self.Situp_Count += 1
                    self.sound = 'correct'
                else:
                    self.WrongSitup_Count += 1
                    self.sound = 'wrong'
                self.body_state = []

            elif self.body_state == ['s2','s1']:
                self.body_state = []

            # تنظیمات مربوط به نادرست بودن حرکت را صفر کن
            self.Incorrect_Posture = False

            return frame, self.Situp_Count, self.WrongSitup_Count, self.sound, self.msgs
        else:
            self.body_state = []
            self.current_state = ''
            self.Incorrect_Posture = False
            self.msgs = []
            return frame, 0, 0,'', []
