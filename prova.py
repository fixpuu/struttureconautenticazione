# prova.py - versione completa con fix bottoni mouse, chat e login
import streamlit as st
import pandas as pd
import time
import sys
import hashlib
import requests
from keyauth import api


# -------------------------
# Config pagina + CSS
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown(
"""
<style>
.stApp {
background: url("https://images.unsplash.com/photo-1608889175123-8a33f57e4dc0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80") no-repeat center center fixed;
background-size: cover;
}
.stApp::before { content: ""; position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.6); z-index: -1; }
h1,h2,h3 { color:#ffd580; font-weight:600; }
.card { background: rgba(15, 17, 26, 0.75); backdrop-filter: blur(8px); padding:20px; border-radius:15px; box-shadow:0 6px 25px rgba(0,0,0,0.6); margin-bottom:20px; }
.small-muted { color:#ccc; font-size:13px; }
.stButton>button {
background: linear-gradient(90deg,#ff7b00,#ffb347);
color:white; font-weight:600; border-radius:10px; padding:8px 20px; border:none; transition:0.15s;
}
.stButton>button:hover { transform:scale(1.03); }
/* Chat bubbles */
.user-bubble { background: linear-gradient(90deg,#2b70ff,#2b9bff); color:white; padding:10px 14px; border-radius:14px; display:inline-block; margin:6px 0; }
.ai-bubble { background: rgba(255,255,255,0.06); color:#e6e6e6; padding:10px 14px; border-radius:14px; display:inline-block; margin:6px 0; }
</style>
""",
unsafe_allow_html=True,
)


# -------------------------
# KeyAuth init
# -------------------------
def safe_checksum():
try:
md5_hash = hashlib.md5()
with open(sys.argv[0], "rb") as f:
md5_hash.update(f.read())
return md5_hash.hexdigest()
except Exception:
return None


def get_keyauth_app():
try:
kwargs = dict(
name="strutture",
ownerid="l9G6gNHYVu",
secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
version="1.0",
)
chk = safe_checksum()
if chk:
kwargs["hash_to_check"] = chk
return api(**kwargs)
except Exception as e:
st.error("Errore inizializzazione KeyAuth: " + str(e))
return None


# inizializzazione globale
keyauth_app = get_keyauth_app()


# -------------------------
# Session state init
# -------------------------
if "auth" not in st.session_state:
st.session_state["auth"] = False
if "user" not in st.session_state:
st.session_state["user"] = None
if "login_error" not in st.session_state:
st.session_state["login_error"] = None
if "show_add_form" not in st.session_state:
st.session_state["show_add_form"] = False
if "chat_history" not in st.session_state:
st.session_state["chat_history"] = []


# -------------------------
# Data loader / saver
# -------------------------
@st.cache_data
def load_data(path="STRUTTURE_cleaned.csv"):
try:
df = pd.read_csv(path)
        # --- Risultati ---
        st.markdown(f"### 📊 Risultati trovati: **{len(df_filtrato)}**")
        st.dataframe(df_filtrato, width="stretch", height=500)

        st.download_button(
            label="📥 Scarica risultati (CSV)",
            data=df_filtrato.to_csv(index=False).encode("utf-8"),
            file_name="risultati.csv",
            mime="text/csv"
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # --- Chat AI ---
        context_df = df_filtrato if (df_filtrato is not None and len(df_filtrato) > 0) else df
        chat_ai_box(context_df)

    except Exception as e:
        # In caso di errore imprevisto nella UI principale: non crashare l'app.
        st.error("Errore interno nell'app: " + str(e))
        st.session_state["auth"] = False
        st.session_state["login_error"] = "Errore interno: " + str(e)
        st.experimental_rerun()

# -------------------------
# Flow
# -------------------------
if not st.session_state["auth"]:
    show_login()
else:
    main_app()

