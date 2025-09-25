# prova_fixed.py - Versione corretta con miglior gestione KeyAuth
import streamlit as st
import pandas as pd
import time
import sys
import hashlib
import requests
import os
from keyauth import api

# -------------------------
# Config pagina + CSS
# -------------------------
st.set_page_config(page_title="🔍 STRUTTURE", page_icon="🏔️", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)), url("https://images.unsplash.com/photo-1608889175123-8a33f57e4dc0?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80") no-repeat center center fixed;
        background-size: cover;
    }
    h1,h2,h3 { color:#ffd580; font-weight:600; margin:0; padding:0.2rem 0; }
    .card { background: rgba(15, 17, 26, 0.78); padding:16px; border-radius:12px; box-shadow:0 6px 20px rgba(0,0,0,0.5); margin-bottom:14px; }
    .small-muted { color:#d0d0d0; font-size:13px; }
    .user-bubble { background: linear-gradient(90deg,#2b70ff,#2b9bff); color:white; padding:8px 12px; border-radius:12px; display:block; margin:6px 0; max-width:88%; word-wrap:break-word; }
    .ai-bubble { background: rgba(255,255,255,0.06); color:#e6e6e6; padding:8px 12px; border-radius:12px; display:block; margin:6px 0; max-width:88%; word-wrap:break-word; }
    @media (max-width: 768px) {
      .card { padding:12px; }
      h1 { font-size:20px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# KeyAuth helpers migliorati
# -------------------------

def safe_checksum():
    """Calcola checksum del file corrente in modo sicuro."""
    try:
        # Prova prima con __file__ se disponibile
        if hasattr(sys.modules[__name__], '__file__'):
            file_path = sys.modules[__name__].__file__
        else:
            file_path = sys.argv[0]
        
        if os.path.exists(file_path):
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                md5_hash.update(f.read())
            return md5_hash.hexdigest()
    except Exception as e:
        st.warning(f"Non riesco a calcolare checksum: {e}")
    return None

def initialize_keyauth():
    """Inizializza KeyAuth con gestione errori migliorata."""
    try:
        # Prova prima a leggere da secrets
        try:
            name = st.secrets["KEYAUTH_NAME"]
            ownerid = st.secrets["KEYAUTH_OWNERID"] 
            secret = st.secrets["KEYAUTH_SECRET"]
            version = st.secrets["KEYAUTH_VERSION"]
        except KeyError as e:
            # Fallback a valori hardcoded se secrets non disponibili
            st.warning(f"Secret mancante: {e}. Uso valori di default.")
            name = "strutture"
            ownerid = "l9G6gNHYVu"  
            secret = "8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1"
            version = "1.0"

        # Calcola checksum in modo sicuro
        checksum = safe_checksum()
        
        # Se non riesco a calcolare checksum, prova senza
        if checksum:
            keyauth_app = api(name, ownerid, secret, version, checksum)
        else:
            # KeyAuth potrebbe richiedere checksum, prova con stringa vuota
            keyauth_app = api(name, ownerid, secret, version, "")
            
        return keyauth_app, None
        
    except Exception as e:
        error_msg = str(e)
        
        # Gestisci errori comuni di KeyAuth
        if "doesn't exist" in error_msg:
            error_msg = "Applicazione KeyAuth non trovata. Verifica i parametri di configurazione."
        elif "invalidver" in error_msg:
            error_msg = "Versione non valida. Aggiorna l'applicazione."
        elif "hash" in error_msg.lower():
            error_msg = "Errore di checksum. L'applicazione potrebbe essere stata modificata."
        elif "timeout" in error_msg.lower():
            error_msg = "Timeout di connessione. Riprova tra qualche minuto."
        
        return None, error_msg

# -------------------------
# Session state init
# -------------------------
if "keyauth_app" not in st.session_state:
    st.session_state["keyauth_app"] = None
    st.session_state["keyauth_error"] = None

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
# Data functions (invariate)
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
# Login UI migliorato
# -------------------------

def show_login():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Login KeyAuth", unsafe_allow_html=True)
    
    # Inizializza KeyAuth se non è stato fatto
    if st.session_state["keyauth_app"] is None:
        with st.spinner("Inizializzazione KeyAuth..."):
            app, error = initialize_keyauth()
            st.session_state["keyauth_app"] = app
            st.session_state["keyauth_error"] = error
    
    # Mostra errore di inizializzazione se presente
    if st.session_state["keyauth_error"]:
        st.error(f"❌ Errore KeyAuth: {st.session_state['keyauth_error']}")
        
        # Bottone per ritentare inizializzazione
        if st.button("🔄 Riprova inizializzazione"):
            st.session_state["keyauth_app"] = None
            st.session_state["keyauth_error"] = None
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    
    # Form di login
    with st.form("login_form"):
        st.markdown("### Inserisci le tue credenziali:")
        
        col1, col2 = st.columns([1, 1])
        with col1:
            username = st.text_input("👤 Username", key="login_username")
        with col2:
            password = st.text_input("🔑 Password", type="password", key="login_password")
        
        # Opzioni avanzate
        with st.expander("🔧 Opzioni avanzate (opzionale)"):
            custom_hwid = st.text_input("🖥️ HWID personalizzato (lascia vuoto per auto)", 
                                      help="Solo se hai problemi con l'HWID automatico")
        
        col_login, col_reg = st.columns([1, 1])
        with col_login:
            login_clicked = st.form_submit_button("🔐 Accedi", use_container_width=True)
        with col_reg:
            register_clicked = st.form_submit_button("📝 Registrati", use_container_width=True)

        # Gestione login
        if login_clicked and username and password:
            try:
                with st.spinner("Autenticazione in corso..."):
                    keyauth_app = st.session_state["keyauth_app"]
                    
                    # Usa HWID personalizzato se fornito
                    if custom_hwid.strip():
                        keyauth_app.login(username, password, custom_hwid.strip())
                    else:
                        keyauth_app.login(username, password)
                    
                    # Login riuscito
                    st.session_state["auth"] = True
                    st.session_state["user"] = username
                    st.session_state["login_error"] = None
                    st.success("✅ Accesso eseguito con successo!")
                    time.sleep(1)
                    st.rerun()
                    
            except SystemExit:
                # KeyAuth fa sys.exit() in caso di errore
                st.session_state["auth"] = False
                st.session_state["login_error"] = "Credenziali non valide o account non autorizzato."
            except Exception as e:
                st.session_state["auth"] = False
                error_msg = str(e)
                
                # Interpreta errori comuni
                if "invalid details" in error_msg.lower():
                    error_msg = "Username o password non corretti."
                elif "hwid" in error_msg.lower():
                    error_msg = "Dispositivo non riconosciuto. Prova con HWID personalizzato."
                elif "banned" in error_msg.lower():
                    error_msg = "Account bannato. Contatta l'amministratore."
                elif "expired" in error_msg.lower():
                    error_msg = "Licenza scaduta."
                
                st.session_state["login_error"] = error_msg

        # Gestione registrazione
        if register_clicked and username and password:
            license_key = st.text_input("🎫 Chiave di licenza:", key="reg_license")
            if license_key:
                try:
                    with st.spinner("Registrazione in corso..."):
                        keyauth_app = st.session_state["keyauth_app"]
                        keyauth_app.register(username, password, license_key)
                        st.success("✅ Registrazione completata! Ora puoi effettuare il login.")
                except Exception as e:
                    st.error(f"❌ Errore registrazione: {str(e)}")

    # Mostra errore di login
    if st.session_state.get("login_error"):
        st.error(f"❌ {st.session_state['login_error']}")

    # Info per debug
    with st.expander("🔍 Info debug"):
        st.write("**Status KeyAuth:**")
        st.write(f"- App inizializzata: {'✅' if st.session_state['keyauth_app'] else '❌'}")
        st.write(f"- Autenticato: {'✅' if st.session_state['auth'] else '❌'}")
        if st.session_state.get("keyauth_app"):
            st.write("- Connessione KeyAuth: ✅")
            
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Chat AI e funzioni principali (invariate)
# -------------------------

def call_groq_chat(messages, max_tokens=400):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("Groq API key non trovata in st.secrets['GROQ_API_KEY'].")

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
        raise RuntimeError(f"Errore di rete verso Groq: {e}")

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
        raise RuntimeError(f"Errore Groq ({r.status_code}): {err}")

def summarise_dataframe_for_ai(df):
    try:
        parts = []
        parts.append(f"Righe totali dataset: {len(df)}")
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
                parts.append("Top località (fino a 6): " + "; ".join([f"{i} ({int(v)})" for i, v in top_luoghi.items()]))
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
            parts.append(f"{c}: min={s.min()} median={s.median()} mean={round(s.mean(),2) if s.notna().sum()>0 else 'NA'} max={s.max()} (valid={s.notna().sum()})")

        if col_cons:
            examples = df[col_cons].dropna().astype(str).head(6).tolist()
            if examples:
                parts.append("Esempi note/considerazioni: " + " | ".join(examples))

        try:
            excerpt = df.head(25).to_csv(index=False)
            if len(excerpt) > 3000:
                excerpt = excerpt[:3000] + "\n... (troncato)"
            parts.append("Estratto CSV (prime 25 righe, troncato se lungo):\n" + excerpt)
        except Exception:
            pass

        return "\n".join(parts)
    except Exception:
        return "Impossibile creare sommario del dataset."

def chat_ai_box(df_context):
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🤖 Consulenza AI (BETA)", unsafe_allow_html=True)
    st.markdown("<div class='small-muted'>Fai domande sui dati filtrati (sci di fondo). L'AI userà il sommario e un estratto CSV come contesto.</div>", unsafe_allow_html=True)

    # render chat history
    for role, text in st.session_state["chat_history"]:
        if role == "user":
            st.markdown(f"<div class='user-bubble'>👤 {st.session_state.get('user','Tu')}: {text}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='ai-bubble'>🤖 AI: {text}</div>", unsafe_allow_html=True)

    with st.form("chat_form", clear_on_submit=False):
        user_q = st.text_area("💬 Scrivi la tua domanda (es: 'Sono a Bionaz... quale struttura consigli?')", key="chat_input", height=90)
        c1, c2 = st.columns([1,1])
        with c1:
            send = st.form_submit_button("Invia alla AI")
        with c2:
            reset = st.form_submit_button("🔄 Reset chat")

    if reset:
        st.session_state["chat_history"] = []
        st.rerun()

    if send and user_q and user_q.strip():
        try:
            st.session_state["chat_history"].append(("user", user_q))

            system_prompt = (
                "Sei un assistente specializzato in test e raccomandazioni per sci di fondo (cross-country skiing). "
                "Rispondi in italiano in modo conciso e pratico, concentrandoti esclusivamente su sci di fondo: sci, attrezzatura, condizione della neve, raccomandazioni operative e considerazioni test. "
                "NON parlare di pneumatici, auto o argomenti non pertinenti. Se la domanda non è chiara o mancano dati, chiedi chiarimenti. "
                "Quando possibile dai 2-3 suggerimenti concreti, ordinati per priorità, e riferisciti ai dati forniti."
            )

            summary = summarise_dataframe_for_ai(df_context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Riassunto dei dati disponibili per il contesto (non è l'intero file):\n{summary}"}
            ]

            for role, text in st.session_state["chat_history"]:
                messages.append({"role": "user" if role == "user" else "assistant", "content": text})

            with st.spinner("L'AI sta ragionando..."):
                ai_text = call_groq_chat(messages, max_tokens=500)

            st.session_state["chat_history"].append(("assistant", ai_text))
        except Exception as e:
            st.error("Errore AI: " + str(e))

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Main app (invariata)
# -------------------------

def main_app():
    try:
        st.markdown(f"<h1 style='text-align:center;'>🏔️ STRUTTURE - Dashboard</h1>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='small-muted' style='text-align:center;'>Benvenuto, <b>{st.session_state.get('user','utente')}</b></div>",
            unsafe_allow_html=True,
        )

        # Logout button
        col_l, col_r = st.columns([9,1])
        with col_r:
            if st.button("Logout"):
                st.session_state["auth"] = False
                st.session_state["user"] = None
                st.session_state["keyauth_app"] = None  # Reset KeyAuth
                st.rerun()

        df = load_data()
        if df is None:
            st.info("Nessun dataset disponibile. Carica il CSV nella root come 'STRUTTURE_cleaned.csv'.")
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
        col_cons = find_col(["considerazione", "note", "commento"])
        col_temp = [c for c in df.columns if "temp" in c.lower()]
        col_hum = [c for c in df.columns if "hum" in c.lower() or "umid" in c.lower()]

        if col_data:
            try:
                df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date
            except Exception:
                pass

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
                try:
                    df[col_data] = pd.to_datetime(df[col_data], errors="coerce").dt.date
                    df_filtrato[col_data] = pd.to_datetime(df_filtrato[col_data], errors="coerce").dt.date
                    giorni_trovati = df_filtrato[col_data].dropna().unique().tolist()
                    df_filtrato = df[df[col_data].isin(giorni_trovati)]
                except Exception:
                    pass

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

    except Exception as e:
        st.error("Errore interno nell'app: " + str(e))
        st.session_state["auth"] = False

# -------------------------
# Flow principale
# -------------------------
if not st.session_state["auth"]:
    show_login()
else:
    main_app()
