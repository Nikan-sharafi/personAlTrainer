import av
import os
import sys
import streamlit as st
import cv2
import tempfile
from main import Squad_couner


BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)

def get_thresholds_beginner():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL': (0,  32),
                            'TRANS': (35, 65),
                            'PASS': (70, 95)
                           }
        
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,
                    'HIP_THRESH': [10, 50],
                    'ANKLE_THRESH': 45,
                    'KNEE_THRESH': [50, 70, 95],
                    'OFFSET_THRESH': 35.0,
                    'INACTIVE_THRESH': 15.0,
                    'CNT_FRAME_THRESH': 50
                }
    return thresholds


# برای حالت pro آستانه حرکتی تنظیم می شود
def get_thresholds_pro():

    _ANGLE_HIP_KNEE_VERT = {
                            'NORMAL': (0,  32),
                            'TRANS': (35, 65),
                            'PASS': (80, 95)
                           }
    thresholds = {
                    'HIP_KNEE_VERT': _ANGLE_HIP_KNEE_VERT,
                    'HIP_THRESH': [15, 50],
                    'ANKLE_THRESH': 30,
                    'KNEE_THRESH': [50, 80, 95],
                    'OFFSET_THRESH': 35.0,
                    'INACTIVE_THRESH': 15.0,
                    'CNT_FRAME_THRESH': 50
                 }
    return thresholds

st.title('تمرین دهنده ورزشی: حرکت اسکات')

mode = st.radio('یک گزینه را انتخاب کنید',
                ['مبتدی', 'حرفه‌ای'], horizontal=True)

thresholds = None 

if mode == 'مبتدی':
    thresholds = get_thresholds_beginner()

elif mode == 'حرفه‌ای':
    thresholds = get_thresholds_pro()


upload_process_frame = Squad_couner(thresholds=thresholds)



download = None

if 'download' not in st.session_state:
    st.session_state['download'] = False


output_video_file = f'output_recorded.mp4'

if os.path.exists(output_video_file):
    os.remove(output_video_file)


with st.form('Upload', clear_on_submit=True):
    up_file = st.file_uploader("Upload a Video", ['mp4','mov', 'avi'])
    uploaded = st.form_submit_button("Upload")

stframe = st.empty()

ip_vid_str = ('<p style="font-family:Helvetica; '
              'font-weight: bold; font-size: 16px;">ویدیوی ورودی</p>')
warning_str = ('<p style="font-family:Helvetica; '
               'font-weight: bold; color: Red; '
               'font-size: 17px;">لطفا ابتدا یک فیلم بارگذاری کنید!!!</p>')

warn = st.empty()


download_button = st.empty()

if up_file and uploaded:
    
    download_button.empty()
    tfile = tempfile.NamedTemporaryFile(delete=False)

    try:
        warn.empty()
        tfile.write(up_file.read())

        vf = cv2.VideoCapture(tfile.name)

        # ساخت ویدیو خروجی
        fps = int(vf.get(cv2.CAP_PROP_FPS))
        width = int(vf.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vf.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_size = (width, height)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_output = cv2.VideoWriter(output_video_file, fourcc, fps, frame_size)
        # -----------------------------------------------------------------------
        
        txt = st.sidebar.markdown(ip_vid_str, unsafe_allow_html=True)   
        ip_video = st.sidebar.video(tfile.name)

        col1, col2 = st.columns(2)
        with col1:
            correct_metric = st.empty()
        with col2:
            incorrect_metric = st.empty()
            
        while vf.isOpened():
            ret, frame = vf.read()
            if not ret:
                break

            # تبدیل فریم از BGR به RGB قبل از پردازش.
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out_frame, correct, incorrect, msgs = upload_process_frame.process(frame)
            correct_metric.metric(label="CORRECT", value=correct)
            incorrect_metric.metric(label="INCORRECT", value=incorrect)
            correct_metric.value = correct
            incorrect_metric.value = correct
            
            stframe.image(out_frame)
            video_output.write(out_frame[..., ::-1])

        vf.release()
        video_output.release()
        stframe.empty()
        ip_video.empty()
        txt.empty()
        tfile.close()
    
    except AttributeError:
        warn.markdown(warning_str, unsafe_allow_html=True)   


if os.path.exists(output_video_file):
    with open(output_video_file, 'rb') as op_vid:
        download = download_button.download_button('download',
                                                   data=op_vid, file_name='output_recorded.mp4')
    
    if download:
        st.session_state['download'] = True


if os.path.exists(output_video_file) and st.session_state['download']:
    os.remove(output_video_file)
    st.session_state['download'] = False
    download_button.empty()