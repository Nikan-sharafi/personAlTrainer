import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd
import hmac
import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth



def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

def get_connection():
    conn = psycopg2.connect(
        host="localhost",  # Change this to your PostgreSQL host
        database="hamyar_varzeshi",
        user="postgres",  # Change this to your PostgreSQL user
        password="nikan1387"  # Change this to your PostgreSQL password
    )
    return conn

def insert_exercise(user_username, exercise, goal, done):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO exercises (user_username, exercise, goal, done)
            VALUES (%s, %s, %s, %s);
        """, (user_username, exercise, goal, done))
        conn.commit()
    conn.close()

def fetch_exercises(user_username):
    conn = get_connection()
    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
        cursor.execute("SELECT * FROM exercises WHERE user_username = %s;", (user_username,))
        records = cursor.fetchall()
    conn.close()
    return records


def update_exercise(exercise_id, goal, done):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("UPDATE exercises SET goal = %s, done = %s WHERE id = %s;", (goal, done, exercise_id))
        conn.commit()
    conn.close()

def plan():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Lalezar&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@100..900&display=swap');
        body {
            direction : rtl;
        }
        * {
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
    
    if not st.session_state["authentication_status"]:
        st.write('باید وارد حساب کاربری خود شوید')
        st.stop()

    st.markdown(f"<h2 style='text-align: center;font-family: \"Lalezar\", sans-serif;'\
                >اهداف من</br></h2>", unsafe_allow_html=True) 
    
    records = fetch_exercises(username)
    df = pd.DataFrame(records)

    for index, row in df.iterrows():
        move = row['exercise']
        goal = row["goal"]
        done = row["done"]
        if move == 'squat':
            move = 'اسکوات'
        if move == 'plank':
            move = 'پلانک'
        if move == 'pushup':
            move = 'شنا'
        if move == 'situp':
            move = 'دراز نشست'

        progress_text = f'{move} : {goal} / {done}'
        my_bar = st.progress(min(1, done / goal), text=progress_text)
    st.write("")  
    with st.expander('اضافه کردن هدف'):
        st.markdown(f"<h3 style='font-family: \"Lalezar\", sans-serif;'\
                >برای یک حرکت هدف انتخاب کنید</h3>", unsafe_allow_html=True) 
        with st.form(key="exercise_form"):
            user_id = username

            moves = ("اسکات", "پلانک", "شنا", "دراز نشست")
            option = st.selectbox(
                "انتخاب حرکت ورزشی",
                moves,
                index=None,
                placeholder="یک حرکت را انتخاب کنید",
                )
            
            goal = st.number_input("تعاد حرکت", min_value=1, step=1)
            submit_button = st.form_submit_button(label="اضافه کردن هدف")

        if submit_button:
            if option == 'اسکات':
                exercise = 'squat'
            elif option == 'پلانک':
                exercise = 'plank'
            elif option == 'شنا':
                exercise = 'pushup'
            elif option == 'دراز نشست':
                exercise = 'situp'

            insert_exercise(user_id, exercise, goal, 0)
            st.success("هدف با موفقیت اضافه شد")

