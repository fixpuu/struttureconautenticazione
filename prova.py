# prova.py - Versione aggiornata con nuova colonna PRIORITA' e tema scuro
import streamlit as st
import pandas as pd
import time
import sys
import hashlib
import requests
import os
import json
from keyauth import api

# -------------------------
# Config pagina + CSS DARK THEME
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;900&display=swap');
    
    * {
        font-family: 'Inter', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 25%, #0f3460 50%, #533483 75%, #1a1a2e 100%);
        background-size: 400% 400%;
        animation: gradientShift 20s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    h1 {
        background: linear-gradient(135deg, #00d4ff 0%, #00fff9 50%, #ffffff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 900;
        font-size: 3.5rem;
        letter-spacing: -2px;
        margin: 0;
        padding: 1rem 0;
        text-shadow: 0 4px 20px rgba(0,212,255,0.4);
        animation: titleFloat 3s ease-in-out infinite;
    }
    
    @keyframes titleFloat {
        0%, 100% { transform: translateY(0px) scale(1); }
        50% { transform: translateY(-10px) scale(1.02); }
    }
    
    h2 {
        color: #00d4ff;
        font-weight: 700;
        font-size: 1.8rem;
        margin: 0.5rem 0;
        text-shadow: 0 2px 10px rgba(0,212,255,0.3);
    }
    
    h3 {
        color: #00fff9;
        font-weight: 600;
        font-size: 1.3rem;
        margin: 0.3rem 0;
    }
    
    .card {
        background: rgba(26, 26, 46, 0.85);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        padding: 2rem;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,212,255,0.2);
        margin-bottom: 2rem;
        border: 1px solid rgba(0,212,255,0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 30px 80px rgba(0,212,255,0.4);
        border-color: rgba(0,212,255,0.5);
    }
    
    .small-muted {
        color: #94a3b8;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    .user-bubble {
        background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        display: inline-block;
        margin: 0.5rem 0;
        max-width: 85%;
        word-wrap: break-word;
        box-shadow: 0 4px 15px rgba(83, 52, 131, 0.5);
        font-weight: 500;
        animation: slideInRight 0.4s ease;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    .ai-bubble {
        background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%);
        color: #1a1a2e;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        display: inline-block;
        margin: 0.5rem 0;
        max-width: 85%;
        word-wrap: break-word;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.5);
        font-weight: 600;
        animation: slideInLeft 0.4s ease;
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* PRIORITÀ STYLING - Più discrete */
    .priority-1 {
        background: linear-gradient(135deg, rgba(255, 215, 0, 0.25) 0%, rgba(255, 237, 78, 0.25) 100%) !important;
        border-left: 4px solid #ffd700 !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .priority-2 {
        background: linear-gradient(135deg, rgba(192, 192, 192, 0.2) 0%, rgba(232, 232, 232, 0.2) 100%) !important;
        border-left: 4px solid #c0c0c0 !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .priority-3 {
        background: linear-gradient(135deg, rgba(205, 127, 50, 0.2) 0%, rgba(224, 145, 66, 0.2) 100%) !important;
        border-left: 4px solid #cd7f32 !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .priority-4 {
        background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(0,255,249,0.1) 100%) !important;
        border-left: 3px solid rgba(0,212,255,0.5) !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .priority-5 {
        background: rgba(26, 26, 46, 0.3) !important;
        border-left: 2px solid rgba(148, 163, 184, 0.4) !important;
        padding: 0.5rem !important;
        margin: 0.3rem 0 !important;
    }
    
    .delete-row {
        background: linear-gradient(135deg, rgba(255,80,80,0.2) 0%, rgba(255,120,120,0.25) 100%);
        border-left: 4px solid #ff5050;
        padding: 1rem;
        margin: 0.8rem 0;
        border-radius: 12px;
        transition: all 0.3s ease;
        backdrop-filter: blur(10px);
    }
    
    .delete-row:hover {
        background: linear-gradient(135deg, rgba(255,80,80,0.3) 0%, rgba(255,120,120,0.35) 100%);
        transform: translateX(5px);
    }
    
    /* Stili bottoni Streamlit */
    .stButton > button {
        background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
        color: white;
        border: 1px solid rgba(0,212,255,0.3);
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(15, 52, 96, 0.5);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.6);
        border-color: rgba(0,212,255,0.6);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 2px solid rgba(0, 212, 255, 0.3);
        padding: 0.75rem 1rem;
        transition: all 0.3s ease;
        background: rgba(26, 26, 46, 0.8);
        color: #ffffff;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #00d4ff;
        box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.25);
    }
    
    /* Label styling */
    .stTextInput > label,
    .stTextArea > label,
    .stSelectbox > label,
    .stMultiSelect > label,
    .stSlider > label {
        color: #00fff9 !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(26, 26, 46, 0.8);
        color: #ffffff;
        border-color: rgba(0, 212, 255, 0.3);
    }
    
    /* Checkbox styling */
    .stCheckbox {
        padding: 0.5rem;
    }
    
    .stCheckbox > label {
        color: #ffffff !important;
        font-weight: 500 !important;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5);
    }
    
    .stDataFrame td, .stDataFrame th {
        color: #ffffff !important;
        background-color: rgba(26, 26, 46, 0.8) !important;
    }
    
    /* Download button */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%);
        color: #1a1a2e;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 212, 255, 0.5);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(0, 212, 255, 0.7);
    }
    
    /* Slider */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #0f3460 0%, #533483 100%);
    }
    
    /* Success/Error messages */
    .stSuccess {
        background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%);
        border-radius: 12px;
        padding: 1rem;
        color: #1a1a2e;
        font-weight: 700;
    }
    
    .stError {
        background: linear-gradient(135deg, #ff5050 0%, #ff7070 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        font-weight: 600;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
        border-radius: 12px;
        padding: 1rem;
        color: #1a1a2e;
        font-weight: 600;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #0f3460 0%, #533483 100%);
        border-radius: 12px;
        padding: 1rem;
        color: white;
        font-weight: 600;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-top-color: #00d4ff !important;
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .card { 
            padding: 1.5rem; 
            border-radius: 16px;
        }
        h1 { 
            font-size: 2rem; 
            letter-spacing: -1px;
        }
        h2 { font-size: 1.5rem; }
        h3 { font-size: 1.2rem; }
    }
    
    /* Animazione di entrata per le card */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .card {
        animation: fadeInUp 0.6s ease;
    }
    
    /* Badge priorità nella tabella */
    .priority-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        margin: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Auth helpers + Remember Me
# -------------------------

REMEMBER_FILE = ".auth_remember.json"

def save_remember_me(username, password):
    """Salva credenziali in modo sicuro per ricordami"""
    try:
        data = {
            "username": username,
            "password_hash": hashlib.sha256(password.encode()).hexdigest()
        }
        with open(REMEMBER_FILE, "w") as f:
            json.dump(data, f)
        return True
    except Exception:
        return False

def load_remember_me():
    """Carica credenziali salvate"""
    try:
        if os.path.exists(REMEMBER_FILE):
            with open(REMEMBER_FILE, "r") as f:
                data = json.load(f)
            return data.get("username"), data.get("password_hash")
    except Exception:
        pass
    return None, None

def clear_remember_me():
    """Cancella credenziali salvate"""
    try:
        if os.path.exists(REMEMBER_FILE):
            os.remove(REMEMBER_FILE)
    except Exception:
        pass

def safe_checksum():
    """Calcola checksum del file corrente in modo sicuro."""
    try:
        if hasattr(sys.modules[__name__], '__file__'):
            file_path = sys.modules[__name__].__file__
        else:
            file_path = sys.argv[0]
        
        if os.path.exists(file_path):
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                md5_hash.update(f.read())
            return md5_hash.hexdigest()
    except Exception:
        pass
    return None

def initialize_auth():
    """Inizializza sistema di autenticazione con gestione errori migliorata."""
    original_exit = sys.exit
    original_os_exit = os._exit
    
    def mock_exit(code=0):
        raise SystemExit(code)
    
    def mock_os_exit(code=0):
        raise SystemExit(code)
    
    sys.exit = mock_exit
    os._exit = mock_os_exit
    
    try:
        try:
            name = st.secrets["KEYAUTH_NAME"]
            ownerid = st.secrets["KEYAUTH_OWNERID"] 
            secret = st.secrets["KEYAUTH_SECRET"]
            version = st.secrets["KEYAUTH_VERSION"]
        except KeyError:
            name = "strutture"
            ownerid = "l9G6gNHYVu"  
            secret = "8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1"
            version = "1.0"

        checksum = safe_checksum()
        
        if checksum:
            auth_app = api(name, ownerid, secret, version, checksum)
        else:
            auth_app = api(name, ownerid, secret, version, "")
        
        sys.exit = original_exit
        os._exit = original_os_exit
        
        return auth_app, None
        
    except SystemExit:
        sys.exit = original_exit
        os._exit = original_os_exit
        return None, "Errore inizializzazione: verifica configurazione KeyAuth"
        
    except Exception as e:
        sys.exit = original_exit
        os._exit = original_os_exit
        
        error_msg = str(e)
        
        if "doesn't exist" in error_msg:
            error_msg = "Servizio di autenticazione non disponibile."
        elif "invalidver" in error_msg:
            error_msg = "Versione non compatibile. Aggiorna l'applicazione."
        elif "hash" in error_msg.lower():
            error_msg = "Errore di verifica integrità."
        elif "timeout" in error_msg.lower():
            error_msg = "Timeout di connessione. Riprova."
        else:
            error_msg = f"Errore di connessione: {error_msg}"
        
        return None, error_msg

# -------------------------
# Session state init
# -------------------------
if "auth_app" not in st.session_state:
    st.session_state["auth_app"] = None
    st.session_state["auth_error"] = None

if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "login_error" not in st.session_state:
    st.session_state["login_error"] = None
if "show_add_form" not in st.session_state:
    st.session_state["show_add_form"] = False
if "show_delete_form" not in st.session_state:
    st.session_state["show_delete_form"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []
if "login_attempt" not in st.session_state:
    st.session_state["login_attempt"] = 0
if "auto_login_tried" not in st.session_state:
    st.session_state["auto_login_tried"] = False
if "saved_password" not in st.session_state:
    st.session_state["saved_password"] = None

# -------------------------
# Data functions
# -------------------------
@st.cache_data
def load_data(path="STRUTTURE (1).csv"):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Errore lettura CSV '{path}': {e}")
        return None

def save_data(df, path="STRUTTURE (1).csv"):
    try:
        df.to_csv(path, index=False)
        return True
    except Exception as e:
        st.error(f"Errore salvataggio CSV: {e}")
        return False

# -------------------------
# Login UI migliorato con Ricordami
# -------------------------

def perform_login(username, password, remember=False):
    """Esegue il login in modo sicuro senza far terminare l'app."""
    try:
        auth_app = st.session_state["auth_app"]
        
        if auth_app is None:
            st.session_state["login_error"] = "Sistema di autenticazione non inizializzato"
            return False

        original_exit = sys.exit
        original_os_exit = os._exit
        original_time_sleep = time.sleep

        def mock_exit(code=0):
            raise SystemExit(code)

        def mock_os_exit(code=0):
            raise SystemExit(code)
        
        def mock_sleep(seconds):
            pass

        sys.exit = mock_exit
        os._exit = mock_os_exit
        time.sleep = mock_sleep

        try:
            auth_app.login(username, password)
            st.session_state["auth"] = True
            st.session_state["user"] = username
            st.session_state["login_error"] = None
            
            if remember:
                save_remember_me(username, password)
                st.session_state["saved_password"] = password
            else:
                clear_remember_me()
                st.session_state["saved_password"] = None
            
            return True

        except SystemExit:
            st.session_state["auth"] = False
            st.session_state["login_error"] = "Credenziali non valide o account scaduto."
            clear_remember_me()
            st.session_state["saved_password"] = None
            return False

        except BaseException as e:
            st.session_state["auth"] = False
            st.session_state["login_error"] = f"Errore autenticazione: {str(e)}"
            clear_remember_me()
            st.session_state["saved_password"] = None
            return False

        finally:
            sys.exit = original_exit
            os._exit = original_os_exit
            time.sleep = original_time_sleep

    except Exception as e:
        msg = str(e)
        if "invalid" in msg.lower():
            msg = "Username o password non corretti."
        elif "hwid" in msg.lower():
            msg = "Dispositivo non riconosciuto."
        elif "banned" in msg.lower():
            msg = "Account sospeso."
        elif "expired" in msg.lower():
            msg = "Accesso scaduto."
        else:
            msg = f"Errore: {msg}"

        st.session_state["auth"] = False
        st.session_state["login_error"] = msg
        clear_remember_me()
        st.session_state["saved_password"] = None
        return False

def show_login():
    st.markdown("<div style='text-align: center; padding: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("<h1>🏔️ STRUTTURE</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: rgba(0,255,249,0.95); font-size: 1.2rem; font-weight: 500; text-shadow: 0 2px 10px rgba(0,212,255,0.5);'>Sistema di gestione dati sci di fondo</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='card' style='max-width: 500px; margin: 0 auto;'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00d4ff; text-align: center; margin-bottom: 1rem;'>🔐 Accesso</h2>", unsafe_allow_html=True)
    
    if st.session_state["auth_app"] is None:
        with st.spinner("Inizializzazione in corso..."):
            app, error = initialize_auth()
            st.session_state["auth_app"] = app
            st.session_state["auth_error"] = error
    
    if st.session_state["auth_error"]:
        st.markdown(f"<div style='background: linear-gradient(135deg, #ff5050 0%, #ff7070 100%); padding: 1rem; border-radius: 12px; color: white; font-weight: 600; text-align: center; margin: 1rem 0;'>❌ {st.session_state['auth_error']}</div>", unsafe_allow_html=True)
        
        if st.button("🔄 Riprova connessione", key="retry_conn"):
            st.session_state["auth_app"] = None
            st.session_state["auth_error"] = None
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    
    # Auto-login se credenziali salvate
    if not st.session_state["auto_login_tried"]:
        st.session_state["auto_login_tried"] = True
        saved_user, saved_pass_hash = load_remember_me()
        
        if saved_user and saved_pass_hash and st.session_state["saved_password"]:
            with st.spinner(f"Accesso automatico per {saved_user}..."):
                success = perform_login(saved_user, st.session_state["saved_password"], remember=True)
                
            if success:
                st.success("✅ Accesso automatico riuscito!")
                time.sleep(0.5)
                st.rerun()
    
    st.markdown("### Inserisci le tue credenziali:")
    
    saved_user, _ = load_remember_me()
    default_username = saved_user if saved_user else ""
    
    username = st.text_input("👤 Username", value=default_username, key=f"login_username_{st.session_state['login_attempt']}")
    password = st.text_input("🔑 Password", type="password", key=f"login_password_{st.session_state['login_attempt']}")
    
    remember_me = st.checkbox("🔐 Ricordami su questo dispositivo", value=bool(saved_user))
    
    login_clicked = st.button("🔐 Accedi", key=f"login_btn_{st.session_state['login_attempt']}", use_container_width=True)
    
    if login_clicked and username and password:
        with st.spinner("Verifica credenziali..."):
            success = perform_login(username, password, remember_me)
            
        if success:
            st.success("✅ Accesso eseguito con successo!")
            time.sleep(0.5)
            st.rerun()
        else:
            st.session_state["login_attempt"] += 1
            st.rerun()
    
    if st.session_state.get("login_error"):
        st.markdown(f"<div style='background: linear-gradient(135deg, #ff5050 0%, #ff7070 100%); padding: 1rem; border-radius: 12px; color: white; font-weight: 600; text-align: center; margin: 1rem 0;'>❌ {st.session_state['login_error']}</div>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #94a3b8;'>💡 Verifica le credenziali e riprova.</p>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Chat AI
# -------------------------

def call_groq_chat(messages, max_tokens=400):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("API key AI non trovata.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": max_tokens,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Errore di rete: {e}")

    if r.status_code == 200:
        j = r.json()
        if "choices" in j and len(j["choices"]) > 0 and "message" in j["choices"][0]:
            return j["choices"][0]["message"]["content"]
        return j.get("message") or str(j)
    else:
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise RuntimeError(f"Errore AI ({r.status_code}): {err}")

def summarise_dataframe_for_ai(df):
    try:
        parts = []
        parts.append(f"Righe totali: {len(df)}")
        cols = list(df.columns)
        parts.append(f"Colonne: {', '.join(cols)}")

        def find_col(possibles):
            for p in possibles:
                for c in df.columns:
                    if p.lower() in c.lower():
                        return c
            return None

        col_data = find_col(["data"])
        col_luogo = find_col(["luogo", "localita"])
        col_cons = find_col(["considerazione", "note", "commento"])
        col_prior = find_col(["priorita", "priority"])

        if col_data:
            try:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
                min_d = df[col_data].min()
                max_d = df[col_data].max()
                parts.append(f"Date: da {min_d} a {max_d}")
            except Exception:
                pass

        if col_luogo:
            try:
                top_luoghi = df[col_luogo].dropna().astype(str).value_counts().head(6)
                parts.append("Top località: " + "; ".join([f"{i} ({int(v)})" for i, v in top_luoghi.items()]))
            except Exception:
                pass

        if col_prior:
            try:
                prior_counts = df[col_prior].value_counts()
                parts.append(f"Priorità: {dict(prior_counts)}")
            except Exception:
                pass

        numeric_fields = []
        for c in df.columns:
            try:
                s = pd.to_numeric(df[c], errors="coerce")
                if s.notna().sum() > 0:
                    numeric_fields.append(c)
            except Exception:
                pass
        numeric_fields = numeric_fields[:6]
        for c in numeric_fields:
            s = pd.to_numeric(df[c], errors="coerce")
            parts.append(f"{c}: min={s.min()} median={s.median()} mean={round(s.mean(),2) if s.notna().sum()>0 else 'NA'} max={s.max()}")

        if col_cons:
            examples = df[col_cons].dropna().astype(str).head(6).tolist()
            if examples:
                parts.append("Esempi note: " + " | ".join(examples))

        try:
            excerpt = df.head(25).to_csv(index=False)
            if len(excerpt) > 3000:
                excerpt = excerpt[:3000] + "\n..."
            parts.append("Estratto CSV:\n" + excerpt)
        except Exception:
            pass

        return "\n".join(parts)
    except Exception:
        return "Impossibile creare sommario."

def chat_ai_box(df_context):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00d4ff; margin-bottom: 0.5rem;'>🤖 Consulenza AI</h2>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted' style='margin-bottom: 1.5rem;'>Fai domande sui dati filtrati e ricevi consigli intelligenti.</div>", unsafe_allow_html=True)

    for role, text in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"<div class='user-bubble'>👤 {st.session_state.get('user','Tu')}: {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>🤖 AI: {text}</div>", unsafe_allow_html=True)

    user_q = st.text_area("💬 Scrivi la tua domanda", key="chat_input", height=90)
    
    col1, col2 = st.columns([1,1])
    with col1:
        send_clicked = st.button("Invia alla AI", key="send_ai")
    with col2:
        reset_clicked = st.button("🔄 Reset chat", key="reset_chat")

    if reset_clicked:
        st.session_state["chat_history"] = []
        st.rerun()

    if send_clicked and user_q and user_q.strip():
        try:
            st.session_state["chat_history"].append(("user", user_q))

            system_prompt = (
                "Sei un assistente esperto per sci di fondo. "
                "Rispondi in italiano in modo conciso e pratico, fornendo consigli tecnici basati sui dati."
            )

            summary = summarise_dataframe_for_ai(df_context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Dati disponibili:\n{summary}"}
            ]

            for role, text in st.session_state["chat_history"]:
                messages.append({"role": "user" if role == "user" else "assistant", "content": text})

            with st.spinner("L'AI sta elaborando..."):
                ai_text = call_groq_chat(messages, max_tokens=500)

            st.session_state["chat_history"].append(("assistant", ai_text))
            st.rerun()
            
        except Exception as e:
            st.error("Errore AI: " + str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Delete rows UI
# -------------------------

def show_delete_interface(df):
    """Interfaccia per eliminare righe"""
    st.markdown("<h2 style='color: #ff5050; margin-bottom: 0.5rem;'>🗑️ Elimina righe</h2>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted' style='margin-bottom: 1.5rem;'>Seleziona le righe da eliminare. Le più recenti sono mostrate per prime.</div>", unsafe_allow_html=True)
    
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None
    
    col_data = find_col(["data"])
    
    df_display = df.copy()
    if col_data:
        try:
            df_display[col_data] = pd.to_datetime(df_display[col_data], errors="coerce")
            df_display = df_display.sort_values(by=col_data, ascending=False, na_position='last')
        except Exception:
            pass
    
    df_recent = df_display.head(50).reset_index(drop=True)
    
    st.info(f"📊 Visualizzazione delle ultime **{len(df_recent)}** righe (su {len(df)} totali)")
    
    if len(df_recent) > 0:
        preview_data = []
        for idx in df_recent.index:
            row = df_recent.iloc[idx]
            
            preview = []
            for col in df_recent.columns[:5]:
                val = row[col]
                if pd.notna(val) and str(val).strip():
                    preview.append(f"{col}: {str(val)[:30]}")
            
            preview_text = " | ".join(preview) if preview else f"Riga {idx}"
            preview_data.append({
                "index": idx,
                "preview": preview_text,
                "original_index": df_recent.index[idx]
            })
        
        st.markdown("### Seleziona righe da eliminare:")
        rows_to_delete = []
        
        for item in preview_data[:20]:
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                selected = st.checkbox("", key=f"del_{item['index']}", label_visibility="collapsed")
            with col2:
                st.markdown(f"<div class='delete-row'>**Riga {item['index']}**: {item['preview']}</div>", unsafe_allow_html=True)
            
            if selected:
                rows_to_delete.append(item['index'])
        
        if rows_to_delete:
            st.warning(f"⚠️ Stai per eliminare **{len(rows_to_delete)}** riga/e")
            
            col_del, col_cancel = st.columns([1, 1])
            with col_del:
                if st.button("🗑️ Conferma eliminazione", type="primary", key="confirm_delete"):
                    try:
                        indices_to_keep = [i for i in df.index if i not in [df_recent.index[idx] for idx in rows_to_delete]]
                        df_new = df.loc[indices_to_keep].reset_index(drop=True)
                        
                        if save_data(df_new):
                            st.success(f"✅ Eliminate {len(rows_to_delete)} riga/e!")
                            try:
                                st.cache_data.clear()
                            except Exception:
                                pass
                            time.sleep(1)
                            st.session_state["show_delete_form"] = False
                            st.rerun()
                        else:
                            st.error("❌ Errore salvataggio")
                    except Exception as e:
                        st.error(f"❌ Errore: {e}")
            
            with col_cancel:
                if st.button("❌ Annulla", key="cancel_delete"):
                    st.session_state["show_delete_form"] = False
                    st.rerun()
        else:
            if st.button("❌ Chiudi", key="close_delete"):
                st.session_state["show_delete_form"] = False
                st.rerun()
    else:
        st.warning("Nessuna riga disponibile")
        if st.button("❌ Chiudi", key="close_delete_empty"):
            st.session_state["show_delete_form"] = False
            st.rerun()

# -------------------------
# Funzione per formattare DataFrame con priorità
# -------------------------

def format_dataframe_with_priority(df):
    """Formatta il DataFrame evidenziando le righe per priorità"""
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None
    
    col_prior = find_col(["priorita", "priority"])
    
    if col_prior and col_prior in df.columns:
        # Ordina per priorità
        df_sorted = df.copy()
        df_sorted[col_prior] = pd.to_numeric(df_sorted[col_prior], errors='coerce')
        df_sorted = df_sorted.sort_values(by=col_prior, na_position='last')
        
        return df_sorted
    
    return df

def display_priority_dataframe(df):
    """Visualizza DataFrame con evidenziazione priorità"""
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None
    
    col_prior = find_col(["priorita", "priority"])
    
    if col_prior and col_prior in df.columns:
        st.markdown("""
        <div style='margin: 1rem 0; padding: 1rem; background: rgba(0,212,255,0.1); border-radius: 12px; border: 1px solid rgba(0,212,255,0.3);'>
            <h4 style='color: #00d4ff; margin: 0 0 0.5rem 0;'>🏆 Legenda Priorità:</h4>
            <div style='display: flex; gap: 1rem; flex-wrap: wrap;'>
                <span class='priority-badge priority-1'>🥇 Priorità 1 - PRIMA SCELTA</span>
                <span class='priority-badge priority-2'>🥈 Priorità 2 - Seconda scelta</span>
                <span class='priority-badge priority-3'>🥉 Priorità 3 - Terza scelta</span>
                <span class='priority-badge priority-4'>4️⃣ Priorità 4</span>
                <span class='priority-badge priority-5'>5️⃣ Priorità 5+</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ordina per priorità
        df_display = df.copy()
        df_display[col_prior] = pd.to_numeric(df_display[col_prior], errors='coerce')
        df_display = df_display.sort_values(by=col_prior, na_position='last')
        
        # Mostra per gruppi di priorità
        for priority in [1, 2, 3, 4, 5]:
            priority_rows = df_display[df_display[col_prior] == priority]
            
            if len(priority_rows) > 0:
                emoji_map = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣"}
                priority_class = f"priority-{priority}"
                
                st.markdown(f"""
                <div class='{priority_class}' style='padding: 1rem; margin: 1rem 0; border-radius: 16px;'>
                    <h3 style='margin: 0 0 1rem 0;'>{emoji_map.get(priority, '')} PRIORITÀ {priority} - {len(priority_rows)} risultati</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(priority_rows, use_container_width=True, height=min(400, len(priority_rows) * 35 + 50))
        
        # Righe senza priorità
        no_priority = df_display[df_display[col_prior].isna()]
        if len(no_priority) > 0:
            st.markdown("""
            <div style='padding: 1rem; margin: 1rem 0; border-radius: 16px; background: rgba(148, 163, 184, 0.1); border: 1px solid rgba(148, 163, 184, 0.3);'>
                <h3 style='margin: 0 0 1rem 0; color: #94a3b8;'>📝 Senza Priorità - {} risultati</h3>
            </div>
            """.format(len(no_priority)), unsafe_allow_html=True)
            
            st.dataframe(no_priority, use_container_width=True, height=min(400, len(no_priority) * 35 + 50))
    else:
        st.dataframe(df, use_container_width=True, height=500)

# -------------------------
# Main app
# -------------------------

def main_app():
    try:
        # Header con animazione
        st.markdown("""
            <div style='text-align:center; padding: 1rem 0; margin-bottom: 2rem;'>
                <h1 style='margin-bottom: 0.5rem;'>🏔️ STRUTTURE Dashboard</h1>
                <p style='color: rgba(0,255,249,0.98); font-size: 1.1rem; font-weight: 500; text-shadow: 0 2px 10px rgba(0,212,255,0.4); margin: 0;'>
                    Benvenuto, <strong style='font-weight: 700; color: #00d4ff;'>{}</strong> 
                    <span style='display: inline-block; animation: wave 2s ease-in-out infinite;'>👋</span>
                </p>
            </div>
            <style>
                @keyframes wave {{
                    0%, 100% {{ transform: rotate(0deg); }}
                    25% {{ transform: rotate(20deg); }}
                    75% {{ transform: rotate(-20deg); }}
                }}
            </style>
        """.format(st.session_state.get('user','utente')), unsafe_allow_html=True)

        col_l, col_r = st.columns([9,1])
        with col_r:
            if st.button("👋 Logout", key="logout_btn"):
                st.session_state["auth"] = False
                st.session_state["user"] = None
                st.session_state["auth_app"] = None
                st.session_state["login_attempt"] = 0
                st.session_state["saved_password"] = None
                clear_remember_me()
                st.rerun()

        df = load_data()
        if df is None:
            st.markdown("<div style='background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%); padding: 1.5rem; border-radius: 12px; color: #1a1a2e; font-weight: 700; text-align: center;'>📊 Nessun dataset disponibile. Carica STRUTTURE (1).csv</div>", unsafe_allow_html=True)
            st.stop()

        # Pulizia colonne non necessarie
        drop_cols = ["luogo_clean", "tipo_neve_clean", "hum_inizio_sospetto", "hum_fine_sospetto"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")

        def find_col(possibles):
            for p in possibles:
                for c in df.columns:
                    if p.lower() in c.lower():
                        return c
            return None

        col_data = find_col(["data"])
        col_luogo = find_col(["luogo", "localita"])
        col_neve = find_col(["tipo_neve", "neve"])
        col_cons = find_col(["considerazione", "note", "commento"])
        col_prior = find_col(["priorita", "priority"])
        col_temp = [c for c in df.columns if "temp" in c.lower()]
        col_hum = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower() or ("um" in c.lower() and "%" in c)]

        if col_data:
            try:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date
            except Exception:
                pass

        # --- Gestione dati ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00d4ff; margin-bottom: 1.5rem;'>✨ Gestione dati</h2>", unsafe_allow_html=True)
        
        col_add_btn, col_del_btn = st.columns([1, 1])
        
        with col_add_btn:
            if not st.session_state["show_add_form"]:
                if st.button("➕ Aggiungi riga", key="show_add", use_container_width=True):
                    st.session_state["show_add_form"] = True
                    st.session_state["show_delete_form"] = False
                    st.rerun()
        
        with col_del_btn:
            if not st.session_state["show_delete_form"]:
                if st.button("🗑️ Elimina righe", key="show_delete", use_container_width=True):
                    st.session_state["show_delete_form"] = True
                    st.session_state["show_add_form"] = False
                    st.rerun()
        
        if st.session_state["show_add_form"]:
            st.markdown("<h3 style='color: #00d4ff; margin: 1.5rem 0;'>➕ Inserisci nuova riga</h3>", unsafe_allow_html=True)
            
            new_data = {}
            cols_per_row = 3
            columns = list(df.columns)
            
            for i in range(0, len(columns), cols_per_row):
                cols_batch = columns[i:i+cols_per_row]
                streamlit_cols = st.columns(len(cols_batch))
                
                for j, col in enumerate(cols_batch):
                    with streamlit_cols[j]:
                        # Campo speciale per PRIORITA'
                        if col_prior and col.lower() == col_prior.lower():
                            new_data[col] = st.selectbox(col, options=["", "1", "2", "3", "4", "5"], key=f"new_{col}")
                        else:
                            new_data[col] = st.text_input(col, key=f"new_{col}")
            
            col_add, col_cancel = st.columns([1, 1])
            with col_add:
                if st.button("📌 Aggiungi", key="add_row_btn"):
                    new_row = {col: (new_data[col] if new_data[col] else None) for col in df.columns}
                    df2 = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data(df2):
                        st.success("✅ Riga aggiunta!")
                        try:
                            st.cache_data.clear()
                        except Exception:
                            pass
                        st.session_state["show_add_form"] = False
                        st.rerun()
            with col_cancel:
                if st.button("❌ Annulla", key="cancel_add"):
                    st.session_state["show_add_form"] = False
                    st.rerun()
        
        if st.session_state["show_delete_form"]:
            show_delete_interface(df)
                    
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Filtri ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00d4ff; margin-bottom: 1.5rem;'>🎯 Filtri avanzati</h2>", unsafe_allow_html=True)
        st.markdown("<div class='small-muted' style='margin-bottom: 1.5rem;'>💡 I filtri vengono applicati automaticamente e possono essere combinati insieme (es. temperatura X + umidità Y)</div>", unsafe_allow_html=True)
        
        # Inizializza priority_filter e variabili filtri
        priority_filter = []
        temp_attivo = False
        hum_attivo = False
        
        c1, c2 = st.columns(2)
        with c1:
            luogo_sel = st.multiselect("📍 Seleziona luogo",
                                       sorted(df[col_luogo].dropna().unique())) if col_luogo else None
            tipo_neve = st.text_input("❄️ Tipo di neve", key="filtro_tipo_neve") if col_neve else None
            
            # Filtro priorità
            if col_prior:
                priority_filter = st.multiselect("🏆 Filtra per Priorità", 
                                                 options=["1", "2", "3", "4", "5"],
                                                 help="Seleziona una o più priorità",
                                                 key="filtro_priorita")
        with c2:
            # Filtri temperatura
            temp_field = st.selectbox("🌡️ Campo temperatura", col_temp, key="filtro_temp_field") if col_temp else None
            temp_range = None
            if temp_field:
                s = pd.to_numeric(df[temp_field], errors="coerce")
                if s.notna().sum() > 0:
                    temp_min_val_original = float(s.min())
                    temp_max_val_original = float(s.max())
                    temp_min_val = temp_min_val_original
                    temp_max_val = temp_max_val_original
                    
                    # Inizializza valori in session_state se non esistono o se cambia il campo
                    temp_min_key = f"temp_min_{temp_field}"
                    temp_max_key = f"temp_max_{temp_field}"
                    
                    # Controlla se il campo è cambiato (confronta con il campo precedente salvato)
                    prev_temp_field_key = "prev_temp_field"
                    if prev_temp_field_key not in st.session_state or st.session_state[prev_temp_field_key] != temp_field:
                        # Campo cambiato, resetta i valori
                        st.session_state[temp_min_key] = temp_min_val_original
                        st.session_state[temp_max_key] = temp_max_val_original
                        st.session_state[prev_temp_field_key] = temp_field
                    
                    if temp_min_key not in st.session_state:
                        st.session_state[temp_min_key] = temp_min_val_original
                    if temp_max_key not in st.session_state:
                        st.session_state[temp_max_key] = temp_max_val_original
                    
                    # Se min e max sono uguali, espandi leggermente il range per permettere input
                    if temp_min_val_original == temp_max_val_original:
                        temp_min_val = temp_min_val_original - 0.1 if temp_min_val_original > 0 else 0
                        temp_max_val = temp_max_val_original + 0.1
                    
                    # Due colonne per min e max
                    temp_col1, temp_col2 = st.columns(2)
                    with temp_col1:
                        temp_min = st.number_input("🌡️ Temp. Min", 
                                                   min_value=temp_min_val, 
                                                   max_value=temp_max_val,
                                                   value=st.session_state[temp_min_key],
                                                   step=0.1,
                                                   format="%.1f",
                                                   key=f"temp_min_input_{temp_field}",
                                                   help=f"Range disponibile: {temp_min_val:.1f} - {temp_max_val:.1f}")
                        st.session_state[temp_min_key] = temp_min
                    with temp_col2:
                        temp_max = st.number_input("🌡️ Temp. Max", 
                                                   min_value=temp_min_val, 
                                                   max_value=temp_max_val,
                                                   value=st.session_state[temp_max_key],
                                                   step=0.1,
                                                   format="%.1f",
                                                   key=f"temp_max_input_{temp_field}",
                                                   help=f"Range disponibile: {temp_min_val:.1f} - {temp_max_val:.1f}")
                        st.session_state[temp_max_key] = temp_max
                    
                    # Verifica che min <= max
                    if temp_min <= temp_max:
                        temp_range = (temp_min, temp_max)
                        # Filtro attivo solo se diverso dal range completo originale
                        temp_attivo = (temp_min > temp_min_val_original or temp_max < temp_max_val_original)
                    else:
                        st.warning("⚠️ Il valore minimo deve essere ≤ al massimo")
                        temp_range = None
                        temp_attivo = False
                    
            # --- Filtro umidità LIBERO ---
            hum_field = st.selectbox("💧 Campo umidità", col_hum, key="filtro_hum_field") if col_hum else None
            hum_range = None
            
            if hum_field:
                hum_col1, hum_col2 = st.columns(2)
                with hum_col1:
                    hum_min = st.number_input("💧 Umidità MIN", value=0.0, step=0.1, key="hum_min_input")
                with hum_col2:
                    hum_max = st.number_input("💧 Umidità MAX", value=100.0, step=0.1, key="hum_max_input")

                if hum_min <= hum_max:
                    hum_range = (hum_min, hum_max)
                    hum_attivo = True
                else:
                    st.warning("⚠️ Min deve essere ≤ Max")
                    hum_attivo = False
            else:
                hum_attivo = False
                    
            solo_cons = st.checkbox("📝 Solo con considerazioni", value=False, key="filtro_solo_cons") if col_cons else False
        
        # Pulsanti per gestire i filtri
        col_reset, col_info = st.columns([1, 3])
        with col_reset:
            if st.button("🔄 Reset filtri", key="reset_filters"):
                # Reset tutti i filtri
                st.session_state["filtro_tipo_neve"] = ""
                st.session_state["filtro_priorita"] = []
                st.session_state["filtro_solo_cons"] = False
                # Reset input numerici temperatura e umidità
                for key in list(st.session_state.keys()):
                    if key.startswith("temp_min_") or key.startswith("temp_max_") or \
                       key.startswith("hum_min_") or key.startswith("hum_max_") or \
                       key.startswith("temp_range_") or key.startswith("hum_range_") or \
                       key == "prev_temp_field" or key == "prev_hum_field":
                        del st.session_state[key]
                st.rerun()

        # --- Applica filtri automaticamente (non serve più il pulsante) ---
        df_filtrato = df.copy()
        filtri_attivi = []
        
        # Filtro per luogo
        if luogo_sel and col_luogo and len(luogo_sel) > 0:
            df_filtrato = df_filtrato[df_filtrato[col_luogo].isin(luogo_sel)]
            filtri_attivi.append(f"📍 Luogo: {', '.join(luogo_sel)}")
        
        # Filtro per tipo neve
        if tipo_neve and col_neve and tipo_neve.strip():
            df_filtrato = df_filtrato[df_filtrato[col_neve].astype(str).str.contains(tipo_neve, case=False, na=False)]
            filtri_attivi.append(f"❄️ Tipo neve: {tipo_neve}")
        
        # Filtro per priorità
        if col_prior and priority_filter and len(priority_filter) > 0:
            df_filtrato[col_prior] = df_filtrato[col_prior].astype(str)
            df_filtrato = df_filtrato[df_filtrato[col_prior].isin(priority_filter)]
            filtri_attivi.append(f"🏆 Priorità: {', '.join(priority_filter)}")
        
        # Filtro per temperatura (applica solo se attivo)
        if temp_field and temp_range and temp_attivo:
            s = pd.to_numeric(df_filtrato[temp_field], errors="coerce")
            df_filtrato = df_filtrato[(s >= temp_range[0]) & (s <= temp_range[1])]
            filtri_attivi.append(f"🌡️ {temp_field}: {temp_range[0]:.1f} - {temp_range[1]:.1f}")
        
        # Filtro per umidità (applica solo se attivo)
        if hum_field and hum_range and hum_attivo:
            s = pd.to_numeric(df_filtrato[hum_field], errors="coerce")
            df_filtrato = df_filtrato[(s >= hum_range[0]) & (s <= hum_range[1])]
            filtri_attivi.append(f"💧 {hum_field}: {hum_range[0]:.1f} - {hum_range[1]:.1f}")
        
        # Filtro per considerazioni
        if solo_cons and col_cons:
            df_filtrato = df_filtrato[df_filtrato[col_cons].notna()]
            filtri_attivi.append("📝 Solo con considerazioni")

        # --- Ricerca globale ---
        st.markdown("<h3 style='color: #00d4ff; margin-top: 2rem; margin-bottom: 1rem;'>🔎 Ricerca globale</h3>", unsafe_allow_html=True)
        global_search = st.text_input("🔎 Cerca in tutto il file", key="global_search", 
                                      help="Cerca il testo in tutte le colonne del dataset filtrato")
        
        # Applica ricerca globale automaticamente se c'è testo
        if global_search and global_search.strip():
            mask = pd.Series(False, index=df_filtrato.index)
            for c in df_filtrato.columns:
                mask |= df_filtrato[c].astype(str).str.contains(global_search, case=False, na=False)
            df_filtrato = df_filtrato[mask]
            filtri_attivi.append(f"🔎 Ricerca: '{global_search}'")
        
        # Mostra filtri attivi (dopo aver applicato tutti i filtri incluso la ricerca)
        if filtri_attivi:
            st.markdown(f"""
            <div style='background: rgba(0,212,255,0.15); padding: 1rem; border-radius: 12px; border: 1px solid rgba(0,212,255,0.3); margin: 1rem 0;'>
                <h4 style='color: #00d4ff; margin: 0 0 0.5rem 0;'>✅ Filtri attivi:</h4>
                <div style='color: #ffffff; font-weight: 500;'>
                    {' • '.join(filtri_attivi)}
                </div>
            </div>
            """, unsafe_allow_html=True)

        # --- Risultati con priorità evidenziate ---
        st.markdown(f"<h3 style='color: #00d4ff; margin-top: 2rem;'>📊 Risultati trovati: <span style='color: #00fff9; font-weight: 900;'>{len(df_filtrato)}</span></h3>", unsafe_allow_html=True)
        
        if len(df_filtrato) > 0:
            display_priority_dataframe(df_filtrato)
        else:
            st.warning("🔍 Nessun risultato trovato con i filtri applicati")

        st.download_button(
            label="📥 Scarica risultati (CSV)",
            data=df_filtrato.to_csv(index=False).encode("utf-8"),
            file_name="risultati.csv",
            mime="text/csv",
            key="download_btn"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # --- Chat AI ---
        context_df = df_filtrato if (df_filtrato is not None and len(df_filtrato) > 0) else df
        chat_ai_box(context_df)

    except Exception as e:
        st.error("Errore interno: " + str(e))
        st.session_state["auth"] = False

# -------------------------
# Flow principale
# -------------------------
if not st.session_state["auth"]:
    show_login()
else:
    main_app()
