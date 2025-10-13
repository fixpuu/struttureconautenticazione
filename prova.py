# prova_fixed.py - Versione corretta con eliminazione righe e ricordami
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
    .delete-row { background: rgba(255,80,80,0.15); border-left: 3px solid #ff5050; padding:10px; margin:8px 0; border-radius:8px; }
    @media (max-width: 768px) {
      .card { padding:12px; }
      h1 { font-size:20px; }
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
            "password": hashlib.sha256(password.encode()).hexdigest()[:32]  # Hash parziale
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
            return data.get("username"), data.get("password")
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
    # Intercetta sys.exit PRIMA di qualsiasi chiamata a KeyAuth
    original_exit = sys.exit
    original_os_exit = os._exit
    
    def mock_exit(code=0):
        raise SystemExit(code)
    
    def mock_os_exit(code=0):
        raise SystemExit(code)
    
    sys.exit = mock_exit
    os._exit = mock_os_exit
    
    try:
        # Prova prima a leggere da secrets
        try:
            name = st.secrets["KEYAUTH_NAME"]
            ownerid = st.secrets["KEYAUTH_OWNERID"] 
            secret = st.secrets["KEYAUTH_SECRET"]
            version = st.secrets["KEYAUTH_VERSION"]
        except KeyError:
            # Fallback a valori di default se secrets non disponibili
            name = "strutture"
            ownerid = "l9G6gNHYVu"  
            secret = "8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1"
            version = "1.0"

        # Calcola checksum in modo sicuro
        checksum = safe_checksum()
        
        # Se non riesco a calcolare checksum, prova senza
        if checksum:
            auth_app = api(name, ownerid, secret, version, checksum)
        else:
            auth_app = api(name, ownerid, secret, version, "")
        
        # Ripristina funzioni originali
        sys.exit = original_exit
        os._exit = original_os_exit
        
        return auth_app, None
        
    except SystemExit:
        # Ripristina funzioni originali
        sys.exit = original_exit
        os._exit = original_os_exit
        return None, "Errore inizializzazione: verifica configurazione KeyAuth (ownerid, secret, version)"
        
    except Exception as e:
        # Ripristina funzioni originali
        sys.exit = original_exit
        os._exit = original_os_exit
        
        error_msg = str(e)
        
        # Gestisci errori comuni senza rivelare il sistema
        if "doesn't exist" in error_msg:
            error_msg = "Servizio di autenticazione non disponibile. Verifica la configurazione."
        elif "invalidver" in error_msg:
            error_msg = "Versione non compatibile. Aggiorna l'applicazione."
        elif "hash" in error_msg.lower():
            error_msg = "Errore di verifica integrità. Riprova o contatta il supporto."
        elif "timeout" in error_msg.lower():
            error_msg = "Timeout di connessione. Riprova tra qualche minuto."
        else:
            error_msg = f"Errore di connessione al servizio di autenticazione: {error_msg}"
        
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

# -------------------------
# Data functions
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
# Login UI migliorato con Ricordami
# -------------------------

def perform_login(username, password, remember=False):
    """Esegue il login in modo sicuro senza far terminare l'app."""
    try:
        auth_app = st.session_state["auth_app"]
        
        if auth_app is None:
            st.session_state["login_error"] = "Sistema di autenticazione non inizializzato"
            return False

        # intercetta qualsiasi tentativo di chiudere Python
        original_exit = sys.exit
        original_os_exit = os._exit
        original_time_sleep = time.sleep

        def mock_exit(code=0):
            raise SystemExit(code)

        def mock_os_exit(code=0):
            raise SystemExit(code)
        
        def mock_sleep(seconds):
            # Non bloccare l'app
            pass

        sys.exit = mock_exit
        os._exit = mock_os_exit
        time.sleep = mock_sleep

        try:
            auth_app.login(username, password)
            # se arrivo qui, login riuscito
            st.session_state["auth"] = True
            st.session_state["user"] = username
            st.session_state["login_error"] = None
            
            # Salva credenziali se ricordami è attivo
            if remember:
                save_remember_me(username, password)
            else:
                clear_remember_me()
            
            return True

        except SystemExit:
            # Login fallito - KeyAuth ha chiamato exit
            st.session_state["auth"] = False
            st.session_state["login_error"] = "Credenziali non valide, account scaduto o dispositivo non autorizzato."
            clear_remember_me()
            return False

        except BaseException as e:
            # cattura eventuali eccezioni non standard che KeyAuth potrebbe lanciare
            st.session_state["auth"] = False
            st.session_state["login_error"] = f"Errore autenticazione: {str(e)}"
            clear_remember_me()
            return False

        finally:
            # ripristina i comportamenti originali
            sys.exit = original_exit
            os._exit = original_os_exit
            time.sleep = original_time_sleep

    except Exception as e:
        msg = str(e)
        if "invalid" in msg.lower():
            msg = "Username o password non corretti."
        elif "hwid" in msg.lower():
            msg = "Dispositivo non riconosciuto. Contatta l'amministratore."
        elif "banned" in msg.lower():
            msg = "Account sospeso. Contatta l'amministratore."
        elif "expired" in msg.lower():
            msg = "Accesso scaduto. Contatta l'amministratore."
        else:
            msg = f"Errore di autenticazione: {msg}"

        st.session_state["auth"] = False
        st.session_state["login_error"] = msg
        clear_remember_me()
        return False

def show_login():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Accesso", unsafe_allow_html=True)
    
    # Inizializza auth se non è stato fatto
    if st.session_state["auth_app"] is None:
        with st.spinner("Inizializzazione in corso..."):
            app, error = initialize_auth()
            st.session_state["auth_app"] = app
            st.session_state["auth_error"] = error
    
    # Mostra errore di inizializzazione se presente
    if st.session_state["auth_error"]:
        st.error(f"❌ {st.session_state['auth_error']}")
        
        # Bottone per ritentare inizializzazione
        if st.button("🔄 Riprova connessione"):
            st.session_state["auth_app"] = None
            st.session_state["auth_error"] = None
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.stop()
    
    # Prova auto-login se "ricordami" è attivo
    if not st.session_state["auto_login_tried"]:
        st.session_state["auto_login_tried"] = True
        saved_user, saved_pass_hash = load_remember_me()
        if saved_user and saved_pass_hash:
            # Nota: non possiamo recuperare la password originale, quindi mostriamo solo un messaggio
            st.info(f"🔄 Credenziali salvate trovate per: **{saved_user}**")
            st.warning("⚠️ Inserisci la password per accedere automaticamente")
    
    # Form di login con gestione migliorata
    st.markdown("### Inserisci le tue credenziali:")
    
    # Carica username salvato se presente
    saved_user, _ = load_remember_me()
    default_username = saved_user if saved_user else ""
    
    # Usa chiavi uniche per evitare problemi di stato
    username = st.text_input("👤 Username", value=default_username, key=f"login_username_{st.session_state['login_attempt']}")
    password = st.text_input("🔑 Password", type="password", key=f"login_password_{st.session_state['login_attempt']}")
    
    # Checkbox Ricordami
    remember_me = st.checkbox("🔐 Ricordami su questo dispositivo", value=bool(saved_user))
    
    # Bottone di login sempre visibile e funzionante
    login_clicked = st.button("🔐 Accedi", key=f"login_btn_{st.session_state['login_attempt']}", use_container_width=True)
    
    # Gestione login
    if login_clicked and username and password:
        with st.spinner("Verifica credenziali..."):
            success = perform_login(username, password, remember_me)
            
        if success:
            st.success("✅ Accesso eseguito con successo!")
            time.sleep(0.5)
            st.rerun()
        else:
            # Incrementa counter per forzare rigenerazione input
            st.session_state["login_attempt"] += 1
            st.rerun()
    
    # Mostra errore di login
    if st.session_state.get("login_error"):
        st.error(f"❌ {st.session_state['login_error']}")
        st.info("💡 Verifica le credenziali e riprova.")

    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# Chat AI
# -------------------------

def call_groq_chat(messages, max_tokens=400):
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        raise RuntimeError("API key AI non trovata nella configurazione.")

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
        raise RuntimeError(f"Errore di rete verso servizio AI: {e}")

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
        raise RuntimeError(f"Errore servizio AI ({r.status_code}): {err}")

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

    # Input e bottoni separati (non in form per evitare problemi)
    user_q = st.text_area("💬 Scrivi la tua domanda (es: 'Sono a Bionaz... quale struttura consigli?')", 
                          key="chat_input", height=90)
    
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
                "Sei un assistente specializzato in test e raccomandazioni per sci di fondo (cross-country skiing). "
                "Rispondi in italiano in modo conciso e pratico, concentrandoti esclusivamente su sci di fondo: sci, attrezzatura, condizione della neve, raccomandazioni operative e considerazioni test. "
                "NON parlare di pneumatici, auto o argomenti non pertinenti. Se la domanda non è chiara o mancano dati, chiedi chiarimenti. "
                "Quando possibile dai 2-3 suggerimenti concreti, ordinati per priorità, e riferisciti ai dati forniti."
            )

            summary = summarise_dataframe_for_ai(df_context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "system", "content": f"Riassunto dei dati disponibili per il contesto:\n{summary}"}
            ]

            for role, text in st.session_state["chat_history"]:
                messages.append({"role": "user" if role == "user" else "assistant", "content": text})

            with st.spinner("L'AI sta elaborando la risposta..."):
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
    """Interfaccia grafica per eliminare righe"""
    st.markdown("## 🗑️ Elimina righe")
    st.markdown("<div class='small-muted'>Visualizza e seleziona le righe da eliminare. Le ultime modificate sono mostrate per prime.</div>", unsafe_allow_html=True)
    
    # Trova colonna data per ordinamento
    def find_col(possibles):
        for p in possibles:
            for c in df.columns:
                if p.lower() in c.lower():
                    return c
        return None
    
    col_data = find_col(["data"])
    
    # Ordina per data se possibile (più recenti prima)
    df_display = df.copy()
    if col_data:
        try:
            df_display[col_data] = pd.to_datetime(df_display[col_data], errors="coerce")
            df_display = df_display.sort_values(by=col_data, ascending=False, na_position='last')
        except Exception:
            pass
    
    # Limita a ultime 50 righe per performance
    df_recent = df_display.head(50).reset_index(drop=True)
    
    # Mostra info
    st.info(f"📊 Visualizzazione delle ultime **{len(df_recent)}** righe (su {len(df)} totali)")
    
    # Selezione righe da eliminare
    if len(df_recent) > 0:
        # Crea preview leggibile
        preview_data = []
        for idx in df_recent.index:
            row = df_recent.iloc[idx]
            
            # Crea anteprima riga
            preview = []
            for col in df_recent.columns[:5]:  # Prime 5 colonne
                val = row[col]
                if pd.notna(val) and str(val).strip():
                    preview.append(f"{col}: {str(val)[:30]}")
            
            preview_text = " | ".join(preview) if preview else f"Riga {idx}"
            preview_data.append({
                "index": idx,
                "preview": preview_text,
                "original_index": df_recent.index[idx]
            })
        
        # Mostra checkbox per ogni riga
        st.markdown("### Seleziona righe da eliminare:")
        rows_to_delete = []
        
        for item in preview_data[:20]:  # Mostra max 20 alla volta
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                selected = st.checkbox("", key=f"del_{item['index']}", label_visibility="collapsed")
            with col2:
                st.markdown(f"<div class='delete-row'>**Riga {item['index']}**: {item['preview']}</div>", unsafe_allow_html=True)
            
            if selected:
                rows_to_delete.append(item['index'])
        
        # Bottoni azione
        if rows_to_delete:
            st.warning(f"⚠️ Stai per eliminare **{len(rows_to_delete)}** riga/e")
            
            col_del, col_cancel = st.columns([1, 1])
            with col_del:
                if st.button("🗑️ Conferma eliminazione", type="primary", key="confirm_delete"):
                    try:
                        # Elimina le righe selezionate
                        indices_to_keep = [i for i in df.index if i not in [df_recent.index[idx] for idx in rows_to_delete]]
                        df_new = df.loc[indices_to_keep].reset_index(drop=True)
                        
                        if save_data(df_new):
                            st.success(f"✅ Eliminate {len(rows_to_delete)} riga/e con successo!")
                            try:
                                st.cache_data.clear()
                            except Exception:
                                pass
                            time.sleep(1)
                            st.session_state["show_delete_form"] = False
                            st.rerun()
                        else:
                            st.error("❌ Errore durante il salvataggio")
                    except Exception as e:
                        st.error(f"❌ Errore durante l'eliminazione: {e}")
            
            with col_cancel:
                if st.button("❌ Annulla", key="cancel_delete"):
                    st.session_state["show_delete_form"] = False
                    st.rerun()
        else:
            if st.button("❌ Chiudi", key="close_delete"):
                st.session_state["show_delete_form"] = False
                st.rerun()
    else:
        st.warning("Nessuna riga disponibile da eliminare")
        if st.button("❌ Chiudi", key="close_delete_empty"):
            st.session_state["show_delete_form"] = False
            st.rerun()

# -------------------------
# Main app
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
                st.session_state["auth_app"] = None
                st.session_state["login_attempt"] = 0
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
                st.rerun()
        else:
            st.markdown("## ➕ Inserisci una nuova riga")
            
            # Crea input per ogni colonna
            new_data = {}
            cols_per_row = 3
            columns = list(df.columns)
            
            for i in range(0, len(columns), cols_per_row):
                cols_batch = columns[i:i+cols_per_row]
                streamlit_cols = st.columns(len(cols_batch))
                
                for j, col in enumerate(cols_batch):
                    with streamlit_cols[j]:
                        new_data[col] = st.text_input(col, key=f"new_{col}")
            
            col_add, col_cancel = st.columns([1, 1])
            with col_add:
                if st.button("📌 Aggiungi riga", key="add_row_btn"):
                    new_row = {col: (new_data[col] if new_data[col] else None) for col in df.columns}
                    df2 = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    if save_data(df2):
                        st.success("✅ Riga aggiunta con successo!")
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
                    
        st.markdown("</div>", unsafe_allow_html=True)

        # --- Filtri ---
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🎯 Filtri")
        
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
            solo_cons = st.checkbox("📝 Solo righe with considerazioni", value=False) if col_cons else False
        
        apply_clicked = st.button("⚡ Applica filtri", key="apply_filters")

        # --- Applica filtri ---
        df_filtrato = df.copy()
        if apply_clicked:
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
        search_clicked = st.button("🔍 Cerca", key="search_btn")
        
        if search_clicked and global_search:
            mask = pd.Series(False, index=df_filtrato.index)
            for c in df_filtrato.columns:
                mask |= df_filtrato[c].astype(str).str.contains(global_search, case=False, na=False)
            df_filtrato = df_filtrato[mask]

        # --- Risultati ---
        st.markdown(f"### 📊 Risultati trovati: **{len(df_filtrato)}**")
        
        # Sostituisci None con stringhe vuote prima di visualizzare
        df_display = df_filtrato.fillna('')
        
        st.dataframe(df_display, use_container_width=True, height=500)

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
        st.error("Errore interno nell'app: " + str(e))
        st.session_state["auth"] = False

# -------------------------
# Flow principale
# -------------------------
if not st.session_state["auth"]:
    show_login()
else:
    main_app()

