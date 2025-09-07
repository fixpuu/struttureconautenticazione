import sys, hashlib, time, pandas as pd, streamlit as st
from keyauth import api

# --- PAGE CONFIG ---
st.set_page_config(page_title="🔍 STRUTTURE Premium", layout="wide")

# --- CUSTOM CSS & ANIMATIONS ---
st.markdown("""
<style>
body {background-color: #0e1117; color: #f0f0f0; font-family: 'Segoe UI', sans-serif;}
h1,h2,h3 {color:#ff6f61; text-align:center;}
.stButton>button {background-color:#ff6f61; color:white; font-size:16px; font-weight:bold; border-radius:10px; margin-right:5px; transition: transform 0.2s;}
.stButton>button:hover {transform: scale(1.05);}
.stTextInput>div>div>input {background-color:#1f1f28; color:white; border-radius:5px; padding:8px; transition: box-shadow 0.3s;}
.stTextInput>div>div>input:focus {box-shadow: 0 0 10px #ff6f61;}
.progress-bar {background-color:#ff6f61; height:15px; border-radius:10px;}
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

# --- SESSION STATE ---
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'mode' not in st.session_state:
    st.session_state['mode'] = None  # login / register

# --- LOGIN/REGISTER SCREEN ---
login_container = st.empty()  # permette di far sparire il form

if not st.session_state['authenticated']:
    with login_container.container():
        st.title("🔑 STRUTTURE Premium")
        cols = st.columns([1,1])
        with cols[0]:
            if st.button("Login"):
                st.session_state['mode'] = "login"
        with cols[1]:
            if st.button("Registrati"):
                st.session_state['mode'] = "register"

        if st.session_state['mode'] == "login":
            st.subheader("Login")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Accedi")
                if submitted:
                    with st.spinner("Verifying credentials..."):
                        time.sleep(1)  # piccola animazione
                        try:
                            keyauthapp.login(username, password)
                            st.success(f"Benvenuto {keyauthapp.user_data.username}!")
                            st.session_state['authenticated'] = True
                            login_container.empty()  # rimuove form subito
                        except Exception as e:
                            st.error(f"Errore login: {e}")

        elif st.session_state['mode'] == "register":
            st.subheader("Registrazione")
            with st.form("register_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                license_key = st.text_input("License Key")
                submitted = st.form_submit_button("Registrati")
                if submitted:
                    with st.spinner("Creando account..."):
                        time.sleep(1)
                        try:
                            keyauthapp.register(username, password, license_key)
                            st.success(f"Registrazione completata! Benvenuto {username}")
                            st.session_state['authenticated'] = True
                            login_container.empty()  # rimuove form subito
                        except Exception as e:
                            st.error(f"Errore registrazione: {e}")

# --- DASHBOARD PRINCIPALE ---
if st.session_state['authenticated']:
    st.balloons()  # effetto animato per accesso riuscito
    st.success(f"Accesso riuscito! Benvenuto {keyauthapp.user_data.username}")

    # --- CARICAMENTO CSV ---
    @st.cache_data
    def load_data():
        df = pd.read_csv("STRUTTURE_cleaned.csv")
        return df

    df = load_data()

    st.title("🔍 Ricerca STRUTTURE")
    
    # --- FILTRI AVANZATI CON ANIMAZIONE ---
    filter_container = st.container()
    with filter_container:
        with st.expander("Filtri avanzati 🔧", expanded=True):
            luoghi = sorted(df["luogo_clean"].dropna().unique())
            luogo_sel = st.multiselect("Seleziona luogo", luoghi)
            
            tipo_neve = st.text_input("Tipo di neve (ricerca per parola chiave)")
            
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

    # --- APPLICA FILTRI CON ANIMAZIONE ---
    result_container = st.container()
    with result_container:
        with st.spinner("Applicando filtri..."):
            time.sleep(0.5)  # effetto caricamento

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

            st.download_button("📥 Scarica risultati filtrati (CSV)",
                               df_filtrato.to_csv(index=False).encode("utf-8"),
                               "risultati.csv",
                               "text/csv")
