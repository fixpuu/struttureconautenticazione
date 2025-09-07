import streamlit as st
import pandas as pd
import time
import webbrowser
from keyauth import api

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="🔍 STRUTTURE App",
    page_icon="🏔️",
    layout="wide"
)

# --- FUNZIONI ---
def get_keyauth_app():
    """Configura KeyAuth"""
    return api(
        name="strutture",
        ownerid="l9G6gNHYVu",
        secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
        version="1.0",
    )

def login_form():
    """Form di login"""
    st.markdown("## 🔐 Login")
    with st.form("login_form", clear_on_submit=True):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            try:
                keyauth_app.license(username)  # Verifica KeyAuth con username come chiave
                st.session_state['login_successful'] = True
                st.success("✅ Login effettuato! Caricamento app...")
                time.sleep(1)  # Animazione caricamento
            except Exception as e:
                st.error(f"❌ Errore login: {str(e)}")

def load_data():
    """Carica CSV"""
    path = "STRUTTURE_cleaned.csv"
    df = pd.read_csv(path)
    return df

def app_main(df):
    """Contenuto principale dell'app"""
    st.title("🔍 Ricerca STRUTTURE")
    
    # --- Filtri ---
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

    # --- Applica filtri ---
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

    # --- Mostra risultati ---
    st.write(f"**{len(df_filtrato)} risultati trovati**")
    st.dataframe(df_filtrato)

    st.download_button(
        "📥 Scarica risultati filtrati (CSV)",
        df_filtrato.to_csv(index=False).encode("utf-8"),
        "risultati.csv",
        "text/csv"
    )

# --- MAIN ---
keyauth_app = get_keyauth_app()

if 'login_successful' not in st.session_state:
    st.session_state['login_successful'] = False

if not st.session_state['login_successful']:
    login_form()
    st.stop()  # Blocca l'esecuzione finché non effettui login

# Se login effettuato, mostra app
df = load_data()
app_main(df)
