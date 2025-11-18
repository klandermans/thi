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

# --- Streamlit App ---
st.set_page_config(page_title="THI Voorspelling", layout="wide")
st.title("THI Voorspelling en Visualisatie")

# --- Postal Code Form ---
with st.form("postal_code_form"):
    postal_code = st.text_input("Voer een postcode in (bijv. 8937 AC):")
    submitted = st.form_submit_button("Haal voorspelling op")

if submitted:
    if not postal_code:
        st.error("Voer een postcode in.")
    else:
        with st.spinner("Locatie opzoeken..."):
            try:
                geolocator = Nominatim(user_agent="thi_streamlit_app")
                location = geolocator.geocode(postal_code, country_codes="NL")
            except Exception as e:
                st.error(f"Fout bij het opzoeken van de locatie: {e}")
                location = None

        if location:
            st.success(f"Locatie gevonden: **{location.address}**")
            lat, lon = location.latitude, location.longitude

            col1, col2 = st.columns(2)

            with col1:
                # --- Buienradar Map ---
                st.subheader("Buienradar")
                buienradar_url = f"https://gadgets.buienradar.nl/gadget/zoommap/?lat={lat}&lng={lon}&overname=2&zoom=8&naam={location.address.split(',')[0]}&size=3&voor=0"
                st.components.v1.iframe(buienradar_url, width=550, height=512, scrolling=False)

            with col2:
                # --- Weather Forecast ---
                st.subheader("Weersvoorspelling en THI")
                with st.spinner("Weersvoorspelling ophalen..."):
                    try:
                        # Meteoserver API
                        api_key = "8f58861a52" # From user's snippet
                        api_url = f"https://data.meteoserver.nl/api/uurverwachting.php?lat={lat}&long={lon}&key={api_key}"
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
                        st.error(f"Fout bij het ophalen van de weersvoorspelling: {e}")
                    except (KeyError, ValueError) as e:
                        st.error(f"Fout bij het verwerken van de weersdata: {e}")

        else:
            st.error(f"Kon geen locatie vinden voor postcode: {postal_code}")
