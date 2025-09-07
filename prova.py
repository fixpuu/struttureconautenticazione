# prova.py
import streamlit as st
import pandas as pd
from keyauth import api
import time

# -------------------
# CONFIG KEYAUTH
# -------------------
def getchecksum():
    import hashlib, sys
    md5_hash = hashlib.md5()
    with open(sys.argv[0], "rb") as file:
        md5_hash.update(file.read())
    return md5_hash.hexdigest()

keyauthapp = api(
    name="strutture",
    ownerid="l9G6gNHYVu",
    secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
    version="1.0",
    hash_to_check=getchecksum()
)

# -------------------
# SESSION STATE INIT
# -------------------
if 'login_successful' not in st.session_state:
    st.session_state['login_successful'] = False
if 'user' not in st.session_state:
    st.session_state['user'] = None

# -------------------
# LOGIN FORM
# -------------------
if not st.session_state['login_successful']:
    st.markdown("<h1 style='text-align:center;color:#4B0082;'>🔒 Login STRUTTURE</h1>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                try:
                    keyauthapp.login(username, password)
                    st.session_state['login_successful'] = True
                    st.session_state['user'] = username
                    st.success("✅ Login effettuato! Caricamento app...")
                    time.sleep(1)  # piccola pausa per animazione
                    st.experimental_rerun()  # aggiorna la pagina per mostrare l'app
                except Exception as e:
                    st.error(f"❌ Errore login: {e}")

# -------------------
# APP PRINCIPALE
# -------------------
if st.session_state['login_successful']:
    st.markdown(f"<h2 style='text-align:center;color:#4B0082;'>Benvenuto, {st.session_state['user']}!</h2>", unsafe_allow_html=True)
    st.info("Caricamento dati...")

    @st.cache_data
    def load_data():
        df = pd.read_csv("STRUTTURE_cleaned.csv")
        return df

    df = load_data()

    st.title("🔍 Ricerca STRUTTURE")

    # FILTRI
    luoghi = sorted(df["luogo_clean"].dropna().unique())
    luogo_sel = st.multiselect("Seleziona luogo", luoghi)
    tipo_neve = st.text_input("Tipo di neve (parola chiave)")

    temp_field = st.selectbox("Campo temperatura", ["temp_aria_inizio", "temp_aria_fine", "temp_neve_inizio", "temp_neve_fine"])
    if temp_field in df.columns:
        min_temp, max_temp = float(df[temp_field].min()), float(df[temp_field].max())
        temp_range = st.slider("Intervallo temperatura", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))
    else:
        temp_range = None

    hum_field = st.selectbox("Campo umidità", ["hum_inizio", "hum_fine"])
    if hum_field in df.columns:
        min_h, max_h = float(df[hum_field].min()), float(df[hum_field].max())
        hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h, value=(min_h, max_h))
    else:
        hum_range = None

    solo_considerazioni = st.checkbox("Mostra solo righe con considerazioni post gara/test")

    # APPLICA FILTRI
    df_filtrato = df.copy()
    if luogo_sel:
        df_filtrato = df_filtrato[df_filtrato["luogo_clean"].isin(luogo_sel)]
    if tipo_neve:
        df_filtrato = df_filtrato[df_filtrato["tipo_neve_clean"].str.contains(tipo_neve, case=False, na=False)]
    if temp_range and temp_field in df_filtrato.columns:
        df_filtrato = df_filtrato[(df_filtrato[temp_field] >= temp_range[0]) & (df_filtrato[temp_field] <= temp_range[1])]
    if hum_range and hum_field in df_filtrato.columns:
        df_filtrato = df_filtrato[(df_filtrato[hum_field] >= hum_range[0]) & (df_filtrato[hum_field] <= hum_range[1])]
    if solo_considerazioni:
        df_filtrato = df_filtrato[df_filtrato["CONSIDERAZIONE POST GARA o TEST"].notna()]

    # RISULTATI
    st.write(f"**{len(df_filtrato)} risultati trovati**")
    st.dataframe(df_filtrato)

    # DOWNLOAD CSV
    st.download_button("📥 Scarica risultati filtrati (CSV)", df_filtrato.to_csv(index=False).encode("utf-8"), "risultati.csv", "text/csv")
