import streamlit as st
import pandas as pd
import time
import sys
import hashlib
from keyauth import api

# -------------------------
# Page config + CSS
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
body {background-color: #0f111a; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;}
h1,h2,h3 {color:#ffd580; font-weight:600;}
.card {
    background: linear-gradient(135deg,#0b1622,#1a2a40);
    padding:20px;
    border-radius:15px;
    box-shadow:0 6px 25px rgba(0,0,0,0.6);
    margin-bottom:20px;
}
.small-muted {color:#9aa7b0; font-size:13px;}
.stButton>button {
    background: linear-gradient(90deg,#ff7b00,#ffb347);
    color:white; font-weight:600; border-radius:10px; padding:8px 20px;
    border:none; transition:0.3s;
}
.stButton>button:hover {transform:scale(1.05);}
</style>
""", unsafe_allow_html=True)

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
            version="1.0"
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
# Session state
# -------------------------
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'login_error' not in st.session_state:
    st.session_state['login_error'] = None

# -------------------------
# Data loader
# -------------------------
@st.cache_data
def load_data(path="STRUTTURE_cleaned.csv"):
    try:
        df = pd.read_csv(path)
        if "DATA" in df.columns:
            df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
        return df
    except Exception as e:
        st.error(f"Errore lettura CSV '{path}': {e}")
        return None

# -------------------------
# Login UI
# -------------------------
def show_login():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login", unsafe_allow_html=True)
    with st.form("login_form"):
        c1, c2 = st.columns([2,2])
        username = c1.text_input("👤 Username")
        password = c2.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Accedi")
        if submitted:
            if keyauth_app is None:
                st.session_state['login_error'] = "KeyAuth non inizializzato."
                return
            try:
                keyauth_app.login(username, password)
                st.session_state['auth'] = True
                st.session_state['user'] = username
                st.success("✅ Login effettuato!")
                time.sleep(0.5)
            except Exception as e:
                st.session_state['login_error'] = str(e)
    if st.session_state.get('login_error'):
        st.error("❌ " + st.session_state['login_error'])
    st.markdown("</div>", unsafe_allow_html=True)
    if not st.session_state['auth']:
        st.stop()

# -------------------------
# Main App
# -------------------------
def main_app():
    st.markdown(f"<h1 style='text-align:center;'>🏔️ STRUTTURE - Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(f"<div class='small-muted' style='text-align:center;'>Benvenuto, <b>{st.session_state.get('user','utente')}</b></div>", unsafe_allow_html=True)

    df = load_data()
    if df is None: st.stop()

    # --- Mapping dinamico ---
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None

    col_data  = find_col(["data"])   # colonna giorno test
    col_luogo = find_col(["luogo_clean","luogo","localita"])
    col_neve  = find_col(["tipo_neve","neve"])
    col_cons  = find_col(["considerazione","note"])
    col_temp  = [c for c in df.columns if "temp" in c.lower()]
    col_hum   = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower()]

    st.markdown("### 🎯 Filtri")

    with st.form("filters_form"):
        c1, c2 = st.columns(2)

        with c1:
            luogo_sel = None
            if col_luogo:
                luoghi = sorted(df[col_luogo].dropna().unique())
                luogo_sel = st.multiselect("📍 Seleziona luogo", luoghi)

            tipo_neve = st.text_input("❄️ Tipo di neve (keyword)") if col_neve else None
            search_all = st.text_input("🔎 Ricerca libera")

        with c2:
            temp_field = st.selectbox("🌡️ Campo temperatura", col_temp) if col_temp else None
            temp_range = None
            if temp_field:
                s = pd.to_numeric(df[temp_field], errors="coerce")
                if s.notna().sum() > 0:
                    min_t, max_t = float(s.min()), float(s.max())
                    temp_range = st.slider("Intervallo temperatura", min_value=min_t, max_value=max_t, value=(min_t, max_t))

            hum_field = st.selectbox("💧 Campo umidità", col_hum) if col_hum else None
            hum_range = None
            if hum_field:
                s = pd.to_numeric(df[hum_field], errors="coerce")
                if s.notna().sum() > 0:
                    min_h, max_h = float(s.min()), float(s.max())
                    hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h, value=(min_h, max_h))

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

        if search_all:
            mask = pd.Series(False, index=df_filtrato.index)
            for c in df_filtrato.columns:
                mask |= df_filtrato[c].astype(str).str.contains(search_all, case=False, na=False)
            df_filtrato = df_filtrato[mask]

     # 👉 Mostra anche tutte le righe degli stessi giorni trovati
        if col_data and not df_filtrato.empty:
            giorni_trovati = pd.to_datetime(df_filtrato[col_data], errors="coerce").dt.date.unique()
            df_filtrato = df[df[col_data].isin(giorni_trovati)]

    st.markdown(f"### 📊 Risultati trovati: **{len(df_filtrato)}**")
    st.dataframe(df_filtrato, use_container_width=True, height=500)

    st.download_button("📥 Scarica risultati (CSV)", df_filtrato.to_csv(index=False).encode("utf-8"),
                       "risultati.csv", "text/csv")

# -------------------------
# Flow
# -------------------------
if not st.session_state['auth']:
    show_login()
else:
    main_app()


