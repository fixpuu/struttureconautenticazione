import streamlit as st
import pandas as pd
import os
import time
from keyauth import api

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
def login_form():
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
                    time.sleep(0.5)
                except Exception as e:
                    st.error(f"❌ Errore login: {e}")

# -------------------
# APP PRINCIPALE
# -------------------
def main_app():
    st.markdown(f"<h2 style='text-align:center;color:#4B0082;'>Bentornato, {st.session_state['user']}!</h2>", unsafe_allow_html=True)
    st.info("Hai bisogno di aiuto o supporto? Contatta lo sviluppatore su: https://t.me/fixpuu")

    @st.cache_data
    def load_data():
        # Carica il nuovo file completo
        df = pd.read_csv("STRUTTURE_full.csv")
        return df

    df = load_data()
    st.title("🔍 Ricerca STRUTTURE")

    # FILTRI
    luoghi = sorted(df["luogo_clean"].dropna().unique()) if "luogo_clean" in df.columns else []
    luogo_sel = st.multiselect("Seleziona luogo", luoghi)

    tipo_neve = st.text_input("Tipo di neve (parola chiave)")

    temp_field = st.selectbox("Campo temperatura", [c for c in df.columns if "temp" in c])
    temp_range = None
    if temp_field in df.columns:
        try:
            min_temp, max_temp = float(df[temp_field].min()), float(df[temp_field].max())
            temp_range = st.slider("Intervallo temperatura", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))
        except:
            pass

    hum_field = st.selectbox("Campo umidità", [c for c in df.columns if "hum" in c])
    hum_range = None
    if hum_field in df.columns:
        try:
            min_h, max_h = float(df[hum_field].min()), float(df[hum_field].max())
            hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h, value=(min_h, max_h))
        except:
            pass

    solo_considerazioni = st.checkbox("Mostra solo righe con considerazioni post gara/test")

    # APPLICA FILTRI
    df_filtrato = df.copy()
    if luogo_sel and "luogo_clean" in df.columns:
        df_filtrato = df_filtrato[df_filtrato["luogo_clean"].isin(luogo_sel)]
    if tipo_neve and "tipo_neve_clean" in df.columns:
        df_filtrato = df_filtrato[df_filtrato["tipo_neve_clean"].str.contains(tipo_neve, case=False, na=False)]
    if temp_range and temp_field in df_filtrato.columns:
        df_filtrato = df_filtrato[(df_filtrato[temp_field] >= temp_range[0]) & (df_filtrato[temp_field] <= temp_range[1])]
    if hum_range and hum_field in df_filtrato.columns:
        df_filtrato = df_filtrato[(df_filtrato[hum_field] >= hum_range[0]) & (df_filtrato[hum_field] <= hum_range[1])]
    if solo_considerazioni and "considerazione_post_gara_o_test" in df.columns:
        df_filtrato = df_filtrato[df_filtrato["considerazione_post_gara_o_test"].notna()]

    # RISULTATI
    st.write(f"**{len(df_filtrato)} risultati trovati**")
    st.dataframe(df_filtrato)

    # DOWNLOAD CSV
    st.download_button(
        "📥 Scarica risultati filtrati (CSV)",
        df_filtrato.to_csv(index=False).encode("utf-8"),
        "risultati.csv",
        "text/csv"
    )

# -------------------
# LOGICA APP
# -------------------
if not st.session_state['login_successful']:
    login_form()
else:
    main_app()
