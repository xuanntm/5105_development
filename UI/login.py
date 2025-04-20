# ✅ login_temp.py (Login UI + Auth microservice)
# Updated with enforced login protection and logout handling

import streamlit as st
import requests
import threading
import time
from flask import Flask, request, jsonify
import psycopg2
import os
import dotenv
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="CTRL+Sustain ESG Dashboard", page_icon="🌱", layout="wide")
# Hide Streamlit's default page navigation (for multi-page apps)
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }
    </style>
""", unsafe_allow_html=True)
# Custom Fonts, Layout, and ESG Background Gradient
st.markdown("""
<style>
    html, body, [class*="css"]  {
        font-family: 'Lato', sans-serif;
        height: 100%;
        margin: 0;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Lato', sans-serif;
        font-weight: bold;
        text-transform: uppercase;
    }
    .ctrl-title {
        font-family: 'Poppins', sans-serif !important;
        font-size: 26px !important;
        font-weight: 700 !important;
        color: #2c3e50 !important;
    }
    .ctrl-caption {
        font-family: 'Poppins', sans-serif !important;
        font-size: 16px !important;
        font-weight: 500 !important;
        color: #4CAF50 !important;
        margin-top: -10px !important;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stApp {
        background: linear-gradient(135deg,#a8e6cf, #cce5ff, #b3b3ff);
        background-size: 180% 180%;
        animation: gradientBG 10s ease infinite;
    }
    @keyframes gradientBG {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 100px;
    }
    .sidebar-center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .centered-subheader {
        text-align: center !important;
        font-size: 30px !important;
        font-family: 'Poppins', sans-serif !important;
    }
    .streamlit-expanderHeader, .stTextInput > div > input, .stPassword > div > input, .stButton > button {
        font-size: 18px !important;
    }
    .stRadio > div[role="radiogroup"] > label {
        font-size: 20px !important;
        font-weight: 600;
        font-family: 'Poppins', sans-serif !important;
        margin-bottom: 8px;
    }
    .button-center {
        display: flex;
        justify-content: center;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------ DB CONNECTION ------------------------ #

DB_URL = os.getenv('DATABASE_URL')
def get_neon_connection():
    return psycopg2.connect(DB_URL)

# ------------------------ AUTH HELPERS ------------------------ #
def user_exists(username):
    with get_neon_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
            return cur.fetchone() is not None

def verify_user(username, password):
    with get_neon_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM users WHERE username = %s AND password = %s", (username, password))
            return cur.fetchone() is not None

def create_user(username, password):
    with get_neon_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                conn.commit()
                return True
            except psycopg2.IntegrityError:
                return False

# ------------------------ FLASK MICRO SERVICE ------------------------ #
app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if verify_user(username, password):
        return jsonify({"status": "success", "message": "Login successful"}), 200
    return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if user_exists(username):
        return jsonify({"status": "fail", "message": "Username already exists"}), 400
    success = create_user(username, password)
    if success:
        return jsonify({"status": "success", "message": "Registration successful"}), 200
    return jsonify({"status": "fail", "message": "Registration failed"}), 500

def run_flask():
    app.run(host="127.0.0.1", port=5000)

threading.Thread(target=run_flask, daemon=True).start()
time.sleep(1)

# ------------------------ STREAMLIT FRONTEND ------------------------ #
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = ""

with st.sidebar:
    st.image("Ctrlsustainlogo.png", width=300)
    menu = st.radio("Login/Register", ["Login", "Register"])

# ------------------------ LOGIN FLOW ------------------------ #
if menu == "Login" and not st.session_state.logged_in:
    st.markdown("<h2 class='centered-subheader'>🔐 Login</h2>", unsafe_allow_html=True)
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    st.markdown("<div class='button-center'>", unsafe_allow_html=True)
    if st.button("Login"):
        res = requests.post("http://127.0.0.1:5000/login", json={"username": username, "password": password})
        if res.status_code == 200:
            st.session_state.logged_in = True
            st.session_state.current_user = username
            st.success("✅ " + res.json().get("message"))
            #st.experimental_rerun()
            st.rerun()
        else:
            st.error("❌ " + res.json().get("message"))
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif menu == "Register" and not st.session_state.logged_in:
    st.markdown("<h2 class='centered-subheader'>📝 Register</h2>", unsafe_allow_html=True)
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    if st.button("Register"):
        res = requests.post("http://127.0.0.1:5000/register", json={"username": new_user, "password": new_pass})
        if res.status_code == 200:
            st.success("✅ " + res.json().get("message"))
        else:
            st.error("❌ " + res.json().get("message"))
# ------------------------ REDIRECT TO HOME ONLY IF LOGGED IN ------------------------ #
if st.session_state.logged_in:
    st.success(f"Welcome, **{st.session_state.current_user}**!")
    st.markdown("""
        <meta http-equiv="refresh" content="0; url=/ESG_GUI_Enhanced_NeonDB" />
    """, unsafe_allow_html=True)
else:
    st.warning("🔒 You must log in to access the ESG Dashboard.")
