# prova.py
import streamlit as st
import pandas as pd
import time
import sys
import hashlib
from keyauth import api

# -------------------------
# Page config + minimal CSS
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
body {background-color: #0f111a; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;}
h1,h2 {color:#ffd580;}
.card {background: linear-gradient(135deg,#0b1622,#102233); padding:18px; border-radius:12px; box-shadow:0 6px 30px rgba(0,0,0,0.6);}
.small-muted {color:#9aa7b0; font-size:13px;}
</style>
""", unsafe_allow_html=True)

# -------------------------
# KeyAuth init (robusta)
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
# Session state init
# -------------------------
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'login_error' not in st.session_state:
    st.session_state['login_error'] = None

# -------------------------
# Utility: robust column mapping
# -------------------------
def map_columns(df):
    """Ritorna mappa di colonne logiche -> nome colonna reale o None."""
    cols = list(df.columns)
    lower_map = {c.lower(): c for c in cols}

    def find_any(possibles):
        for p in possibles:
            if p.lower() in lower_map:
                return lower_map[p.lower()]
        # try substring match
        for c in cols:
            lc = c.lower()
            for p in possibles:
                if p.lower() in lc:
                    return c
        return None

    mapping = {}
    mapping['luogo'] = find_any(['luogo_clean', 'luogo', 'localita', 'località', 'location', 'place'])
    mapping['tipo_neve'] = find_any(['tipo_neve_clean', 'tipo_neve', 'neve', 'tipo_neve'])
    # temperatures: choose all columns that look like temperature
    temp_candidates = [c for c in cols if 'temp' in c.lower() or 'temperat' in c.lower()]
    mapping['temps'] = temp_candidates  # list (maybe empty)
    hum_candidates = [c for c in cols if 'hum' in c.lower() or 'umid' in c.lower()]
    mapping['hums'] = hum_candidates
    mapping['considerazioni'] = find_any(['CONSIDERAZIONE POST GARA o TEST', 'considerazione', 'note', 'considerazioni'])
    return mapping

# -------------------------
# Data loader (cached)
# -------------------------
@st.cache_data
def load_data(path="STRUTTURE_cleaned.csv"):
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Errore lettura CSV '{path}': {e}")
        return None

# -------------------------
# LOGIN UI (sparisce dopo auth)
# -------------------------
def show_login():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login (username / password)")
    with st.form("login_form", clear_on_submit=False):
        cols = st.columns([3,2,1])
        with cols[0]:
            username = st.text_input("Username")
        with cols[1]:
            password = st.text_input("Password", type="password")
        with cols[2]:
            submitted = st.form_submit_button("Accedi")
        if submitted:
            if keyauth_app is None:
                st.session_state['login_error'] = "KeyAuth non inizializzato correttamente."
                return
            try:
                # prova a fare login; l'API KeyAuth qui può variare a seconda della libreria
                # Qui seguiamo il tuo uso precedente: keyauth_app.login(username, password)
                keyauth_app.login(username, password)
                # se la chiamata non solleva errore, consideriamo login OK
                st.session_state['auth'] = True
                st.session_state['user'] = username
                st.success("✅ Login effettuato! Caricamento app...")
                # lasciare un piccolo delay per l'effetto, poi la pagina verrà rerun (submit)
                time.sleep(0.5)
            except Exception as e:
                st.session_state['login_error'] = str(e)
    if st.session_state.get('login_error'):
        st.error(st.session_state['login_error'])
    st.markdown("</div>", unsafe_allow_html=True)
    # IMPORTANT: stoppiamo l'esecuzione qui se non autenticati (così la parte principale non viene renderizzata)
    if not st.session_state['auth']:
        st.stop()

# -------------------------
# MAIN APP
# -------------------------
def main_app():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown(f"### 👋 Benvenuto, **{st.session_state.get('user','utente')}**", unsafe_allow_html=True)
    df = load_data()
    if df is None:
        st.stop()

    mapping = map_columns(df)

    # Show detected columns (small muted)
    detected = []
    if mapping['luogo']: detected.append(f"luogo: `{mapping['luogo']}`")
    if mapping['tipo_neve']: detected.append(f"tipo_neve: `{mapping['tipo_neve']}`")
    if mapping['temps']: detected.append(f"temp fields: {mapping['temps']}")
    if mapping['hums']: detected.append(f"hum fields: {mapping['hums']}")
    if mapping['considerazioni']: detected.append(f"considerazioni: `{mapping['considerazioni']}`")
    if detected:
        st.markdown("<div class='small-muted'>Colonne rilevate: " + " • ".join(detected) + "</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='small-muted'>Attenzione: non sono state rilevate colonne utili per i filtri.</div>", unsafe_allow_html=True)

    st.markdown("---")

    # Layout filtri + ricerca libera
    with st.expander("🔎 Filtri e ricerca", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            # luogo filter
            luogo_sel = None
            if mapping['luogo']:
                unique_luoghi = sorted(df[mapping['luogo']].dropna().unique())
                luogo_sel = st.multiselect("Seleziona luogo", unique_luoghi)
            # tipo neve free text (if exists)
            tipo_neve_query = None
            if mapping['tipo_neve']:
                tipo_neve_query = st.text_input("Tipo di neve (keyword)", value="")
            # general free text search across string columns
            q = st.text_input("Ricerca libera (cerca in tutte le colonne testuali)")
            reset = st.button("Reset filtri")
        with col2:
            # temperature selector: if multiple detected, choose one
            temp_field = None
            if mapping['temps']:
                temp_field = st.selectbox("Campo temperatura (se presente)", mapping['temps'])
                # compute range only if numeric
                try:
                    series = pd.to_numeric(df[temp_field], errors='coerce')
                    min_temp, max_temp = float(series.min()), float(series.max())
                    temp_range = st.slider("Intervallo temperatura", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))
                except Exception:
                    temp_range = None
            else:
                temp_range = None

            hum_field = None
            if mapping['hums']:
                hum_field = st.selectbox("Campo umidità (se presente)", mapping['hums'])
                try:
                    series = pd.to_numeric(df[hum_field], errors='coerce')
                    min_h, max_h = float(series.min()), float(series.max())
                    hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h, value=(min_h, max_h))
                except Exception:
                    hum_range = None
            else:
                hum_range = None

            mostra_cons = False
            if mapping['considerazioni']:
                mostra_cons = st.checkbox("Mostra solo righe con considerazioni post gara/test")
        if reset:
            # simple way: rerun without persistent filters
            st.experimental_set_query_params()  # reset URL params - harmless
            st.experimental_rerun()

    # --- Applica filtri in modo robusto con animazione
    with st.spinner("Applicazione filtri..."):
        time.sleep(0.35)
        df_filtered = df.copy()

        # luogo
        if mapping['luogo'] and luogo_sel:
            df_filtered = df_filtered[df_filtered[mapping['luogo']].isin(luogo_sel)]

        # tipo neve
        if mapping['tipo_neve'] and tipo_neve_query:
            df_filtered = df_filtered[df_filtered[mapping['tipo_neve']].astype(str).str.contains(tipo_neve_query, case=False, na=False)]

        # temp range
        if temp_field and temp_range is not None and temp_field in df_filtered.columns:
            series = pd.to_numeric(df_filtered[temp_field], errors='coerce')
            df_filtered = df_filtered[(series >= temp_range[0]) & (series <= temp_range[1])]

        # hum range
        if hum_field and hum_range is not None and hum_field in df_filtered.columns:
            series = pd.to_numeric(df_filtered[hum_field], errors='coerce')
            df_filtered = df_filtered[(series >= hum_range[0]) & (series <= hum_range[1])]

        # considerazioni
        if mostra_cons and mapping['considerazioni']:
            df_filtered = df_filtered[df_filtered[mapping['considerazioni']].notna() & (df_filtered[mapping['considerazioni']].astype(str).str.strip() != "")]

        # ricerca libera q: cerca in tutte le colonne testuali
        if q:
            # build boolean mask across object/string columns
            text_cols = [c for c in df_filtered.columns if df_filtered[c].dtype == "object" or df_filtered[c].dtype.name == "string"]
            if text_cols:
                mask = pd.Series(False, index=df_filtered.index)
                for c in text_cols:
                    mask = mask | df_filtered[c].astype(str).str.contains(q, case=False, na=False)
                df_filtered = df_filtered[mask]
            else:
                # no textual columns, try all columns by casting
                mask = pd.Series(False, index=df_filtered.index)
                for c in df_filtered.columns:
                    mask = mask | df_filtered[c].astype(str).str.contains(q, case=False, na=False)
                df_filtered = df_filtered[mask]

    # --- Visualizzazione risultati
    st.markdown(f"### Risultati: {len(df_filtered)} righe")
    st.dataframe(df_filtered, use_container_width=True)

    # download
    st.download_button("📥 Scarica risultati (CSV)", df_filtered.to_csv(index=False).encode("utf-8"), "risultati.csv", "text/csv")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# App flow
# -------------------------
if not st.session_state['auth']:
    show_login()
else:
    main_app()
