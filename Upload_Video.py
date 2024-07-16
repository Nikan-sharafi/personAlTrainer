import av
import os
import sys
import streamlit as st
import cv2
import tempfile
from playsound import playsound
import vlc
from utils import Squad_couner, Plank_counter, Pushup_counter, Situp_counter

def Upload():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lalezar&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap');
        body {
            direction : rtl;
        }
        *,h1,h2,h3,h4,h5,h6 {
            font-family: Vazirmatn, sans-serif;
        }

        </style>
        """,
        unsafe_allow_html=True
    )
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
        
        mode = st.radio('سطح حرکات را انتخاب کنید',
                        ['مبتدی', 'حرفه‌ای'], horizontal=True)

        thresholds = None 

        if option == 'اسکات':
            upload_process_frame = Squad_couner(mode=mode)
            st.markdown(
    """
    <style>
    .st-emotion-cache-1v0mbdj{
        margin: auto;
        width : 20%;
    }
    </style>
    """,
    unsafe_allow_html=True
)
        elif option == 'پلانک':
            upload_process_frame = Plank_counter(mode=mode)
        elif option == 'شنا':
            upload_process_frame = Pushup_counter(mode=mode)
        elif option == 'دراز نشست':
            upload_process_frame = Situp_counter(mode=mode)


        download = None

        if 'download' not in st.session_state:
            st.session_state['download'] = False


        output_video_file = f'output_recorded.mp4'

        if os.path.exists(output_video_file):
            try:
                os.remove(output_video_file)
            except:
                pass


        with st.form('Upload', clear_on_submit=True):
            up_file = st.file_uploader("آپلود ویدیو", ['mp4','mov', 'avi', 'avi', 'asf', 'm4v'])
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
                    
                video_frame = st.empty()
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write('')
                with col2:
                    col11,col12, col13 = st.columns(3)
                    with col11:
                        correct_metric = st.empty()
                    with col12:
                        st.markdown('<h1>/</h1>',unsafe_allow_html=True)
                    with col13:
                        incorrect_metric = st.empty()
                with col3:
                    messages_metric = st.empty()

                frame_count = 0
                p_msgs = []
                
                while vf.isOpened():
                    ret, frame = vf.read()
                    if not ret:
                        break
                    # تبدیل فریم از BGR به RGB قبل از پردازش.
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    out_frame, correct, incorrect, sound , msgs = upload_process_frame.process(frame)
                    if sound == 'correct':
                        p = vlc.MediaPlayer("correct.mp3")
                        p.play()    
                    if sound == 'wrong':
                        p = vlc.MediaPlayer("wrong.mp3")
                        p.play()
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
                
                    with col1:
                        video_frame.image(out_frame)
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
