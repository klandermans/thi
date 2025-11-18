import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# --- THI Calculation Functions (ongewijzigd) ---
def calculate_thi(temp, rh):
    """Calculates the Temperature-Humidity Index (THI)."""
    return 0.8 * temp + (rh / 100) * (temp - 14.4) + 46.4

def get_thi_alert(thi):
    """Returns the alert status based on the THI."""
    return "Alert" if thi >= 72 else "Geen alert"

# --- CONFIGURATIE (Leeuwarden Hardcoded) ---
API_KEY = "8f58861a52" 
LAT = 53.2013  # Leeuwarden
LON = 5.7601   # Leeuwarden
LOCATIE_NAAM = "Leeuwarden" 

# --- Streamlit App ---
st.set_page_config(page_title="THI Voorspelling", layout="wide")

# ... (Sidebar code blijft hetzelfde) ...
with st.sidebar:
    st.header("🐄 Heatstress App 🛠️")
    try:
        st.image("images/cowboy.png", caption="The Dairy Campus Cowboys")
    except FileNotFoundError:
        st.warning("Afbeelding 'cowboy.png' niet gevonden.")    
    st.markdown("""
    <p>The Dairy <b style="color:red">Heat</b>stress App was forged in the digital frontier by the Dairy Campus Cowboys.</p>
    <br>              
    <p>⭐ Anna, our shining star, tolerated zero 'fluff' on the Frontier.</p>
    <p>🤠 Paul, the sherrif supplied the vital and safe context.</p> 
    <p>💻 Bert, responsible for disrupting hacks and Beer & bytes</p>
    <p>The Dairy Campus Cowboys engineered this  application to deliver heat stress insights, without the fluff.</P>
    """, unsafe_allow_html=True)
    

# --- Hoofd Titel ---
st.markdown("<h1><font color=red>HEAT</font> stress APP</h1>", unsafe_allow_html=True)

# --- Postal Code Form (staat er voor spek en bonen) ---
with st.form("postal_code_form"):
    postal_code = st.text_input("Voer een postcode in (bijv. 8937 AC):")
    submitted = st.form_submit_button("Haal voorspelling op")

# st.info(f"De weersvoorspelling wordt **altijd** getoond voor **{LOCATIE_NAAM}** i.v.m. HTTP errors.")

# --- DATA EN VISUALISATIE voor Leeuwarden ---
col2, col1 = st.columns(2)

# --- Buienradar Map (Wordt direct getoond) ---
with col1:
    st.subheader("Buienradar")
    buienradar_url = f"https://gadgets.buienradar.nl/gadget/zoommap/?lat={LAT}&lng={LON}&overname=2&zoom=8&naam={LOCATIE_NAAM}&size=3&voor=0"
    st.components.v1.iframe(buienradar_url, width=550, height=512, scrolling=False)

# --- Weersvoorspelling en THI Ophalen (Debug-modus) ---
with col2:
    st.subheader("Heatstress voorspelling")
    forecast_list = []
    
    with st.spinner("Weersvoorspelling ophalen..."):
        try:
            api_url = f"https://data.meteoserver.nl/api/uurverwachting.php?lat={LAT}&long={LON}&key={API_KEY}"
            r = requests.get(api_url)
            
            # 1. API Status Check
            if r.status_code != 200:
                # DEBUG OUTPUT: Toon de exacte fout van de server
                st.error(f"Fout bij API-call (Status Code {r.status_code}):")
                st.code(r.text) # Toon de ruwe server respons
                st.stop() # Stop de uitvoering hier
                
            # 2. JSON Parsing
            try:
                data = r.json()["data"]
            except KeyError:
                st.error("JSON Error: De API-respons bevat niet de verwachte sleutel 'data'.")
                st.code(r.json())
                st.stop() # Stop de uitvoering hier




            # 3. Data Processing
            for forecast in data:
                # Vereenvoudigde, werkende logica teruggehaald
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
                    "THI Buiten": f"{thi_out:.1f}", # Voeg THI Buiten toe aan tabel
                    "THI Binnen": f"{thi_in:.1f}",
                    "Advies": alert
                })
            
            df = pd.DataFrame(forecast_list)
            df["Tijd"] = pd.to_datetime(df["Tijd"])
            df["Buiten"] = pd.to_numeric(df["THI Buiten"])
            df["Binnen"] = pd.to_numeric(df["THI Binnen"])
            fig = go.Figure()
            fig.update_yaxes(range=[30, 85])

            datum_min = df["Tijd"].min()
            datum_max = df["Tijd"].max()

            # ... (Plotly layout en shapes code blijft hetzelfde) ...
            fig.update_layout(
                shapes=[
                    dict(type="rect", xref="x", yref="y", x0=datum_min, x1=datum_max, y0=0, y1=68, fillcolor="lightgreen", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=datum_min, x1=datum_max, y0=68, y1=72, fillcolor="yellow", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=datum_min, x1=datum_max, y0=72, y1=78, fillcolor="orange", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=datum_min, x1=datum_max, y0=78, y1=82, fillcolor="red", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=datum_min, x1=datum_max, y0=82, y1=100, fillcolor="darkred", opacity=0.2, layer="below", line_width=0),
                ],
                # title=dict(text=f"Voorspelde THI voor {LOCATIE_NAAM}"),
                # xaxis_title="Tijd",
                yaxis_title="THI",
                hovermode="x unified",
                legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.3, # Positioneer de legenda onder de plot
                        xanchor="center",
                        x=0.5
                    )                
            )

            # Lijnen toevoegen (gebruiken nu de numerieke kolommen)
            fig.add_trace(go.Scatter(x=df["Tijd"], y=df["Binnen"], name="THI Binnen (Geschat)", mode="lines+markers", line=dict(color='white', width=1)))
            fig.add_trace(go.Scatter(x=df["Tijd"], y=df["Buiten"], name="THI Buiten", mode="lines", line=dict(color='blue', dash='dash')))

            st.plotly_chart(fig, use_container_width=True)

            df = pd.DataFrame(forecast_list)

            st.dataframe(df, hide_index=True, use_container_width=True)

        except requests.exceptions.RequestException as e:
            # Netwerk/HTTP fout
            st.error(f"Netwerkfout bij API: {e}")
        except Exception as e:
            # Algemene verwerkingsfout
            st.error(f"Fout bij het verwerken van de data (Meteoserver): {e}")