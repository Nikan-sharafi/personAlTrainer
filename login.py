import yaml
from yaml.loader import SafeLoader
import streamlit as st
import streamlit_authenticator as stauth



def authenticate():
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
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
    )

    name, state, username = authenticator.login()
    print(name, state, username)
    with st.expander('تنظیمات حساب کاربری'):
        col1, col2, col3 = st.columns(3)

    if not st.session_state["authentication_status"]:
        st.write('حساب کاربری ندرید؟')
        try:
            fields = {'Form name':'ساخت حساب کاربری', 'Email':'ایمیل', 'Username':'نام کاربری', 'Password':'رمز عبور', 'Repeat password':'تکرار رمز عبور', 'Register':'ایجاد حساب کاربری'}
            email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False)
            if email_of_registered_user:
                st.success('حساب کاربری با موفقیت ایجاد شد')
            with open('config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
        except Exception as e:
            st.error(e)

    if st.session_state["authentication_status"]:
    # st.write
        with col1:
            authenticator.logout('خروج از حساب کاربری')
    elif st.session_state["authentication_status"] is False:
        st.error('نام کاربری یا رمز عبور نادرست است')
    elif st.session_state["authentication_status"] is None:
        st.warning('لطفا نام کاربری و پسورد خود را وارد کنید')
        
    if st.session_state["authentication_status"] and col2.button('تغییر رمز عبور'):
        if st.session_state["authentication_status"]:
            try:
                fields = {'Form name':'تغییر رمز عبور', 'Current password':'رمز عبور فعلی', 'New password':'رمز عبور جدید', 'Repeat password': 'تکرار رمز عبور', 'Reset':'تغییر'}
                if authenticator.reset_password(st.session_state["username"], fields = fields):
                    st.success('رمز عبور با موفقیت تغییر یافت')
            except Exception as e:
                st.error(e)

        with open('config.yaml', 'w') as file:
            yaml.dump(config, file, default_flow_style=False)

    if st.session_state["authentication_status"] and col3.button('ویرایش اطلاعات کاربری'):
            try:
                if authenticator.update_user_details(st.session_state["username"]):
                    st.success('اطلاعات با موفقیت ویرایش شد')
            except Exception as e:
                st.error(e)