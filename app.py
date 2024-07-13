import streamlit as st 
import hydralit_components as hc
from Upload_Video import Upload
from Live_Stream import Live
from streamlit_webrtc import VideoHTMLAttributes, webrtc_streamer
from aiortc.contrib.media import MediaRecorder
from main import Squad_couner, Plank_counter, Pushup_counter
import av

st.set_page_config(page_title="همیار ورزشی", page_icon="./fitness.ico",layout='wide',initial_sidebar_state='collapsed',)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lalezar&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Vazirmatn&display=swap');

    div {
        font-family: font-family: \"Vazir\", sans-serif; 
    }   
    .row-widget{
        direction: rtl;
    }
    #complexnavbarSupportedContent{
        direction: rtl;
    }
    .nav-link{
        direction: rtl;
    }
    .st-emotion-cache-z5fcl4{
        padding: 2rem 2rem 0rem;
    }
    .st-emotion-cache-1v0mbdj{
        margin: auto;
        width : 50%;
    }
    .css-14rfh7s{
        font-family: font-family: \"Vazir\", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)


menu_data = [
    {'id':'Upload','icon':"⬆️",'label':"آپلود ویدیو⬆️"},
    {'id':'Live','icon':"",'label':"پخش زنده📷️"}
]
over_theme = {'txc_inactive': '#FFFFFF'}

menu_id = hc.nav_bar(
    menu_definition=menu_data,
    override_theme=over_theme,
    home_name='درباره',
    hide_streamlit_markers=False, 
    sticky_nav=True,
    sticky_mode='pinned',
)
selected_nav_item = menu_id

if selected_nav_item == 'Upload':
    Upload()
elif selected_nav_item == 'Live':
    Live()

else:
    st.markdown("<h1 style='text-align: center; font-family: \"Lalezar\", sans-serif;'>درباره</h1>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    # st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif; '>.با استفاده از این برنامه، می تونید حرکات ورزشی خودتون رو اصلاح کرده تعداد حرکات درست رو شمارش کنید</p>", unsafe_allow_html=True)
    # st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>.برای استفاده از برنامه، یک گزینه از نوار بالا انتخاب کنید. برای ویدیو ضبط شده گزینه آپلود ویدیو و برای استفاده از دوربین گزینه پخش زنده</p>", unsafe_allow_html=True)
    # st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>.می توانید با باز کردن نوار سمت چپ حرکت انتخابی خود را عوض کنید</p>", unsafe_allow_html=True)
    # # st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>ساخته شده با ❤️ توسط نیکان شرفی</p>", unsafe_allow_html=True)
    # st.image('fitness2.svg', width=200)
    

    c1,c2 = st.columns([1,2])
    with c2:
        st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif; '>با استفاده از این برنامه، می تونید حرکات ورزشی خودتون رو اصلاح کرده تعداد حرکات درست رو شمارش کنید</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>برای استفاده از برنامه، یک گزینه از نوار بالا انتخاب کنید. برای ویدیو ضبط شده گزینه آپلود ویدیو و برای استفاده از دوربین گزینه پخش زنده</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>می توانید با باز کردن نوار سمت چپ حرکت انتخابی خود را عوض کنید</p>", unsafe_allow_html=True)
    # st.markdown("<p style='text-align: right; font-size: 20px;  font-family: \"Vazir\", sans-serif;'>ساخته شده با ❤️ توسط نیکان شرفی</p>", unsafe_allow_html=True)
    with c1:
        st.image('fitness.svg', width=200)