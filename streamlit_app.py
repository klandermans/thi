import streamlit as st
import requests
from geopy.geocoders import Nominatim
import pandas as pd

# --- THI Calculation Functions ---
def calculate_thi(temp, rh):
    """Calculates the Temperature-Humidity Index (THI)."""
    return 0.8 * temp + (rh / 100) * (temp - 14.4) + 46.4

def get_thi_alert(thi):
    """Returns the alert status based on the THI."""
    if thi >= 72:
        return "Alert"
    else:
        return "Geen alert"

# --- CONFIGURATIE ---
API_KEY = "8f58861a52" 
USER_AGENT = "thi_streamlit_app" 

# --- Streamlit App ---
st.set_page_config(page_title="THI Voorspelling", layout="wide")

# --- ZIJBALK (De "Hamburger" met Credits) ---
with st.sidebar:
    st.header("🐄 Heatstress App 🛠️")

    try:
        st.image("images/cowboy.png", caption="The Dairy Campus Cowboys")
    except FileNotFoundError:
        st.warning("Afbeelding 'cowboy.png' niet gevonden.")    
    text = """
    
    <p>The Dairy <b style="color:red">Heat</b>stress App was forged in the digital frontier by the Dairy Campus Cowboys.</p>
    <br>              
    <p>⭐ Anna, our shining star, tolerated zero 'fluff' on the Frontier.</p>

    <p>🤠 Paul, the sherrif supplied the vital and safe context.</p> 

    <p>💻 Bert, responsible for disrupting hacks and Beer & bytes</p>

    <p>The Dairy Campus Cowboys engineered this  application to deliver heat stress insights, without the fluff.</P>
    """
    st.markdown(text, unsafe_allow_html=True)

    

# --- Hoofd Titel ---
title = ("<h1><font color=red>HEAT</font> stress APP</h1>")
st.markdown(title, unsafe_allow_html=True)

# --- Postal Code Form ---
with st.form("postal_code_form"):
    postal_code = st.text_input("Voer een postcode in (bijv. 8937 AC):")
    submitted = st.form_submit_button("Haal voorspelling op")

if submitted:
    if not postal_code:
        st.error("Voer een postcode in.")
    else:
        location = None
        # 1. LOCATIE OPLOSSEN (Geocoding)
        with st.spinner("Locatie opzoeken..."):
            try:
                geolocator = Nominatim(user_agent=USER_AGENT)
                location = geolocator.geocode(postal_code, country_codes="NL")
            except Exception as e:
                st.error(f"Fout bij het opzoeken van de locatie: {e}")
                
        # 2. DATA EN VISUALISATIE (alleen als locatie succesvol is)
        if location:
            st.success(f"Locatie gevonden: **{location.address}**")
            lat, lon = location.latitude, location.longitude

            col1, col2 = st.columns(2)

            with col1:
                # --- Buienradar Map ---
                st.subheader("Buienradar")
                naam = location.address.split(',')[0]
                buienradar_url = f"https://gadgets.buienradar.nl/gadget/zoommap/?lat={lat}&lng={lon}&overname=2&zoom=8&naam={naam}&size=3&voor=0"
                st.components.v1.iframe(buienradar_url, width=550, height=512, scrolling=False)

            with col2:
                # --- Weersvoorspelling en THI Ophalen ---
                st.subheader("Weersvoorspelling en THI")
                with st.spinner("Weersvoorspelling ophalen..."):
                    try:
                        api_url = f"https://data.meteoserver.nl/api/uurverwachting.php?lat={lat}&long={lon}&key={API_KEY}"
                        r = requests.get(api_url)
                        r.raise_for_status() 
                        data = r.json()["data"]

                        # Process data
                        forecast_list = []
                        for forecast in data:
                            temp_out = float(forecast["temp"])
                            rh = float(forecast["rv"])
                            
                            temp_in = 0.81 * temp_out + 5.60 
                            
                            thi_out = calculate_thi(temp_out, rh)
                            thi_in = calculate_thi(temp_in, rh)
                            alert = get_thi_alert(thi_in)

                            forecast_list.append({
                                "Tijd": forecast["tijd_nl"],
                                "Temp (°C)": f"{temp_out:.1f}",
                                "RV (%)": f"{rh:.1f}",
                                "THI Buiten": f"{thi_out:.1f}",
                                "THI Binnen": f"{thi_in:.1f}",
                                "Advies": alert
                            })
                        
                        df = pd.DataFrame(forecast_list)
                        st.dataframe(df, hide_index=True, use_container_width=True)

                    except requests.exceptions.RequestException as e:
                        st.error(f"Fout bij het ophalen van de weersvoorspelling (Meteoserver): {e}")
                    except (KeyError, ValueError, TypeError) as e:
                        st.error(f"Fout bij het verwerken van de weersdata: {e}")

        else:
            st.error(f"Kon de locatie niet oplossen voor postcode: {postal_code}")