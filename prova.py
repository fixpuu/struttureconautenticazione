import sys
import hashlib
import pandas as pd
import streamlit as st
from keyauth import api

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

st.title("🔑 Autenticazione KeyAuth")

license_key = st.text_input("Inserisci la tua license key", type="password")
if st.button("Conferma Key"):
    try:
        keyauthapp.license(license_key)
        st.success(f"Benvenuto {keyauthapp.user_data.username}")
        st.info(f"HWID: {keyauthapp.user_data.hwid}")
    except Exception as e:
        st.error(f"Errore KeyAuth: {e}")

# --- CARICAMENTO DATI CSV ---
@st.cache_data
def load_data():
    df = pd.read_csv("STRUTTURE_cleaned.csv")
    return df

df = load_data()

st.title("🔍 Ricerca STRUTTURE")

# --- FILTRI UTENTE ---
luoghi = sorted(df["luogo_clean"].dropna().unique())
luogo_sel = st.multiselect("Seleziona luogo", luoghi)

tipo_neve = st.text_input("Tipo di neve (ricerca per parola chiave)")

# Campi temperatura
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

# Campi umidità
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
st.write(f"**{len(df_filtrato)} risultati trovati**")
st.dataframe(df_filtrato)

# --- DOWNLOAD CSV ---
st.download_button("📥 Scarica risultati filtrati (CSV)",
                   df_filtrato.to_csv(index=False).encode("utf-8"),
                   "risultati.csv",
                   "text/csv")
