import streamlit as st
import pyautogui
import pandas as pd
import time
from keyauth import api

# ======================
# CONFIGURAZIONE KEYAUTH
# ======================
keyauthapp = api(
    name="strutture",
    ownerid="l9G6gNHYVu",
    secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
    version="1.0"
)

# ======================
# SESSION STATE INIT
# ======================
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'login_error' not in st.session_state:
    st.session_state['login_error'] = ''

# ======================
# FUNZIONI
# ======================
def login(username, password):
    try:
        keyauthapp.login(username, password)
        if keyauthapp.response.success:
            st.session_state['authenticated'] = True
            pyautogui.alert("Login effettuato con successo!", title="✔ Success")
        else:
            st.session_state['login_error'] = "Credenziali non valide!"
    except Exception as e:
        st.session_state['login_error'] = str(e)

@st.cache_data
def load_data():
    df = pd.read_csv("STRUTTURE_cleaned.csv")
    return df

# ======================
# LOGIN FORM
# ======================
if not st.session_state['authenticated']:
    st.markdown(
        """
        <style>
        .login-box {background-color:#1f1f1f;padding:40px;border-radius:20px;
                    box-shadow:0px 10px 30px rgba(0,0,0,0.5);max-width:450px;margin:auto;}
        .stButton>button {margin:5px;width:45%;height:45px;font-size:18px;border-radius:10px;}
        .stTextInput>div>div>input {height:45px;font-size:16px;border-radius:10px;}
        </style>
        """, unsafe_allow_html=True
    )

    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.title("🔑 Accedi a Strutture App")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                login(username, password)
        with col2:
            st.button("Info")  # eventuale pulsante extra
        st.markdown('</div>', unsafe_allow_html=True)
    
    if st.session_state['login_error']:
        st.error(st.session_state['login_error'])
    st.stop()  # STOPPA la renderizzazione dell'app principale finché non login

# ======================
# CONTENUTO PRINCIPALE
# ======================
st.markdown(
    """
    <style>
    .main-box {padding:30px;border-radius:20px;background:linear-gradient(135deg,#00c6ff,#0072ff);
                color:white;box-shadow:0px 10px 30px rgba(0,0,0,0.5);}
    </style>
    """, unsafe_allow_html=True
)
st.markdown('<div class="main-box">', unsafe_allow_html=True)

st.title("🔍 Ricerca STRUTTURE")

df = load_data()

# Filtri
luoghi = sorted(df["luogo_clean"].dropna().unique())
luogo_sel = st.multiselect("Seleziona luogo", luoghi)

tipo_neve = st.text_input("Tipo di neve (parola chiave)")

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

# Applica filtri
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

# Mostra risultati
st.write(f"**{len(df_filtrato)} risultati trovati**")
st.dataframe(df_filtrato)

# Download CSV
st.download_button("📥 Scarica risultati filtrati (CSV)",
                   df_filtrato.to_csv(index=False).encode("utf-8"),
                   "risultati.csv",
                   "text/csv")

st.markdown('</div>', unsafe_allow_html=True)
