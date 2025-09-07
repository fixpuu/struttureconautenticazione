import sys, hashlib, time, pandas as pd, streamlit as st
from keyauth import api

# --- PAGE CONFIG ---
st.set_page_config(page_title="🔍 STRUTTURE Premium", layout="wide")
st.markdown("""
<style>
body {background-color: #1a1a1a; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;}
h1 {color: #ff6f61; text-align: center;}
.stButton>button {background-color:#ff6f61; color:white; font-size:16px; font-weight:bold; border-radius:10px;}
.stTextInput>div>div>input {background-color:#2b2b2b; color:white; border-radius:5px; padding:5px;}
</style>
""", unsafe_allow_html=True)

# --- KEYAUTH SETUP ---
def getchecksum():
    md5_hash = hashlib.md5()
    with open(sys.argv[0], "rb") as file:
        md5_hash.update(file.read())
    return md5_hash.hexdigest()

keyauthapp = api(
    name="strutture",
    ownerid="l9G6gNHYVu",
    secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
    version="1.0",
    hash_to_check=getchecksum()
)

# --- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'mode' not in st.session_state:
    st.session_state['mode'] = None  # login / register

# --- SELEZIONE FORM ---
if not st.session_state['authenticated']:
    st.title("🔑 STRUTTURE Premium")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            st.session_state['mode'] = "login"
    with col2:
        if st.button("Registrati"):
            st.session_state['mode'] = "register"

# --- FORM LOGIN / REGISTRAZIONE ---
if st.session_state['mode'] == "login":
    st.subheader("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi")
        if submitted:
            try:
                keyauthapp.login(username, password)  # Login KeyAuth
                st.success(f"Benvenuto {keyauthapp.user_data.username}!")
                st.session_state['authenticated'] = True
            except Exception as e:
                st.error(f"Errore login: {e}")

elif st.session_state['mode'] == "register":
    st.subheader("Registrazione")
    with st.form("register_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        license_key = st.text_input("License Key")
        submitted = st.form_submit_button("Registrati")
        if submitted:
            try:
                keyauthapp.register(username, password, license_key)  # Registrazione KeyAuth
                st.success(f"Registrazione completata! Benvenuto {username}")
                st.session_state['authenticated'] = True
            except Exception as e:
                st.error(f"Errore registrazione: {e}")

# --- ACCESSO AI DATI SOLO SE AUTENTICATO ---
if st.session_state['authenticated']:
    st.success("Accesso riuscito! Caricamento dati…")
    @st.cache_data
    def load_data():
        df = pd.read_csv("STRUTTURE_cleaned.csv")
        time.sleep(1)
        return df
    df = load_data()
    st.dataframe(df)
