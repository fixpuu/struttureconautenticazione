import streamlit as st
import pandas as pd
import time
import sys
import hashlib
from keyauth import api
import streamlit.components.v1 as components
from datetime import datetime

# -------------------------
# Page config + CSS
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
/* Basic theme */
body {background-color: #0f111a; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;}
h1,h2,h3 {color:#ffd580; font-weight:600;}
.card {
    background: linear-gradient(135deg,#0b1622,#1a2a40);
    padding:20px;
    border-radius:15px;
    box-shadow:0 6px 25px rgba(0,0,0,0.6);
    margin-bottom:20px;
}
.big-button {
    background: linear-gradient(90deg,#00c6ff,#0072ff);
    color:white; font-weight:700; font-size:18px;
    border-radius:15px; padding:14px 28px;
    border:none; text-align:center;
    margin:18px 0;
}
.stButton>button:hover {transform:scale(1.03);}
/* small text */
.small-muted {color:#9aa7b0; font-size:13px;}
/* ensure Streamlit app content is above background */
#snow-canvas { position: fixed; top:0; left:0; width:100%; height:100%; pointer-events:none; z-index:-1; }

/* card inside app for forms */
.form-card {
    background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 14px;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# Snow background (canvas JS)
# -------------------------
snow_html = """
<canvas id="snow-canvas"></canvas>
<script>
const canvas = document.getElementById('snow-canvas');
function resize() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
}
window.addEventListener('resize', resize);
resize();

const ctx = canvas.getContext('2d');
const flakes = [];
const numFlakes = Math.floor(window.innerWidth / 10);

for (let i = 0; i < numFlakes; i++) {
  flakes.push({
    x: Math.random() * canvas.width,
    y: Math.random() * canvas.height,
    r: Math.random() * 3 + 1,
    d: Math.random() * numFlakes
  });
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = 'rgba(255,255,255,0.9)';
  ctx.beginPath();
  for (let i = 0; i < flakes.length; i++) {
    const f = flakes[i];
    ctx.moveTo(f.x, f.y);
    ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2, true);
  }
  ctx.fill();
  update();
}
let angle = 0;
function update() {
  angle += 0.01;
  for (let i = 0; i < flakes.length; i++) {
    const f = flakes[i];
    f.y += Math.cos(angle + f.d) + 1 + f.r / 2;
    f.x += Math.sin(angle) * 2;
    if (f.x > canvas.width + 5 || f.x < -5 || f.y > canvas.height) {
      f.x = Math.random() * canvas.width;
      f.y = -10;
    }
  }
}
setInterval(draw, 30);
</script>
"""
# Render with a small height but canvas is fixed so covers whole viewport
components.html(snow_html, height=10)

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
# Session state defaults
# -------------------------
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'login_error' not in st.session_state:
    st.session_state['login_error'] = None
if 'show_add_form' not in st.session_state:
    st.session_state['show_add_form'] = False

# -------------------------
# Data loader / saver
# -------------------------
@st.cache_data
def load_data(path="STRUTTURE_cleaned.csv"):
    try:
        df = pd.read_csv(path)
        # drop some unwanted columns if present
        drop_cols = ["luogo_clean", "tipo_neve_clean", "hum_inizio_sospetto", "hum_fine_sospetto"]
        df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors="ignore")
        if "DATA" in df.columns:
            df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").dt.date
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
    if df is None:
        st.stop()

    # --- Pulsante per mostrare form aggiunta ---
    st.markdown("### ✨ Gestione dati")
    if not st.session_state['show_add_form']:
        if st.button("➕ Aggiungi una nuova riga", key="show_add", use_container_width=True):
            st.session_state['show_add_form'] = True
            st.rerun()
    else:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("## ➕ Inserisci una nuova riga")
        with st.form("add_row_form"):
            new_data = {}
            cols = df.columns.tolist()
            # generiamo input coerenti: se la colonna sembra una data usiamo date_input, se numerica number_input, altrimenti text_input
            for col in cols:
                lower = col.lower()
                if "date" in lower or "data" == lower or "giorno" in lower:
                    new_data[col] = st.date_input(f"{col}", key=f"new_{col}")
                elif any(k in lower for k in ["temp","temper","°","celsius","f°"]) :
                    new_data[col] = st.number_input(f"{col}", value=0.0, format="%.2f", key=f"new_{col}")
                elif any(k in lower for k in ["hum","umid","percent"]):
                    new_data[col] = st.number_input(f"{col}", value=0.0, format="%.2f", key=f"new_{col}")
                elif any(k in lower for k in ["note","consider","consid","comment"]):
                    new_data[col] = st.text_area(f"{col}", key=f"new_{col}")
                else:
                    new_data[col] = st.text_input(f"{col}", key=f"new_{col}")
            submitted_new = st.form_submit_button("📌 Aggiungi riga")
            if submitted_new:
                # Normalizza valori: date -> string iso, empty string -> None
                new_row = {}
                for col, val in new_data.items():
                    if isinstance(val, (datetime,)) or (hasattr(val, "isoformat") and hasattr(val, "year")):
                        try:
                            new_row[col] = val.isoformat()
                        except Exception:
                            new_row[col] = str(val)
                    elif val == "":
                        new_row[col] = None
                    else:
                        new_row[col] = val
                df_new = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                if save_data(df_new):
                    st.success("✅ Riga aggiunta con successo!")
                    st.cache_data.clear()  # aggiorna cache di load_data
                    time.sleep(0.4)
                    st.session_state['show_add_form'] = False
                    st.rerun()
        if st.button("❌ Annulla", key="hide_add", use_container_width=True):
            st.session_state['show_add_form'] = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- Mapping dinamico ---
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None

    col_data  = find_col(["data"])
    col_luogo = find_col(["luogo","localita"])
    col_neve  = find_col(["tipo_neve","neve"])
    col_cons  = find_col(["considerazione","note"])
    col_temp  = [c for c in df.columns if "temp" in c.lower()]
    col_hum   = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower()]

    # -------------------------
    # Filtri
    # -------------------------
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

        if col_data and not df_filtrato.empty:
            giorni_trovati = pd.to_datetime(df_filtrato[col_data], errors="coerce").dt.date.unique()
            df_filtrato = df[df[col_data].isin(giorni_trovati)]

    st.markdown(f"### 📊 Risultati trovati: **{len(df_filtrato)}**")
    st.dataframe(df_filtrato, width="stretch", height=500)

    st.download_button(
        "📥 Scarica risultati (CSV)",
        df_filtrato.to_csv(index=False).encode("utf-8"),
        "risultati.csv",
        "text/csv"
    )

# -------------------------
# Flow
# -------------------------
if not st.session_state['auth']:
    show_login()
else:
    main_app()
