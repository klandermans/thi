import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# --- Config & CSS (Max Width 800px) ---
st.set_page_config(page_title="THI App", layout="wide")

# CSS: Maximaliseer de hoofdbody op 800px voor mobiele apps (KISS)
st.markdown(
    """
    <style>
    /* Selecteert de hoofdcontainer en stelt de maximale breedte in */
    .block-container {
        max-width: 800px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- THI Calculation Functions ---
def calculate_thi(temp, rh):
    """Bereken de Temperature Humidity Index (THI)."""
    return 0.8 * temp + (rh / 100) * (temp - 14.4) + 46.4

def get_thi_alert(thi):
    """Bepaalt de alertstatus op basis van de THI (binnen)."""
    return "Alert" if thi >= 72 else "Geen alert"

# --- Heatstress status box ---
def stress_color_box(thi):
    """Geeft een visuele statusbox weer op basis van de maximale THI."""
    if thi < 68:
        color = "green"
        text = "Geen stress"
    elif thi < 72:
        color = "orange"
        text = "Stress in aantocht"
    else:
        color = "red"
        text = "Stress!"

    st.markdown(
        f"""
        <div style="padding:20px; border-radius:10px; background-color:{color};
                    color:white; text-align:center; font-size:24px; font-weight:700;">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )


# -------------------------------------------------------------------
# ----------------------   PAGE LOGIC (ROUTER)  ----------------------
# -------------------------------------------------------------------

# Init session state
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------------- SIDEBAR = HAMBURGER MENU -----------------------
with st.sidebar:
    st.markdown("## ☰ Menu")
    
    # Update navigatie met "Inschrijven"
    nav = st.radio(
        "Navigatie",
        ["Dashboard", "Inschrijven", "About"],
        label_visibility="collapsed"
    )

    if nav == "Dashboard":
        st.session_state.page = "home"
    elif nav == "Inschrijven":
        st.session_state.page = "register"
    else:
        st.session_state.page = "about"
        
    # Zoekmenu verplaatst naar de sidebar (hamburger menu)
    st.markdown("---")
    with st.form("postal_code_form_sidebar"): # Unieke key
        st.text_input("Voer een postcode in (bijv. 8937 AC):", key="sidebar_postcode_input")
        st.form_submit_button("Haal voorspelling op")


# -------------------------------------------------------------------
# -------------------------- HOME PAGE ------------------------------
# -------------------------------------------------------------------

def page_home():
    API_KEY = "8f58861a52"
    LAT = 53.2013
    LON = 5.7601
    LOCATIE_NAAM = "Leeuwarden"

    st.markdown("<h1><font color=red>HEAT</font> stress APP</h1>", unsafe_allow_html=True)

    # st.subheader("Heatstress voorspelling")
    forecast_list = []

    with st.spinner("Weersvoorspelling ophalen..."):
        try:
            api_url = f"https://data.meteoserver.nl/api/uurverwachting.php?lat={LAT}&long={LON}&key={API_KEY}"
            r = requests.get(api_url)

            if r.status_code != 200:
                st.error(f"API error {r.status_code}")
                st.code(r.text)
                return

            data = r.json()["data"]

            for forecast in data:
                temp_out = float(forecast["temp"])
                rh = float(forecast["rv"])
                # Vereenvoudigde berekening voor binnentemperatuur
                temp_in = 0.81 * temp_out + 5.60

                thi_out = calculate_thi(temp_out, rh)
                thi_in = calculate_thi(temp_in, rh)

                forecast_list.append({
                    "Tijd": forecast["tijd_nl"],
                    "Temp (°C)": f"{temp_out:.1f}",
                    "RV (%)": f"{rh:.1f}",
                    "THI Buiten": f"{thi_out:.1f}",
                    "THI Binnen": f"{thi_in:.1f}",
                    "Advies": get_thi_alert(thi_in)
                })

            df = pd.DataFrame(forecast_list)
            df["Tijd"] = pd.to_datetime(df["Tijd"])
            df["Buiten"] = pd.to_numeric(df["THI Buiten"])
            df["Binnen"] = pd.to_numeric(df["THI Binnen"])

            # ---------------- STATUS BOX -------------------
            max_thi = df["Binnen"].max()
            stress_color_box(max_thi)

            # ---------------- PLOT -------------------
            fig = go.Figure()
            fig.update_yaxes(range=[30, 85])

            dmin = df["Tijd"].min()
            dmax = df["Tijd"].max()
            
            # THI Zone markeringen
            fig.update_layout(
                shapes=[
                    dict(type="rect", xref="x", yref="y", x0=dmin, x1=dmax, y0=0, y1=68, fillcolor="lightgreen", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=dmin, x1=dmax, y0=68, y1=72, fillcolor="yellow", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=dmin, x1=dmax, y0=72, y1=78, fillcolor="orange", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=dmin, x1=dmax, y0=78, y1=82, fillcolor="red", opacity=0.2, layer="below", line_width=0),
                    dict(type="rect", xref="x", yref="y", x0=dmin, x1=dmax, y0=82, y1=100, fillcolor="darkred", opacity=0.2, layer="below", line_width=0),
                ],
                yaxis_title="THI",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5
                )
            )

            fig.add_trace(go.Scatter(x=df["Tijd"], y=df["Binnen"], name="THI Binnen", mode="lines+markers", line=dict(color='white')))
            fig.add_trace(go.Scatter(x=df["Tijd"], y=df["Buiten"], name="THI Buiten", mode="lines", line=dict(color='blue', dash='dash')))

            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(f"Fout bij verwerken data: {e}")


        # st.subheader("Buienradar")
        url = f"https://gadgets.buienradar.nl/gadget/zoommap/?lat={LAT}&lng={LON}&overname=2&zoom=8&naam={LOCATIE_NAAM}&size=3&voor=0"
        st.components.v1.iframe(url, width=550, height=512, scrolling=False)


# -------------------------------------------------------------------
# -------------------------- REGISTER PAGE --------------------------
# -------------------------------------------------------------------

# -------------------------------------------------------------------
# -------------------------- REGISTER PAGE (FIXED) ------------------
# -------------------------------------------------------------------

def page_register():
    st.header("📲 Aanmelden voor Maatwerk Alert")
    
    st.markdown("Wil je ook een maatwerk alert op je telefoon ontvangen. Vul dan het onderstaand formulier in.")
    
    # Formulier met verplichte velden (gebruikt st.form_submit_button)
    with st.form("register_form"):
        st.subheader("Verplichte Gegevens")
        
        # 'required=True' verwijderd omdat dit argument niet wordt ondersteund.
        name = st.text_input("Naam", help="Volledige naam")
        ubn = st.text_input("UBN NUmmer", help="Uniek Bedrijfs Nummer (indien van toepassing)")
        address = st.text_input("Adres", help="Straat en huisnummer")
        city = st.text_input("Woonplaats", help="Plaatsnaam")
        phone = st.text_input("Telefoonnummer", help="Voor Whatsapp-alerts")
        birthdate = st.text_input("Geboortedatum", help="Voor leeftijdsgebonden advies (DD-MM-JJJJ)")
        bankrekening = st.text_input("Bankrekening", help="Voor incasso (IBAN)")   
        geslacht = st.selectbox("Geslacht", ["Man", "Vrouw"])
        soortBoerderij = st.selectbox("Soort Boerderij", ["Melkveebedrijf", "Vleesveebedrijf", "Overig"])   
        

        
        submitted = st.form_submit_button("Schrijf mij in")

        if submitted:
            # 1. Validatiecheck toevoegen (simuleert 'required')
            if not name or not address or not city or not phone:
                st.error("Vul AUB alle verplichte velden in. Elk veld is nodig.")
            else:
                # 2. 'Dummy' actie na succesvolle validatie
                st.success(f"Bedankt voor je inschrijving, {name}! Je ontvangt binnenkort een maatwerk alert.")
                st.info("Let op: Dit formulier slaat momenteel geen gegevens op en verstuurt geen echte alerts.")

# -------------------------------------------------------------------
# -------------------------- ABOUT PAGE ------------------------------
# -------------------------------------------------------------------

def page_about():
    st.header("🐄 Heatstress App 🛠️")
    try:
        st.image("images/cowboy.png", caption="The Dairy Campus Cowboys")
    except FileNotFoundError:
        st.warning("Afbeelding 'cowboy.png' niet gevonden.")    
    st.markdown("""
    <p>The Dairy <b style="color:red">Heat</b>stress App was forged in the digital frontier by the Dairy Campus Cowboys.</p>
    <br>              
    <p>⭐ Anna, our shining star, tolerated zero 'fluff' on the Frontier.</p>
    <p>🤠 Paul, the old sherrif supplied the vital and safe context.</p> 
    <p>💻 Bert, responsible for disrupting hacks, beers & bytes</p>
    <p>The Dairy Campus Cowboys engineered this  application to deliver heat stress insights, without the fluff.</P>
    """, unsafe_allow_html=True)
    

# -------------------------------------------------------------------
# -------------------------- ROUTER ------------------------------
# -------------------------------------------------------------------

if st.session_state.page == "home":
    page_home()
elif st.session_state.page == "register":
    page_register()
else:
    page_about()