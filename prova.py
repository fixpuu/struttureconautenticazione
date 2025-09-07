import sys, hashlib, time, pandas as pd, streamlit as st
from keyauth import api

# --- PAGE CONFIG ---
st.set_page_config(page_title="🔍 STRUTTURE Premium", layout="wide")

# --- STYLING ---
st.markdown("""
<style>
body {
    background-color: #0f111a;
    color: #f0f0f0;
    font-family: 'Segoe UI', sans-serif;
}
h1, h2, h3 {
    color: #ff6f61;
    text-align: center;
}
.stButton>button {
    background: linear-gradient(90deg, #ff6f61, #ff9472);
    color:white;
    font-size:16px;
    font-weight:bold;
    border-radius:15px;
    padding:8px 25px;
    transition: all 0.3s ease;
}
.stButton>button:hover {
    transform: scale(1.05);
}
.stTextInput>div>div>input {
    background-color:#1c1f33; 
    color:white; 
    border-radius:10px; 
    padding:10px; 
    border: 1px solid #ff6f61;
}
.stSlider>div>div>input {
    color: #ff6f61;
}
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

# --- LOGIN FORM ---
if not st.session_state['authenticated']:
    st.title("🔑 STRUTTURE Premium")
    st.subheader("Effettua il login per accedere")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Accedi")
        
        if submitted:
            with st.spinner("Verificando credenziali… 🔑"):
                time.sleep(1)  # animazione
                try:
                    keyauthapp.login(username, password)
                    st.success(f"Benvenuto {keyauthapp.user_data.username}!")
                    time.sleep(0.5)
                    st.session_state['authenticated'] = True
                except Exception as e:
                    st.error(f"Errore login: {e}")

# --- APP PRINCIPALE SOLO SE AUTENTICATO ---
if st.session_state['authenticated']:
    # Animazione di caricamento
    with st.spinner("Caricamento dati… 📊"):
        time.sleep(1)
    
    # --- CARICAMENTO CSV ---
    @st.cache_data
    def load_data():
        df = pd.read_csv("STRUTTURE_cleaned.csv")
        time.sleep(0.5)
        return df

    df = load_data()

    st.title("🔍 Ricerca STRUTTURE")
    
    # --- FILTRI ---
    luoghi = sorted(df["luogo_clean"].dropna().unique())
    luogo_sel = st.multiselect("Seleziona luogo", luoghi)
    tipo_neve = st.text_input("Tipo di neve (ricerca per parola chiave)")
    temp_field = st.selectbox("Campo temperatura", ["temp_aria_inizio", "temp_aria_fine", "temp_neve_inizio", "temp_neve_fine"])
    hum_field = st.selectbox("Campo umidità", ["hum_inizio", "hum_fine"])
    solo_considerazioni = st.checkbox("Mostra solo righe con considerazioni post gara/test")

    # --- APPLICA FILTRI ---
    df_filtrato = df.copy()
    if luogo_sel:
        df_filtrato = df_filtrato[df_filtrato["luogo_clean"].isin(luogo_sel)]
    if tipo_neve:
        df_filtrato = df_filtrato[df_filtrato["tipo_neve_clean"].str.contains(tipo_neve, case=False, na=False)]
    if temp_field in df.columns:
        min_temp, max_temp = float(df[temp_field].min()), float(df[temp_field].max())
        temp_range = st.slider("Intervallo temperatura", min_value=min_temp, max_value=max_temp, value=(min_temp, max_temp))
        df_filtrato = df_filtrato[(df_filtrato[temp_field] >= temp_range[0]) & (df_filtrato[temp_field] <= temp_range[1])]
    if hum_field in df.columns:
        min_h, max_h = float(df[hum_field].min()), float(df[hum_field].max())
        hum_range = st.slider("Intervallo umidità", min_value=min_h, max_value=max_h, value=(min_h, max_h))
        df_filtrato = df_filtrato[(df_filtrato[hum_field] >= hum_range[0]) & (df_filtrato[hum_field] <= hum_range[1])]
    if solo_considerazioni:
        df_filtrato = df_filtrato[df_filtrato["CONSIDERAZIONE POST GARA o TEST"].notna()]

    # --- MOSTRA DATI ---
    st.write(f"**{len(df_filtrato)} risultati trovati**")
    st.dataframe(df_filtrato, use_container_width=True)
    st.download_button(
        "📥 Scarica risultati filtrati (CSV)", 
        df_filtrato.to_csv(index=False).encode("utf-8"), 
        "risultati.csv", 
        "text/csv"
    )
