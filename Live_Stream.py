import av
import os
import sys
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder
from main import Squad_couner, Plank_counter, Pushup_counter
import cv2

def Live():
    BASE_DIR = os.path.abspath(os.path.join(__file__, '../../'))
    sys.path.append(BASE_DIR)

    moves = ("اسکات", "پلانک", "شنا", "دراز نشست")
    title, select = st.empty(), st.empty()

    title.markdown(f"<h1 style='text-align: center;font-family: \"Lalezar\", sans-serif;'\
                   >تمرین دهنده ورزشی</h1>", unsafe_allow_html=True)
    option = select.selectbox(
            "انتخاب حرکت ورزشی",
            moves,
            index=None,
            placeholder="یک حرکت را انتخاب کنید",
            )

    if option:

        select.empty()
        select = st.sidebar.empty()

        option = select.selectbox(
                "انتخاب حرکت ورزشی",
                moves,
                index = moves.index(option),
                placeholder="یک حرکت را انتخاب کنید",
                )

        move = ': حرکت ' + option
        title.markdown(f"<h1 style='text-align: center;font-family: \"Lalezar\", sans-serif;'\
                       >تمرین دهنده ورزشی{move}</h1>", unsafe_allow_html=True)    
        
        mode = st.radio('سطح حرکت را انتخاب کنید', ['مبتدی', 'حرفه‌ای'], horizontal=True)

        thresholds = None 

        if option == 'اسکات':
            upload_process_frame = Squad_couner(mode=mode)
        elif option == 'پلانک':
            upload_process_frame = Plank_counter(mode=mode)
        elif option == 'شنا':
            upload_process_frame = Pushup_counter(mode=mode)

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
        def video_frame_callback(frame):
            print('resid!')
            
            frame = frame.to_ndarray(format="rgb24")  # Decode and get RGB frame
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            out_frame, correct, incorrect, msgs = upload_process_frame.process(frame)  # Process frame

            st.metric(label="تعداد حرکات درست", value=correct)
            st.metric(label="تعداد حرکات نادرست", value=incorrect)

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
               

        # Example usage of webrtc_streamer with the video_frame_callback:
        rtx = webrtc_streamer(
                                key="Squats-pose-analysis",
                                video_frame_callback=video_frame_callback,
                                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},  # Add this config
                                media_stream_constraints={"video": True, "audio": False},
                                video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
                                 async_processing=True,
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