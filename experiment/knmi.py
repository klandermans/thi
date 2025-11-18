"""
Download en verwerk de weersvoorspelling van meteoserver.nl
om de THI (Temperature-Humidity Index) te berekenen en een alert te genereren.
"""

import requests
import os

LOG_FILE = "thi.log"
API_URL = "https://data.meteoserver.nl/api/uurverwachting.php?locatie=Goutum&key=8f58861a52"

def calculate_thi(temp, rh):
    """Berekent de Temperature-Humidity Index (THI)."""
    return 0.8 * temp + (rh / 100) * (temp - 14.4) + 46.4

def get_thi_alert(thi):
    """Retourneert de alert status op basis van de THI."""
    if thi >= 72:
        return "Alert"
    else:
        return "Geen alert"

def log_output(message):
    """Schrijft output naar de console en naar een logfile."""
    print(message)
    with open(LOG_FILE, "a") as f:
        f.write(message + "\n")

# Verwijder oude logfile
if os.path.exists(LOG_FILE):
    os.remove(LOG_FILE)

# === 1. Data ophalen van meteoserver.nl ===
log_output("Ophalen van weersvoorspelling van meteoserver.nl...")
try:
    r = requests.get(API_URL)
    r.raise_for_status()
    data = r.json()["data"]
    log_output("Data succesvol opgehaald.")
except requests.exceptions.RequestException as e:
    log_output(f"Fout bij het ophalen van de data: {e}")
    exit()
except KeyError:
    log_output("Fout: 'data' key niet gevonden in de API response.")
    exit()

# === 2. THI berekenen en loggen ===
log_output("\nTHI voorspelling komende uren:")
log_output("Tijdstip, Temp (°C), RV (%), THI Buiten, THI Binnen, Advies")

for forecast in data:
    try:
        time_nl = forecast["tijd_nl"]
        temp_out = float(forecast["temp"])
        rh = float(forecast["rv"])

        # Bereken THI voor buiten
        thi_out = calculate_thi(temp_out, rh)

        # Bereken voorspelde binnentemperatuur en THI voor binnen
        temp_in = 0.81 * temp_out + 5.60
        thi_in = calculate_thi(temp_in, rh)
        
        alert = get_thi_alert(thi_in)

        log_output(f"{time_nl}, {temp_out:.1f}, {rh:.1f}, {thi_out:.1f}, {thi_in:.1f}, {alert}")

    except (KeyError, ValueError) as e:
        log_output(f"Fout bij het verwerken van een voorspelling: {e}")
        continue

log_output("\n✅ Klaar. Data van meteoserver.nl succesvol verwerkt.")