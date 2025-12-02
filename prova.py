# prova.py - VERSIONE AGGIORNATA
# Include: multi-filter (anche multi-temp), group inclusion per righe "continuazione",
# ricerca globale, login robusto, UI scura. Copia/sovrascrivi il file esistente.

import streamlit as st
import pandas as pd
import time, sys, hashlib, os, json
from keyauth import api

# -------------------------
# Config pagina + CSS (tema scuro minimale)
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown("""
<style>
/* semplice tema scuro - puoi estendere */
.stApp { background: linear-gradient(135deg, #0b1220 0%, #0f2130 100%); color: #e6eef8; }
.card { background: rgba(10, 16, 28, 0.75); padding:20px; border-radius:12px; box-shadow: 0 6px 20px rgba(0,0,0,0.6); }
h1,h2,h3 { color:#ffd580; }
.stButton > button { background: linear-gradient(90deg,#ff7b00,#ffb347); color:white; border-radius:10px; padding:8px 18px; }
.stTextInput > label, .stSelectbox > label, .stMultiSelect > label { color:#cfeefd !important; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# -------------------------
# Helpers auth (checksum + init KeyAuth)
# -------------------------
def safe_checksum():
    try:
        path = sys.modules[__name__].__file__ if hasattr(sys.modules[__name__], '__file__') else sys.argv[0]
        if os.path.exists(path):
            md5 = hashlib.md5()
            with open(path, "rb") as f:
                md5.update(f.read())
            return md5.hexdigest()
    except Exception:
        pass
    return None

def init_keyauth():
    try:
        # preferisci mettere credenziali in st.secrets se su Streamlit Cloud
        name = st.secrets.get("KEYAUTH_NAME", "strutture")
        ownerid = st.secrets.get("KEYAUTH_OWNERID", "l9G6gNHYVu")
        secret = st.secrets.get("KEYAUTH_SECRET", "8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1")
        version = st.secrets.get("KEYAUTH_VERSION", "1.0")
        chk = safe_checksum()
        kwargs = dict(name=name, ownerid=ownerid, secret=secret, version=version)
        if chk:
            kwargs["hash_to_check"] = chk
        # costruttore dell'API KeyAuth - wrapper locale
        return api(**kwargs), None
    except Exception as e:
        return None, str(e)

# -------------------------
# Session state init
# -------------------------
if "auth" not in st.session_state:
    st.session_state["auth"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "auth_app" not in st.session_state:
    st.session_state["auth_app"], st.session_state["auth_init_error"] = init_keyauth()
if "login_error" not in st.session_state:
    st.session_state["login_error"] = None
if "show_add_form" not in st.session_state:
    st.session_state["show_add_form"] = False
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# -------------------------
# Data loader (cerca più nomi CSV)
# -------------------------
@st.cache_data
def load_data_try(paths=None):
    if paths is None:
        paths = ["STRUTTURE_cleaned.csv", "STRUTTURE (1).csv", "STRUTTURE.csv"]
    for p in paths:
        if os.path.exists(p):
            try:
                df = pd.read_csv(p, dtype=str)   # carichiamo tutto come stringhe per safety
                df = df.fillna("")  # evita NaN nella logica
                df["_source_path"] = p
                return df, p
            except Exception as e:
                continue
    return None, None

def save_data(df, path):
    try:
        df.to_csv(path, index=False)
        # invalida cache
        try:
            st.cache_data.clear()
        except Exception:
            pass
        return True
    except Exception as e:
        st.error(f"Errore salvataggio CSV: {e}")
        return False

# -------------------------
# Login (robusto: non lasciare che sys.exit uccida l'app)
# -------------------------
def perform_login(username, password):
    app = st.session_state.get("auth_app")
    if app is None:
        st.session_state["login_error"] = "Sistema di autenticazione non inizializzato."
        return False
    # KeyAuth wrappers talvolta chiamano sys.exit/raise SystemExit -> catturiamo
    try:
        app.login(username, password)
        st.session_state["auth"] = True
        st.session_state["user"] = username
        st.session_state["login_error"] = None
        return True
    except SystemExit:
        st.session_state["auth"] = False
        st.session_state["login_error"] = "Credenziali non valide o account scaduto."
        return False
    except Exception as e:
        st.session_state["auth"] = False
        st.session_state["login_error"] = f"{str(e)}"
        return False

def show_login_ui():
    st.markdown("<div class='card' style='max-width:600px;margin:0 auto;'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login")
    if st.session_state.get("auth_init_error"):
        st.error("Errore inizializzazione KeyAuth: " + str(st.session_state.get("auth_init_error")))

    with st.form("login_form"):
        c1, c2 = st.columns([2,2])
        username = c1.text_input("👤 Username")
        password = c2.text_input("🔑 Password", type="password")
        submitted = st.form_submit_button("Accedi")

        if submitted:
            ok = perform_login(username, password)
            if ok:
                st.success("✅ Login effettuato!")
                time.sleep(0.25)
                st.rerun()     # <<< CORRETTO
            else:
                st.error("❌ " + (st.session_state.get("login_error") or "Errore login"))

    st.markdown("</div>", unsafe_allow_html=True)

    if not st.session_state["auth"]:
        st.stop()

# -------------------------
# Funzione: costruisce 'group_date' per includere righe continuazione
# (la colonna DATA originale può essere vuota nelle righe successive)
# -------------------------
def add_group_date_column(df, col_data_name):
    # col_data_name è il nome della colonna che contiene la DATA (se esiste)
    df2 = df.copy()
    if not col_data_name or col_data_name not in df2.columns:
        # nessuna colonna data: crea group_date vuoto
        df2["__group_date"] = ""
        return df2
    # converti in datetime quando possibile: lasciamo stringhe ma proviamo parse
    try:
        # provo a creare una colonna datetime coerente; se fallisce manteniamo stringa e ffill
        parsed = pd.to_datetime(df2[col_data_name], errors="coerce")
        # se parsed non è tutto NaT, usalo per ffill; altrimenti fallback su stringhe non vuote
        if parsed.notna().sum() > 0:
            df2["_parsed_date"] = parsed
            # forward-fill basato su parsed_date
            df2["_parsed_date_ff"] = df2["_parsed_date"].ffill()
            # renderizzo come date ISO o stringa per matching
            df2["__group_date"] = df2["_parsed_date_ff"].dt.date.astype(str).fillna("")
            df2 = df2.drop(columns=["_parsed_date","_parsed_date_ff"])
        else:
            # fallback: considera celle non vuote come "start group" e ffill delle stringhe
            df2["__group_date"] = df2[col_data_name].replace("", pd.NA).ffill().fillna("").astype(str)
    except Exception:
        df2["__group_date"] = df2[col_data_name].replace("", pd.NA).ffill().fillna("").astype(str)
    return df2

# -------------------------
# Utility: trova nome colonna per pattern
# -------------------------
def find_col_by_keywords(df, possibles):
    for p in possibles:
        for c in df.columns:
            if p.lower() in c.lower():
                return c
    return None

# -------------------------
# MAIN APP
# -------------------------
def main_app():
    # header
    st.markdown("<div style='text-align:center;margin-bottom:1rem;'><h1>🏔️ STRUTTURE</h1></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center;color:#cfeefd;'>Benvenuto <b>{st.session_state.get('user') or 'utente'}</b></div>", unsafe_allow_html=True)

    df, used_path = load_data_try()
    if df is None:
        st.error("Nessun file CSV trovato. Metti 'STRUTTURE_cleaned.csv' (o 'STRUTTURE (1).csv') nella cartella.")
        st.stop()

    # pulizia / colonne utili
    # non eliminare colonne originali - lavoriamo su copia
    df = df.copy()

    # colonna data rilevata (nome dinamico)
    col_data = find_col_by_keywords(df, ["data", "DATA"])
    col_luogo = find_col_by_keywords(df, ["luogo", "localita", "località"])
    col_neve = find_col_by_keywords(df, ["tipo_neve", "tipo neve", "neve", "tipo_neve_clean"])
    col_cons = find_col_by_keywords(df, ["considerazione", "note", "CONSIDERAZIONE", "OSSERVAZIONI"])
    col_temp_candidates = [c for c in df.columns if "temp" in c.lower() or "temper" in c.lower()]
    col_hum_candidates = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower() or "humidity" in c.lower()]
    col_prior = find_col_by_keywords(df, ["priorita", "priority"])

    # aggiungo colonna group_date per includere righe "continuazione"
    df = add_group_date_column(df, col_data)

    # --- Gestione dati: aggiungi / elimina (semplice)
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### ✨ Gestione dati")
    c1, c2 = st.columns([1,1])
    with c1:
        if st.button("➕ Aggiungi riga"):
            st.session_state["show_add_form"] = not st.session_state["show_add_form"]
            st.experimental_rerun()
    with c2:
        if st.button("🔄 Ricarica dati"):
            try:
                st.cache_data.clear()
            except Exception:
                pass
            st.experimental_rerun()

    if st.session_state["show_add_form"]:
        st.markdown("#### Inserisci nuova riga (campi vuoti -> lascialo)")
        with st.form("add_row"):
            new_vals = {}
            cols = list(df.columns)
            # non mostriamo gruppo virtuale
            cols = [c for c in cols if c != "__group_date" and c != "_source_path"]
            for col in cols:
                new_vals[col] = st.text_input(col)
            if st.form_submit_button("Aggiungi"):
                # append su df e salva nello stesso file utilizzato
                row = {k: (v if v is not None else "") for k,v in new_vals.items()}
                df2 = pd.concat([df[cols].copy(), pd.DataFrame([row])], ignore_index=True)
                if save_data(df2, used_path):
                    st.success("Riga aggiunta.")
                    st.session_state["show_add_form"] = False
                    st.experimental_rerun()
                else:
                    st.error("Errore salvataggio.")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Filtri avanzati (multi-filter) ---
    st.markdown("<div class='card' style='margin-top:1rem;'>", unsafe_allow_html=True)
    st.markdown("### 🎯 Filtri avanzati (applicabili insieme)")

    with st.form("filters_form"):
        # colonne sinistra/destra
        left, right = st.columns(2)
        with left:
            luogo_sel = None
            if col_luogo:
                luoghi = sorted(df[col_luogo].replace("", pd.NA).dropna().unique().tolist())
                luogo_sel = st.multiselect("📍 Seleziona luogo", options=luoghi)
            neve_keyword = st.text_input("❄️ Tipo di neve (keyword)", value="")
            # priorità
            priority_sel = None
            if col_prior:
                priority_choices = sorted(df[col_prior].replace("", pd.NA).dropna().unique().tolist())
                priority_sel = st.multiselect("🏆 Priorità", options=priority_choices)

        with right:
            # multipli campi temperature: permetti di selezionare più campi temp
            temp_fields_sel = []
            if col_temp_candidates:
                temp_fields_sel = st.multiselect("🌡️ Seleziona campi temperatura (puoi scegliere più)", options=col_temp_candidates)
            temp_ranges = {}
            for tfield in temp_fields_sel:
                # calcolo min/max numerico
                s = pd.to_numeric(df[tfield].replace("", pd.NA), errors="coerce")
                if s.notna().sum() > 0:
                    mn, mx = float(s.min()), float(s.max())
                    rng = st.slider(f"Intervallo per {tfield}", min_value=mn, max_value=mx, value=(mn, mx), step=(max(0.1, (mx-mn)/100)))
                    temp_ranges[tfield] = rng
                else:
                    st.info(f"{tfield}: nessun valore numerico rilevabile")

            # multipli campi umidità
            hum_fields_sel = []
            if col_hum_candidates:
                hum_fields_sel = st.multiselect("💧 Seleziona campi umidità", options=col_hum_candidates)
            hum_ranges = {}
            for h in hum_fields_sel:
                s = pd.to_numeric(df[h].replace("", pd.NA), errors="coerce")
                if s.notna().sum() > 0:
                    mn, mx = float(s.min()), float(s.max())
                    rng = st.slider(f"Intervallo per {h}", min_value=mn, max_value=mx, value=(mn, mx), step=(max(0.1, (mx-mn)/100)))
                    hum_ranges[h] = rng
                else:
                    st.info(f"{h}: nessun valore numerico rilevabile")

        # ricerca globale / testo (ma la mettiamo in basso per ordine)
        apply_btn = st.form_submit_button("⚡ Applica filtri")

    # Applico filtri su copia
    df_filtered = df.copy()

    if apply_btn:
        # LUOGO
        if luogo_sel and col_luogo:
            df_filtered = df_filtered[df_filtered[col_luogo].isin(luogo_sel)]
        # NEVE keyword
        if neve_keyword and col_neve:
            df_filtered = df_filtered[df_filtered[col_neve].astype(str).str.contains(neve_keyword, case=False, na=False)]
        # PRIORITA
        if priority_sel and col_prior:
            df_filtered = df_filtered[df_filtered[col_prior].astype(str).isin(priority_sel)]
        # TEMPERATURE: per ogni campo richiesto AND tra i filtri (tutti devono rispettare il range)
        for tfield, rng in temp_ranges.items():
            s = pd.to_numeric(df_filtered[tfield].replace("", pd.NA), errors="coerce")
            df_filtered = df_filtered[(s >= rng[0]) & (s <= rng[1])]
        # UMIDITA'
        for hfield, rng in hum_ranges.items():
            s = pd.to_numeric(df_filtered[hfield].replace("", pd.NA), errors="coerce")
            df_filtered = df_filtered[(s >= rng[0]) & (s <= rng[1])]
        # SOLO con considerazioni
        if col_cons:
            df_filtered = df_filtered[df_filtered[col_cons].replace("", pd.NA).notna()]

        # --- IMPORTANT: estendi selezione per includere tutte le righe del "blocco" dello stesso giorno ---
        # df_filtered contiene le righe che corrispondono ai filtri; vogliamo includere TUTTE le righe del file
        # aventi lo stesso __group_date (creato con ffill) di quelle trovate.
        try:
            giorni = df_filtered["__group_date"].replace("", pd.NA).dropna().unique().tolist()
            if giorni:
                df_filtered = df[df["__group_date"].isin(giorni)].copy()
        except Exception:
            # se qualcosa va storto ignoriamo questa estensione
            pass

    # --- Ricerca globale (posizionata qui, dopo i filtri)
    st.markdown("<div style='margin-top:12px;'>", unsafe_allow_html=True)
    st.markdown("### 🔎 Ricerca globale (testo)")
    col_a, col_b = st.columns([4,1])
    with col_a:
        global_query = st.text_input("Cerca in tutto il blocco filtrato (lascia vuoto per disabilitare)", key="global_query")
    with col_b:
        if st.button("🔍 Cerca", key="global_search_btn"):
            # eseguiamo la ricerca testuale nella view corrente
            if global_query:
                mask = pd.Series(False, index=df_filtered.index)
                for c in df_filtered.columns:
                    if c == "__group_date" or c == "_source_path":
                        continue
                    mask |= df_filtered[c].astype(str).str.contains(global_query, case=False, na=False)
                df_filtered = df_filtered[mask]
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Risultati: usiamo la funzione di formattazione priorità se presente
    st.markdown("<div class='card' style='margin-top:12px;'>", unsafe_allow_html=True)
    st.markdown(f"### 📊 Risultati trovati: **{len(df_filtered)}**")

    # se esiste col_prior visualizziamo raggruppati, altrimenti semplice dataframe
    if col_prior and col_prior in df_filtered.columns and df_filtered[col_prior].replace("", pd.NA).notna().any():
        # ordina per group_date (se esiste) e priorità
        try:
            df_show = df_filtered.copy()
            df_show[col_prior] = pd.to_numeric(df_show[col_prior], errors="coerce")
            if "__group_date" in df_show.columns:
                df_show = df_show.sort_values(["__group_date", col_prior], ascending=[True, True], na_position="last")
            else:
                df_show = df_show.sort_values(col_prior, na_position="last")
        except Exception:
            df_show = df_filtered.copy()
        st.dataframe(df_show.reset_index(drop=True), width=1400, height=520)
    else:
        st.dataframe(df_filtered.reset_index(drop=True), width=1400, height=520)

    # Download
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Scarica risultati (CSV)", data=csv_bytes, file_name="risultati.csv", mime="text/csv")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Flow
# -------------------------
if not st.session_state.get("auth", False):
    show_login_ui()
else:
    main_app()

