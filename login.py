import streamlit as st
from keyauth import api
import hashlib, sys, time

# --- PAGE CONFIG ---
st.set_page_config(page_title="Login STRUTTURE", layout="centered")

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

# --- ANIMATED LOGIN INTERFACE ---
st.markdown("""
    <style>
    .login-container {
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 30px;
        border-radius: 20px;
        box-shadow: 0px 10px 25px rgba(0,0,0,0.3);
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity:0; transform: translateY(-20px);}
        to {opacity:1; transform: translateY(0);}
    }
    .stButton>button {
        margin-right: 10px;
        background: #f6d365;
        color: #000;
        font-weight: bold;
        border-radius: 12px;
        padding: 10px 30px;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        background: #fda085;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="login-container">', unsafe_allow_html=True)
st.title("🔑 Login STRUTTURE Premium")

with st.form("login_form"):
    col1, col2 = st.columns([2,1])
    with col1:
        username = st.text_input("Username")
    with col2:
        password = st.text_input("Password", type="password")
    
    submitted = st.form_submit_button("Accedi")

    if submitted:
        try:
            keyauthapp.login(username, password)
            st.session_state['authenticated'] = True
            st.success("✅ Login effettuato! Caricamento app...")
            time.sleep(0.3)
            # scompare il login e vai all'app
            st.experimental_set_query_params(auth="ok")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"❌ Errore login: {e}")

st.markdown('</div>', unsafe_allow_html=True)
