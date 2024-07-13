import av
import os
import sys
import asyncio
import time
import pandas as pd
import queue
# import threading
import streamlit as st
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer, WebRtcMode
from aiortc.contrib.media import MediaRecorder
from main import Squad_couner, Plank_counter, Pushup_counter, Situp_counter
import cv2
from collections import deque


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
        elif option == 'دراز نشست':
            upload_process_frame = Situp_counter(mode=mode)

        if 'download' not in st.session_state:
            st.session_state['download'] = False

        output_video_file = f'output_live.flv'

        
        def out_recorder_factory() -> MediaRecorder:
            return MediaRecorder(output_video_file)
        result_queue: "queue.Queue[list]" = queue.Queue()

        def video_frame_callback(frame):
            
            img = frame.to_ndarray(format="rgb24")  
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            out_frame, correct, incorrect,sound , msgs = upload_process_frame.process(img) 

            result_queue.put([correct,incorrect,msgs])   
            out_frame = cv2.cvtColor(out_frame, cv2.COLOR_RGB2BGR)
            return av.VideoFrame.from_ndarray(out_frame, format="bgr24")

        col1, col2, col3 = st.columns(3)
        with col1:
            for _ in range(10):
                st.text("")
            # st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
            correct_metric = st.empty()
            st.text("")
            st.text("")
            # st.markdown("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;")
            incorrect_metric = st.empty()
        with col2:
            empty = st.empty
        with col3:
            for _ in range(10):
                st.text("")
            messages_metric = st.empty()
        with col2:        
            ctx = webrtc_streamer(
                            key="Squats-pose-analysis",
                            mode = WebRtcMode.SENDRECV,
                            video_frame_callback=video_frame_callback,
                            # rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
                            media_stream_constraints={"video":  True,"audio": False},
                            video_html_attrs=VideoHTMLAttributes(autoPlay=True, controls=False, muted=False),
                            async_processing=True,
                            out_recorder_factory=out_recorder_factory
                                )
        
        frame_count = 0
        p_msgs = []
        while ctx.state.playing:
            result = result_queue.get()
            # print(result)
            with col1:
                correct_metric.metric(label="تعداد حرکات درست", value=result[0])
                incorrect_metric.metric(label="تعداد حرکات نادرست", value=result[1])
            msgs = result[2]
            # print(msgs)
            if not msgs:
                frame_count += 1
                if frame_count <= 5:
                    msgs = p_msgs
                else:
                    msgs = ['']
            else:
                frame_count = 0
                p_msgs = msgs          
            with col3:
                    
                for i in msgs:
                    messages_metric.markdown("- " + i)

        
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