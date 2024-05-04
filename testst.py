from streamlit_webrtc import webrtc_streamer
import av
import cv2
from main import Squad_couner
def main():
    pr = Squad_couner('مبتدی')
    def video_frame_callback(frame):
        print('resid!')
        
        img = frame.to_ndarray(format="rgb24")  
        print('resid!1')
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        print('resid!2')

        out_frame, correct, incorrect, msgs = pr.process(img) 
        print('resid!3')

        #correct_metric.metric(label="تعداد حرکات درست", value='0')
        #incorrect_metric.metric(label="تعداد حرکات نادرست", value='incorrect')


        # for i in msgs:
        #     messages_metric.markdown("- " + i).
        out_frame = cv2.cvtColor(out_frame, cv2.COLOR_RGB2BGR)
        return av.VideoFrame.from_ndarray( out_frame, format="bgr24")

    webrtc_streamer(
                    key="Squats_pose_analysis",
                    video_frame_callback=video_frame_callback
                )
main()