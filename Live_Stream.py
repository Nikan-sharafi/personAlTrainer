import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder
from main import Squad_couner
from main import get_thresholds_beginner
from main import get_thresholds_pro

BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
sys.path.append(BASE_DIR)


st.title('تمرین دهنده ورزشی: حرکت اسکات')

mode = st.radio('یک گزینه را انتخاب کنید', ['مبتدی', 'حرفه‌ای'], horizontal=True)

thresholds = None 

if mode == 'مبتدی':
    thresholds = get_thresholds_beginner()

elif mode == 'حرفه‌ای':
    thresholds = get_thresholds_pro()


upload_process_frame = Squad_couner(thresholds=thresholds)


if 'download' not in st.session_state:
    st.session_state['download'] = False

output_video_file = f'output_live.flv'

col1, col2, col3 = st.columns(3)
with col1:
    correct_metric = st.empty()
with col2:
    incorrect_metric = st.empty()
with col3:
    messages_metric = st.empty()
frame_count = 0
p_msgs = []


def video_frame_callback(frame: av.VideoFrame):
    frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
    out_frame, correct, incorrect, msgs = upload_process_frame.process(frame)  # Process frame
    correct_metric.metric(label="تعداد حرکات درست", value=correct)
    incorrect_metric.metric(label="تعداد حرکات نادرست", value=incorrect)

    #نشان دادن طولانی تر پیام ها
    if not msgs:
        frame_count += 1
        if frame_count <= 5:
            msgs = p_msgs
        else:
            msgs = ['']
    else:
        frame_count = 0
        p_msgs = msgs

    for i in msgs:
        messages_metric.markdown("- " + i)
    
    return av.VideoFrame.from_ndarray(frame, format="rgb24")  # Encode and return BGR frame


def out_recorder_factory() -> MediaRecorder:
        return MediaRecorder(output_video_file)


ctx = webrtc_streamer(
                        key="Squats-pose-analysis",
                        video_frame_callback=video_frame_callback,
                        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # Add this config
                        media_stream_constraints={"video": {"width": {'min':480, 'ideal':480}}, "audio": False},
                        video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
                        out_recorder_factory=out_recorder_factory
                    )


download_button = st.empty()

if os.path.exists(output_video_file):
    with open(output_video_file, 'rb') as op_vid:
        download = download_button.download_button('Download Video', data = op_vid, file_name='output_live.flv')

        if download:
            st.session_state['download'] = True



if os.path.exists(output_video_file) and st.session_state['download']:
    os.remove(output_video_file)
    st.session_state['download'] = False
    download_button.empty()


    


