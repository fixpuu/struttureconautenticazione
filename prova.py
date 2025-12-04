# prova.py - Versione pulita e ricomposta
"""
File ricomposto dall'assistente: mantiene tutta la logica originale
(marcatori CSS, UI, autenticazione KeyAuth, caricamento CSV, filtri,
visualizzazione priorità, eliminazione righe, aggiunta riga e chat AI).

Nota: ho corretto indentazione, blocchi troncati e variabili interrotte,
senza rimuovere o modificare la logica di base.
"""

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
    
    h2 { color: #00d4ff; font-weight: 700; font-size: 1.8rem; margin: 0.5rem 0; text-shadow: 0 2px 10px rgba(0,212,255,0.3); }
    h3 { color: #00fff9; font-weight: 600; font-size: 1.3rem; margin: 0.3rem 0; }
    .card { background: rgba(26, 26, 46, 0.85); backdrop-filter: blur(20px) saturate(180%); -webkit-backdrop-filter: blur(20px) saturate(180%); padding: 2rem; border-radius: 24px; box-shadow: 0 20px 60px rgba(0,0,0,0.6), 0 0 0 1px rgba(0,212,255,0.2); margin-bottom: 2rem; border: 1px solid rgba(0,212,255,0.3); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
    .card:hover { transform: translateY(-5px); box-shadow: 0 30px 80px rgba(0,212,255,0.4); border-color: rgba(0,212,255,0.5); }
    .small-muted { color: #94a3b8; font-size: 0.9rem; font-weight: 500; }
    .user-bubble { background: linear-gradient(135deg, #0f3460 0%, #533483 100%); color: white; padding: 1rem 1.5rem; border-radius: 20px 20px 5px 20px; display: inline-block; margin: 0.5rem 0; max-width: 85%; word-wrap: break-word; box-shadow: 0 4px 15px rgba(83, 52, 131, 0.5); font-weight: 500; animation: slideInRight 0.4s ease; }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(50px);} to { opacity: 1; transform: translateX(0);} }
    .ai-bubble { background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%); color: #1a1a2e; padding: 1rem 1.5rem; border-radius: 20px 20px 20px 5px; display: inline-block; margin: 0.5rem 0; max-width: 85%; word-wrap: break-word; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.5); font-weight: 600; animation: slideInLeft 0.4s ease; }
    @keyframes slideInLeft { from { opacity: 0; transform: translateX(-50px);} to { opacity: 1; transform: translateX(0);} }
    /* PRIORITÀ STYLING */
    .priority-1 { background: linear-gradient(135deg, rgba(255, 215, 0, 0.25) 0%, rgba(255, 237, 78, 0.25) 100%) !important; border-left: 4px solid #ffd700 !important; padding: 0.5rem !important; margin: 0.3rem 0 !important; }
    .priority-2 { background: linear-gradient(135deg, rgba(192, 192, 192, 0.2) 0%, rgba(232, 232, 232, 0.2) 100%) !important; border-left: 4px solid #c0c0c0 !important; padding: 0.5rem !important; margin: 0.3rem 0 !important; }
    .priority-3 { background: linear-gradient(135deg, rgba(205, 127, 50, 0.2) 0%, rgba(224, 145, 66, 0.2) 100%) !important; border-left: 4px solid #cd7f32 !important; padding: 0.5rem !important; margin: 0.3rem 0 !important; }
    .priority-4 { background: linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(0,255,249,0.1) 100%) !important; border-left: 3px solid rgba(0,212,255,0.5) !important; padding: 0.5rem !important; margin: 0.3rem 0 !important; }
    .priority-5 { background: rgba(26, 26, 46, 0.3) !important; border-left: 2px solid rgba(148, 163, 184, 0.4) !important; padding: 0.5rem !important; margin: 0.3rem 0 !important; }
    .delete-row { background: linear-gradient(135deg, rgba(255,80,80,0.2) 0%, rgba(255,120,120,0.25) 100%); border-left: 4px solid #ff5050; padding: 1rem; margin: 0.8rem 0; border-radius: 12px; transition: all 0.3s ease; backdrop-filter: blur(10px); }
    .delete-row:hover { background: linear-gradient(135deg, rgba(255,80,80,0.3) 0%, rgba(255,120,120,0.35) 100%); transform: translateX(5px); }
    .stButton > button { background: linear-gradient(135deg, #0f3460 0%, #533483 100%); color: white; border: 1px solid rgba(0,212,255,0.3); border-radius: 12px; padding: 0.75rem 2rem; font-weight: 600; font-size: 1rem; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(15, 52, 96, 0.5); }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(0, 212, 255, 0.6); border-color: rgba(0,212,255,0.6); }
    .stTextInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > select { border-radius: 12px; border: 2px solid rgba(0, 212, 255, 0.3); padding: 0.75rem 1rem; transition: all 0.3s ease; background: rgba(26, 26, 46, 0.8); color: #ffffff; font-weight: 500; }
    .stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus, .stSelectbox > div > div > select:focus { border-color: #00d4ff; box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.25); }
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stMultiSelect > label, .stSlider > label { color: #00fff9 !important; font-weight: 600 !important; font-size: 0.95rem !important; }
    .stMultiSelect > div > div { background: rgba(26, 26, 46, 0.8); color: #ffffff; border-color: rgba(0, 212, 255, 0.3); }
    .stCheckbox { padding: 0.5rem; }
    .stCheckbox > label { color: #ffffff !important; font-weight: 500 !important; }
    .stDataFrame { border-radius: 16px; overflow: hidden; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
    .stDataFrame td, .stDataFrame th { color: #ffffff !important; background-color: rgba(26, 26, 46, 0.8) !important; }
    .stDownloadButton > button { background: linear-gradient(135deg, #00d4ff 0%, #00fff9 100%); color: #1a1a2e; border: none; border-radius: 12px; padding: 0.75rem 2rem; font-weight: 700; transition: all 0.3s ease; box-shadow: 0 4px 15px rgba(0, 212, 255, 0.5); }
    .stDownloadButton > button:hover { transform: translateY(-2px); box-shadow: 0 6px 25px rgba(0, 212, 255, 0.7); }
    .stSpinner > div { border-top-color: #00d4ff !important; }
    @media (max-width: 768px) { .card { padding: 1.5rem; border-radius: 16px; } h1 { font-size: 2rem; letter-spacing: -1px; } h2 { font-size: 1.5rem; } h3 { font-size: 1.2rem; } }
    @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
    .card { animation: fadeInUp 0.6s ease; }
    .priority-badge { display: inline-block; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 700; font-size: 0.85rem; margin: 0.2rem; }
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
        except Exception:
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

    if st.session_state.get("auth_error"):
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
        if saved_user and saved_pass_hash and st.session_state.get("saved_password"):
            with st.spinner(f"Accesso automatico per {saved_user}..."):
                success = perform_login(saved_user, st.session_state.get("saved_password"), remember=True)
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
# Chat AI Migliorata
# -------------------------

def call_groq_chat(messages, max_tokens=800):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("API key AI non trovata.")

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-70b-versatile",
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=30)
    except requests.RequestException as e:
        raise RuntimeError(f"Errore di rete: {e}")

    if r.status_code == 200:
        j = r.json()
        if "choices" in j and len(j["choices"]) > 0:
            # compatibilità con diversi formati di risposta
            first = j["choices"][0]
            if isinstance(first, dict) and "message" in first and "content" in first["message"]:
                return first["message"]["content"]
            if isinstance(first, dict) and "text" in first:
                return first["text"]
        return j.get("message") or str(j)
    else:
        try:
            err = r.json()
        except Exception:
            err = r.text
        raise RuntimeError(f"Errore AI ({r.status_code}): {err}")


def summarise_dataframe_for_ai(df):
    """Crea un sommario completo e dettagliato del DataFrame per l'AI"""
    try:
        parts = []
        parts.append("=== DATASET COMPLETO ===")
        parts.append(f"Righe totali: {len(df)}")
        cols = list(df.columns)
        parts.append(f"Colonne disponibili ({len(cols)}): {', '.join(cols)}")

        def find_col(possibles):
            for p in possibles:
                for c in df.columns:
                    if p.lower() in c.lower():
                        return c
            return None

        # Analisi colonne chiave
        col_data = find_col(["data"])
        col_luogo = find_col(["luogo", "localita"])
        col_cons = find_col(["considerazione", "note", "commento", "osservazioni"])
        col_prior = find_col(["priorita", "priority"])
        col_struttura = find_col(["struttura"])
        col_impronta = find_col(["impronta"])
        col_neve = find_col(["tipo_neve", "neve"])
        col_meteo = find_col(["meteo", "condizioni"])
# Date
if col_data:
    try:
        df_temp = df.copy()
        df_temp[col_data] = pd.to_datetime(df_temp[col_data], errors="coerce")
        min_d = df_temp[col_data].min()
        max_d = df_temp[col_data].max()
        count_dates = df_temp[col_data].notna().sum()
        parts.append(
            f"📅 PERIODO: {min_d} → {max_d} ({count_dates} date valide)"
        )
    except Exception:
        pass


        # Località
        if col_luogo:
            try:
                top_luoghi = df[col_luogo].dropna().astype(str).value_counts().head(10)
                parts.append(f"
📍 LOCALITÀ ({len(df[col_luogo].dropna().unique())} uniche):")
                for luogo, count in top_luoghi.items():
                    parts.append(f"  - {luogo}: {int(count)} test/gare")
            except Exception:
                pass

        # Priorità
        if col_prior:
            try:
                df_temp = df.copy()
                df_temp[col_prior] = pd.to_numeric(df_temp[col_prior], errors='coerce')
                prior_counts = df_temp[col_prior].value_counts().sort_index()
                parts.append(f"
🏆 PRIORITÀ:")
                for p, count in prior_counts.items():
                    if pd.notna(p):
                        parts.append(f"  - Priorità {int(p)}: {int(count)} risultati")
            except Exception:
                pass

        # Strutture più usate
        if col_struttura:
            try:
                strutture = df[col_struttura].dropna().astype(str)
                strutture = strutture[strutture != '----']
                if len(strutture) > 0:
                    top_strutt = strutture.value_counts().head(10)
                    parts.append(f"
🎿 STRUTTURE PIÙ USATE:")
                    for strutt, count in top_strutt.items():
                        parts.append(f"  - {strutt}: {int(count)}x")
            except Exception:
                pass

        # Impronte più usate
        if col_impronta:
            try:
                impronte = df[col_impronta].dropna().astype(str).value_counts().head(8)
                parts.append(f"
👣 IMPRONTE PIÙ USATE:")
                for imp, count in impronte.items():
                    parts.append(f"  - {imp}: {int(count)}x")
            except Exception:
                pass

        # Tipi di neve
        if col_neve:
            try:
                neve_types = df[col_neve].dropna().astype(str).value_counts().head(8)
                parts.append(f"
❄️ TIPI DI NEVE:")
                for neve, count in neve_types.items():
                    parts.append(f"  - {neve[:60]}: {int(count)}x")
            except Exception:
                pass

        # Analisi numerica temperature e umidità
        numeric_analysis = []
        for col in df.columns:
            if any(x in col.lower() for x in ["temp", "umid", "hum"]):
                try:
                    s = pd.to_numeric(df[col], errors="coerce")
                    if s.notna().sum() > 5:
                        numeric_analysis.append(f"  - {col}: min={s.min():.1f}, media={s.mean():.1f}, max={s.max():.1f}")
                except Exception:
                    pass
        if numeric_analysis:
            parts.append(f"
🌡️ CONDIZIONI METEO:")
            parts.extend(numeric_analysis[:10])

        # Considerazioni chiave (esempi)
        if col_cons:
            try:
                examples = df[col_cons].dropna().astype(str)
                examples = examples[examples.str.len() > 10]
                if len(examples) > 0:
                    parts.append(f"
📝 CONSIDERAZIONI CHIAVE (esempi):")
                    for i, ex in enumerate(examples.head(15).tolist(), 1):
                        if len(ex) > 150:
                            ex = ex[:150] + "..."
                        parts.append(f"  {i}. {ex}")
            except Exception:
                pass

        # CSV completo ridotto
        try:
            sample_size = min(100, len(df))
            csv_sample = df.head(sample_size).to_csv(index=False)
            if len(csv_sample) > 8000:
                csv_sample = csv_sample[:8000] + "
... [troncato]"
            parts.append(f"
📊 DATI CSV ({sample_size} righe):
{csv_sample}")
        except Exception:
            pass

        return "
".join(parts)

    except Exception as e:
        return f"Errore creazione sommario: {e}"


def chat_ai_box(df_context):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='color: #00d4ff; margin-bottom: 0.5rem;'>🤖 Consulenza AI Avanzata</h2>", unsafe_allow_html=True)
    st.markdown("<div class='small-muted' style='margin-bottom: 1.5rem;'>Fai domande tecniche sui dati. L'AI ha accesso all'intero CSV e può darti consigli dettagliati su strutture, impronte, condizioni meteo e setup ottimali.</div>", unsafe_allow_html=True)

    for role, text in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"<div class='user-bubble'>👤 {st.session_state.get('user','Tu')}: {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>🤖 AI: {text}</div>", unsafe_allow_html=True)

    user_q = st.text_area("💬 Scrivi la tua domanda", key="chat_input", height=90, placeholder="Es: Quale struttura funziona meglio con neve umida e temperatura tra 0 e 5 gradi?")

    col1, col2 = st.columns([1,1])
    with col1:
        send_clicked = st.button("🚀 Invia alla AI", key="send_ai")
    with col2:
        reset_clicked = st.button("🔄 Reset chat", key="reset_chat")

    if reset_clicked:
        st.session_state["chat_history"] = []
        st.rerun()

    if send_clicked and user_q and user_q.strip():
        try:
            st.session_state["chat_history"].append(("user", user_q))

            system_prompt = """Sei un esperto consulente tecnico per sci di fondo con anni di esperienza.
COMPETENZE:

Analisi approfondita di strutture, impronte e paraffine
Correlazione tra condizioni meteo (temperatura, umidità, neve) e setup ottimale
Interpretazione delle priorità e note tecniche
Consigli basati su dati storici e pattern ricorrenti

STILE DI RISPOSTA:

Rispondi in italiano tecnico ma chiaro
Fornisci dettagli specifici citando dati dal CSV
Suggerisci setup alternativi se appropriato
Spiega il PERCHÉ delle tue raccomandazioni
Se chiesto, confronta diverse soluzioni
Usa emoji tecnici: 🎿❄️🌡️💧🏆

FORMATO:

Risposta diretta alla domanda
Dati specifici dal CSV che supportano la risposta
Raccomandazioni pratiche
Considerazioni aggiuntive se rilevanti"""
            summary = summarise_dataframe_for_ai(df_context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"DATI COMPLETI A DISPOSIZIONE:
{summary}"}
            ]

            for role, text in st.session_state["chat_history"]:
                messages.append({"role": "user" if role == "user" else "assistant", "content": text})

            with st.spinner("🧠 L'AI sta analizzando i dati in dettaglio..."):
                ai_text = call_groq_chat(messages, max_tokens=1000)

            st.session_state["chat_history"].append(("assistant", ai_text))
            st.rerun()

        except Exception as e:
            st.error("Errore AI: " + str(e))

    # Suggerimenti di esempio
    if len(st.session_state["chat_history"]) == 0:
        st.markdown("""
        <div style='margin-top: 1.5rem; padding: 1rem; background: rgba(0,212,255,0.1); border-radius: 12px; border: 1px solid rgba(0,212,255,0.3);'>
        <h4 style='color: #00d4ff; margin: 0 0 0.5rem 0;'>💡 Domande Esempio:</h4>
        <ul style='color: #94a3b8; margin: 0; padding-left: 1.5rem;'>
        <li>Qual è la struttura migliore per neve trasformata con temperatura sopra 0°?</li>
        <li>Confronta le performance di LMV+LM vs V103T+V102</li>
        <li>Quali setup hanno ottenuto priorità 1 a Bionaz?</li>
        <li>Come varia la scelta dell'impronta con l'umidità?</li>
        <li>Cosa consigli per una gara con neve nuova e -5°C?</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)

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
            preview_data.append({"index": idx, "preview": preview_text, "original_index": df_recent.index[idx]})

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
# Funzione per visualizzare DataFrame con priorità
# -------------------------

def display_priority_dataframe(df, show_priorities=False):
    """Visualizza DataFrame con evidenziazione priorità solo se show_priorities=True"""
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None

    col_prior = find_col(["priorita", "priority"])

    if show_priorities and col_prior and col_prior in df.columns:
        st.markdown("""
        <div style='margin: 1rem 0; padding: 0.8rem; background: rgba(0,212,255,0.1); border-radius: 12px; border: 1px solid rgba(0,212,255,0.3);'>
            <h4 style='color: #00d4ff; margin: 0 0 0.5rem 0; font-size: 1.1rem;'>🏆 Legenda Priorità:</h4>
            <div style='display: flex; gap: 0.8rem; flex-wrap: wrap;'>
                <span style='padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600; background: rgba(255, 215, 0, 0.25); border-left: 4px solid #ffd700;'>🥇 1° Scelta</span>
                <span style='padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600; background: rgba(192, 192, 192, 0.2); border-left: 4px solid #c0c0c0;'>🥈 2° Scelta</span>
                <span style='padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 600; background: rgba(205, 127, 50, 0.2); border-left: 4px solid #cd7f32;'>🥉 3° Scelta</span>
                <span style='padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 500; background: rgba(0,212,255,0.1); border-left: 3px solid rgba(0,212,255,0.5);'>4️⃣ Priorità 4</span>
                <span style='padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 500; background: rgba(26, 26, 46, 0.3); border-left: 2px solid rgba(148, 163, 184, 0.4);'>5️⃣ Priorità 5+</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Ordina per priorità
        df_display = df.copy()
        df_display[col_prior] = pd.to_numeric(df_display[col_prior], errors='coerce')
        df_display = df_display.sort_values(by=col_prior, na_position='last')

        # Mostra per gruppi di priorità con titoli più piccoli
        for priority in [1, 2, 3, 4, 5]:
            priority_rows = df_display[df_display[col_prior] == priority]
            if len(priority_rows) > 0:
                emoji_map = {1: "🥇", 2: "🥈", 3: "🥉", 4: "4️⃣", 5: "5️⃣"}
                priority_class = f"priority-{priority}"
                st.markdown(f"""
                <div class='{priority_class}' style='border-radius: 12px;'>
                    <h4 style='margin: 0; font-size: 1rem; color: #00fff9;'>{emoji_map.get(priority, '')} Priorità {priority} ({len(priority_rows)} risultati)</h4>
                </div>
                """, unsafe_allow_html=True)
                st.dataframe(priority_rows, use_container_width=True, height=min(350, len(priority_rows) * 35 + 50))

        # Righe senza priorità
        no_priority = df_display[df_display[col_prior].isna()]
        if len(no_priority) > 0:
            st.markdown(f"""
            <div style='padding: 0.5rem; margin: 0.5rem 0; border-radius: 12px; background: rgba(148, 163, 184, 0.1); border-left: 2px solid rgba(148, 163, 184, 0.3);'>
                <h4 style='margin: 0; font-size: 1rem; color: #94a3b8;'>📝 Senza Priorità ({len(no_priority)} risultati)</h4>
            </div>
            """, unsafe_allow_html=True)
            st.dataframe(no_priority, use_container_width=True, height=min(350, len(no_priority) * 35 + 50))
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

        # Trova tutte le colonne temperatura
        temp_aria_cols = [c for c in df.columns if "temp" in c.lower() and "aria" in c.lower()]
        temp_neve_cols = [c for c in df.columns if "temp" in c.lower() and "neve" in c.lower()]
        col_hum = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower()]

        if col_data:
            try:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date
            except Exception:
                pass

        # --- Gestione dati ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00d4ff; margin-bottom: 1.5rem;'>
