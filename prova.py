# prova.py - versione completa con chat AI Groq integrata
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
        return df
    except Exception as e:
        st.error(f"Errore lettura CSV '{path}': {e}")
        return None

def save_data(df, path="STRUTTURE_cleaned.csv"):
    try:
        df.to_csv(path, index=False)
        return True
    except Exception as e:
        st.error(f"Errore salvataggio CSV: {e}")
        return False

# -------------------------
# Login UI
# -------------------------
def show_login():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login", unsafe_allow_html=True)

    with st.form("login_form"):
        c1, c2 = st.columns([2, 2])
        username = c1.text_input("👤 Username")
        password = c2.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Accedi")

        if submitted:
            if keyauth_app is None:
                st.session_state["login_error"] = "KeyAuth non inizializzato."
                return
            try:
                keyauth_app.login(username, password)
                st.session_state["auth"] = True
                st.session_state["user"] = username
                st.success("✅ Login effettuato!")
                time.sleep(0.4)
            except Exception as e:
                st.session_state["login_error"] = str(e)

    if st.session_state.get("login_error"):
        st.error("❌ " + st.session_state["login_error"])

    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state["auth"]:
        st.stop()

# -------------------------
# Chat AI helper (Groq)
# -------------------------
def call_groq_chat(messages, max_tokens=400):
    """
    messages: list of dicts like {"role":"user"/"system"/"assistant","content": "..."}
    """
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("Groq API key non trovata in st.secrets['GROQ_API_KEY'].")

    url = "https://api.groq.com/openai/v1/chat/completions"
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": messages,
        "max_tokens": max_tokens
    }
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    r = requests.post(url, json=payload, headers=headers, timeout=30)
    if r.status_code == 200:
        j = r.json()
        if "choices" in j and len(j["choices"]) > 0 and "message" in j["choices"][0]:
            return j["choices"][0]["message"]["content"]
        return j.get("message") or str(j)
    else:
        raise RuntimeError(f"Errore Groq ({r.status_code}): {r.text}")

def chat_ai_box(df_context):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Consulenza AI (Groq)", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Fai domande sui dati filtrati. L'AI userà i dati come contesto.</div>", unsafe_allow_html=True)

    for role, text in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"<div class='user-bubble'>👤 {st.session_state.get('user','Tu')}: {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>🤖 AI: {text}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=False):
        user_q = st.text_area("💬 Scrivi la tua domanda", key="chat_input")
        send = st.form_submit_button("Invia alla AI")
        reset = st.form_submit_button("🔄 Reset chat")

    if reset:
        st.session_state["chat_history"] = []
        st.experimental_rerun()

    if send and user_q and user_q.strip():
        st.session_state["chat_history"].append(("user", user_q))

        system_prompt = (
            "Sei un assistente per supportare decisioni tecniche su sci/strutture. "
            "Rispondi in modo conciso, pratico e con raccomandazioni basate sui dati storici forniti. "
            "Se possibile, dai 2-3 suggerimenti concreti e ordina per priorità."
        )

        try:
            df_excerpt = df_context.head(20).to_csv(index=False)
        except Exception:
            df_excerpt = "Impossibile serializzare il dataset."

        messages = [{"role": "system", "content": system_prompt}]
        messages.append({"role": "system", "content": f"Ecco un estratto dei dati (CSV):\n{df_excerpt}"})
        for role, text in st.session_state["chat_history"]:
            messages.append({"role": "user" if role == "user" else "assistant", "content": text})

        try:
            with st.spinner("L'AI sta ragionando..."):
                ai_text = call_groq_chat(messages, max_tokens=500)
            st.session_state["chat_history"].append(("assistant", ai_text))
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Errore AI: {e}")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Main app
# -------------------------
def main_app():
    st.markdown(f"<h1 style='text-align:center;'>🏔️ STRUTTURE - Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='small-muted' style='text-align:center;'>Benvenuto, <b>{st.session_state.get('user','utente')}</b></div>",
        unsafe_allow_html=True,
    )

    df = load_data()
    if df is None:
        st.stop()

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
    col_cons = find_col(["considerazione", "note"])
    col_temp = [c for c in df.columns if "temp" in c.lower()]
    col_hum = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower()]

    if col_data:
        df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date

    # --- Gestione dati ---
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### ✨ Gestione dati")
    if not st.session_state["show_add_form"]:
        if st.button("➕ Aggiungi una nuova riga", key="show_add"):
            st.session_state["show_add_form"] = True
    else:
        st.markdown("## ➕ Inserisci una nuova riga")
        with st.form("add_row_form"):
            new_data = {col: st.text_input(col, key=f"new_{col}") for col in df.columns}
            submitted_new = st.form_submit_button("📌 Aggiungi riga")
            if submitted_new:
                new_row = {col: (new_data[col] if new_data[col] else None) for col in df.columns}
                df2 = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_data(df2):
                    st.success("✅ Riga aggiunta con successo!")
                    try:
                        st.cache_data.clear()
                    except Exception:
                        pass
                    st.session_state["show_add_form"] = False
        if st.button("❌ Annulla", key="hide_add"):
            st.session_state["show_add_form"] = False
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Filtri ---
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Filtri")
    with st.form("filters_form"):
        c1, c2 = st.columns(2)
        with c1:
            luogo_sel = st.multiselect("📍 Seleziona luogo",
                                       sorted(df[col_luogo].dropna().unique())) if col_luogo else None
            tipo_neve = st.text_input("❄️ Tipo di neve") if col_neve else None
        with c2:
            temp_field = st.selectbox("🌡️ Campo temperatura", col_temp) if col_temp else None
            temp_range = None
            if temp_field:
                s = pd.to_numeric(df[temp_field], errors="coerce")
                if s.notna().sum() > 0:
                    temp_range = st.slider("Intervallo temperatura",
                                           float(s.min()), float(s.max()),
                                           (float(s.min()), float(s.max())))
            hum_field = st.selectbox("💧 Campo umidità", col_hum) if col_hum else None
            hum_range = None
            if hum_field:
                s = pd.to_numeric(df[hum_field], errors="coerce")
                if s.notna().sum() > 0:
                    hum_range = st.slider("Intervallo umidità",
                                           float(s.min()), float(s.max()),
                                           (float(s.min()), float(s.max())))
            solo_cons = st.checkbox("📝 Solo righe con considerazioni", value=False) if col_cons else False
        apply_btn = st.form_submit_button("⚡ Applica filtri")

    # --- Applica filtri ---
    df_filtrato = df.copy()
    if apply_btn:
        if luogo_sel and col_luogo:
            df_filtrato = df_filtrato[df_filtrato[col_luogo].isin(luogo_sel)]
        if tipo_neve and col_neve:
            df_filtrato = df_filtrato[df_filtrato[col_neve].astype(str).str.contains(tipo_neve, case=False, na=False)]
        if temp_field and temp_range:
            s = pd.to_numeric(df_filtrato[temp_field], errors="coerce")
            df_filtrato = df_filtrato[(s >= temp_range[0]) & (s <= temp_range[1])]
        if hum_field and hum_range:
            s = pd.to_numeric(df_filtrato[hum_field], errors="coerce")
            df_filtrato = df_filtrato[(s >= hum_range[0]) & (s <= hum_range[1])]
        if solo_cons and col_cons:
            df_filtrato = df_filtrato[df_filtrato[col_cons].notna()]

        if col_data and not df_filtrato.empty:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date
            df_filtrato[col_data] = pd.to_datetime(df_filtrato[col_data], errors="coerce").dt.date
            giorni_trovati = df_filtrato[col_data].dropna().unique().tolist()
            df_filtrato = df[df[col_data].isin(giorni_trovati)]

    # --- 🔎 Barra di ricerca globale ---
    st.markdown("### 🔎 Ricerca globale")
    global_search = st.text_input("🔎 Cerca in tutto il file", key="global_search")
    if global_search:
        mask = pd.Series(False, index=df_filtrato.index)
        for c in df_filtrato.columns:
            mask |= df_filtrato[c].astype(str).str.contains(global_search, case=False, na=False)
        df_filtrato = df_filtrato[mask]

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

# -------------------------
# Flow
# -------------------------
if not st.session_state["auth"]:
    show_login()
else:
    main_app()
