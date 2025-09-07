import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="🔍 STRUTTURE Premium", layout="wide")

# --- CONTROLLO LOGIN ---
query_params = st.experimental_get_query_params()
if query_params.get("auth") != ["ok"]:
    st.warning("Devi effettuare il login prima!")
    st.stop()

# --- CARICAMENTO CSV ---
@st.cache_data
def load_data():
    return pd.read_csv("STRUTTURE_cleaned.csv")

df = load_data()

# --- INTERFACCIA ANIMATA ---
st.markdown("""
    <style>
    .fade-in {
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from {opacity:0; transform: translateY(20px);}
        to {opacity:1; transform: translateY(0);}
    }
    .stSlider>div>div>div>div>div {
        background: linear-gradient(90deg,#667eea,#764ba2);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔍 Ricerca STRUTTURE Premium", anchor="top")

with st.container():
    st.markdown('<div class="fade-in">', unsafe_allow_html=True)

    # FILTRI
    col1, col2 = st.columns(2)
    with col1:
        luoghi = sorted(df["luogo_clean"].dropna().unique())
        luogo_sel = st.multiselect("Seleziona luogo", luoghi)
    with col2:
        tipo_neve = st.text_input("Tipo di neve (parola chiave)")

    temp_field = st.selectbox("Campo temperatura", ["temp_aria_inizio", "temp_aria_fine", "temp_neve_inizio", "temp_neve_fine"])
    hum_field = st.selectbox("Campo umidità", ["hum_inizio", "hum_fine"])
    solo_considerazioni = st.checkbox("Mostra solo righe con considerazioni post gara/test")

    # FILTRAGGIO
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

    # RISULTATI CON ANIMAZIONE
    st.write(f"**{len(df_filtrato)} risultati trovati**")
    st.dataframe(df_filtrato, use_container_width=True)
    st.download_button("📥 Scarica risultati filtrati (CSV)", df_filtrato.to_csv(index=False).encode("utf-8"), "risultati.csv", "text/csv")

    st.markdown('</div>', unsafe_allow_html=True)
