import sys
import hashlib
import pandas as pd
import streamlit as st
from keyauth import api

# --- STREAMLIT STYLE ---
st.set_page_config(page_title="Ricerca STRUTTURE", layout="wide")
st.markdown("""
<style>
body {background-color: #f0f2f6;}
h1 {color: #1f77b4; font-family: 'Arial', sans-serif;}
h2 {color: #2ca02c;}
.stButton>button {background-color: #1f77b4; color: white; font-weight: bold;}
.stSlider>div>div>div>div {color: #1f77b4;}
</style>
""", unsafe_allow_html=True)

# --- KEYAUTH SETUP ---
def getchecksum():
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

# --- AUTENTICAZIONE ---
auth_container = st.container()
with auth_container:
    st.title("🔑 Autenticazione KeyAuth")
    st.info("Inserisci la tua license key per accedere all'applicazione.")
    license_key = st.text_input("License Key", type="password")
    if st.button("Conferma Key"):
        try:
            keyauthapp.license(license_key)
            st.success(f"Benvenuto {keyauthapp.user_data.username}")
            st.info(f"HWID: {keyauthapp.user_data.hwid}")
            st.session_state['authenticated'] = True
        except Exception as e:
            st.error(f"Errore KeyAuth: {e}")

# --- CARICAMENTO DATI SOLO SE AUTENTICATO ---
if st.session_state.get('authenticated', False):
    
    # Nasconde container di login
    auth_container.empty()

    # Caricamento dati CSV
    @st.cache_data
    def load_data():
        df = pd.read_csv("STRUTTURE_cleaned.csv")
        return df

    df = load_data()

    st.title("🔍 Ricerca STRUTTURE")
    
    # --- FILTRI IN COLONNE ---
    filtro_container = st.container()
    col1, col2 = st.columns(2)

    with col1:
        luoghi = sorted(df["luogo_clean"].dropna().unique())
        luogo_sel = st.multiselect("Seleziona luogo", luoghi)

        tipo_neve = st.text_input("Tipo di neve (ricerca per parola chiave)")

    with col2:
        temp_field = st.selectbox(
            "Campo temperatura",
            ["temp_aria_inizio", "temp_aria_fine", "temp_neve_inizio", "temp_neve_fine"]
        )
        if temp_field in df.columns:
            min_temp, max_temp = float(df[temp_field].min()), float(df[temp_field].max())
            temp_range = st.slider("Intervallo temperatura", min_value=min_temp, max_value=max_temp,
                                   value=(min_temp, max_temp))
        else:
            temp_range = None

        hum_field = st.selectbox("Campo umidità", ["hum_inizio", "hum_fine"])
        if hum_field in df.columns:
            min_h, max_h = float(df[hum_field].min()), float(df[hum_field].max())
            hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h,
                                  value=(min_h, max_h))
        else:
            hum_range = None

        solo_considerazioni = st.checkbox("Mostra solo righe con considerazioni post gara/test")

    # --- APPLICA FILTRI ---
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

    # --- MOSTRA RISULTATI ---
    st.markdown(f"### Risultati: {len(df_filtrato)} righe trovate")
    st.dataframe(df_filtrato)

    # --- DOWNLOAD CSV ---
    st.download_button("📥 Scarica risultati filtrati (CSV)",
                       df_filtrato.to_csv(index=False).encode("utf-8"),
                       "risultati.csv",
                       "text/csv")
