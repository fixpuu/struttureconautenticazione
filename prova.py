import os
import sys
import time
import hashlib
import subprocess                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 
import pyautogui
import webbrowser
from keyauth import api
from time import sleep
import pandas as pd
import streamlit as st


print("Connecting to our servers")


def progress_bar(duration):
    steps = 50
    interval = duration / steps

    print("Loading the script:")
    for i in range(steps + 1):
        progress = i * 100 / steps
        bar_length = int(progress / 2)
        print("\r[{:<50}] {:.0f}%".format("=" * bar_length, progress), end="")
        time.sleep(interval)
    print()

duration = 4
progress_bar(duration)


"""
https://www.fancytextpro.com/BigTextGenerator
"""
print("""
 $$$$$$\   $$$$$$\  $$$$$$\       $$\       $$$$$$\   $$$$$$\  $$$$$$\ $$\   $$\ 
$$  __$$\ $$  __$$\ \_$$  _|      $$ |     $$  __$$\ $$  __$$\ \_$$  _|$$$\  $$ |
$$ /  \__|$$ /  $$ |  $$ |        $$ |     $$ /  $$ |$$ /  \__|  $$ |  $$$$\ $$ |
$$ |$$$$\ $$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |$$$$\   $$ |  $$ $$\$$ |
$$ |\_$$ |$$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |\_$$ |  $$ |  $$ \$$$$ |
$$ |  $$ |$$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |  $$ |  $$ |  $$ |\$$$ |
\$$$$$$  | $$$$$$  |$$$$$$\       $$$$$$$$\ $$$$$$  |\$$$$$$  |$$$$$$\ $$ | \$$ |
 \______/  \______/ \______|      \________|\______/  \______/ \______|\__|  \__|
                                                                                 
                                                                                 
                                                                                 
developer: @mattygoi
""")

def limpar_terminal():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def getchecksum():
    md5_hash = hashlib.md5()
    file = open(''.join(sys.argv), "rb")
    md5_hash.update(file.read())
    digest = md5_hash.hexdigest()
    return digest

### CHANGE YOUR KEYAUTH 
keyauthapp = api(
    name = "strutture",
    ownerid = "l9G6gNHYVu",
    secret="8f89f06f3cec7207ad7ac9e1786057396d0bb6c587ba8f6fc548ba4f244c78b1",
    version = "1.0",
    hash_to_check = getchecksum()
)

def answer():
    try:
        print("""1. Key
2. Contact us
3. Exit
              
        """)
        ans = input("Select Option: ")
        if ans == "1":
            key = input('Enter your license: ')
            keyauthapp.license(key)
        elif ans == "2":
            webbrowser.open("https://discord.gg/YOUR_LINK")
            os.system("TASKKILL /F /IM cmd.exe")
            sys.exit()
        elif ans == "3":
            os.system("TASKKILL /F /IM cmd.exe")
            sys.exit()
        else:
            print("\nInvalid option")
            sleep(1)
            answer()
    except KeyboardInterrupt:
        os._exit(1)

answer()
# region USER DATA
print("\nUser data: ")
print("Your key: " + keyauthapp.user_data.username)
print("Hardware-Id: " + keyauthapp.user_data.hwid)
print("Thanks for choosing us :)")
print("")
time.sleep(3)
limpar_terminal()

subs = keyauthapp.user_data.subscriptions

def ascii():
    ascii = print("""
 $$$$$$\   $$$$$$\  $$$$$$\       $$\       $$$$$$\   $$$$$$\  $$$$$$\ $$\   $$\ 
$$  __$$\ $$  __$$\ \_$$  _|      $$ |     $$  __$$\ $$  __$$\ \_$$  _|$$$\  $$ |
$$ /  \__|$$ /  $$ |  $$ |        $$ |     $$ /  $$ |$$ /  \__|  $$ |  $$$$\ $$ |
$$ |$$$$\ $$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |$$$$\   $$ |  $$ $$\$$ |
$$ |\_$$ |$$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |\_$$ |  $$ |  $$ \$$$$ |
$$ |  $$ |$$ |  $$ |  $$ |        $$ |     $$ |  $$ |$$ |  $$ |  $$ |  $$ |\$$$ |
\$$$$$$  | $$$$$$  |$$$$$$\       $$$$$$$$\ $$$$$$  |\$$$$$$  |$$$$$$\ $$ | \$$ |
 \______/  \______/ \______|      \________|\______/  \______/ \______|\__|  \__|
                                                                                 
                                                                                 
                                                                                 
developer: @mattygoi
                                       
""")
    

pyautogui.alert("MADE BY: AmigoxD", title="Script Info")

ascii()

print("The script will start in 5 seconds...")
time.sleep(5)


@st.cache_data
def load_data():
    # Carica il CSV dalla stessa cartella dello script
    path = "STRUTTURE_cleaned.csv"
    df = pd.read_csv(path)
    return df

df = load_data()

st.title("🔍 Ricerca STRUTTURE")

# Filtri
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
