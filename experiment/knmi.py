"""
Download en lees de KNMI HARMONIE-AROME weersvoorspelling
voor Leeuwarden (53.2 N, 5.8 E) via de KNMI Open Data API.
"""

import os
import requests
import xarray as xr
import numpy as np

# === CONFIG ===
API_BASE = "https://api.dataplatform.knmi.nl/open-data/v1"
DATASET = "harmonie_arome_cy43_nl_sfc"     # surface-level modeldata Nederland
VERSION = "latest"

# KNMI anonieme API-key (geldig tot 1 juli 2026)
API_KEY = (
    "eyJvcmciOiI1ZTU1NGUxOTI3NGE5NjAwMDEyYTNlYjEiLCJpZCI6ImVlNDFjMWI0MjlkODQ2MThiNWI4"
    "ZDViZDAyMTM2YTM3IiwiaCI6Im11cm11cjEyOCJ9"
)
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Accept": "application/json"}

# Coördinaten Leeuwarden
target_lat, target_lon = 53.2, 5.8

# === 1. Lijst bestanden ophalen ===
print("Ophalen lijst van beschikbare bestanden...")
r = requests.get(f"{API_BASE}/datasets/{DATASET}/versions/{VERSION}/files", headers=HEADERS)
r.raise_for_status()
files = r.json()["files"]

# Filter alleen GRIB2-bestanden
grib_files = [f["filename"] for f in files if f["filename"].endswith(".grib2")]
if not grib_files:
    raise RuntimeError("Geen GRIB2-modelbestanden gevonden in dataset.")

# Gebruik het nieuwste bestand (meest recente modelrun)
latest_file = sorted(grib_files)[-1]
print(f"Nieuwste bestand gevonden: {latest_file}")

# === 2. Download-URL ophalen ===
r2 = requests.get(
    f"{API_BASE}/datasets/{DATASET}/versions/{VERSION}/files/{latest_file}/url",
    headers=HEADERS,
)
r2.raise_for_status()
download_url = r2.json()["temporaryDownloadUrl"]

# === 3. Bestand downloaden ===
local_file = "harmonie_latest.grib2"
print(f"Downloaden van {latest_file} ...")
with requests.get(download_url, stream=True) as rf:
    rf.raise_for_status()
    with open(local_file, "wb") as f:
        for chunk in rf.iter_content(8192):
            f.write(chunk)
print(f"Bestand opgeslagen als {local_file}")

# === 4. Inlezen met xarray/cfgrib ===
print("Bestand openen met xarray (engine=cfgrib)...")
ds = xr.open_dataset(local_file, engine="cfgrib")
print("Variabelen beschikbaar:", list(ds.data_vars)[:10])

# === 5. Dichtsbijzijnde gridpunt bij Leeuwarden vinden ===
lat = ds["latitude"].values
lon = ds["longitude"].values
ilat = np.abs(lat - target_lat).argmin()
ilon = np.abs(lon - target_lon).argmin()
print(f"Dichtstbijzijnde gridpunt: lat={lat[ilat]:.3f}, lon={lon[ilon]:.3f}")

# === 6. Temperatuur & wind uitlezen ===
if "t2m" in ds:       # temperatuur op 2 m hoogte (Kelvin)
    temp = ds["t2m"][:, ilat, ilon] - 273.15
    print("\nTemperatuur (°C) komende uren:")
    for t, v in zip(ds["time"].values, temp.values):
        print(str(t)[:19], f"{v:.1f} °C")

if "ff10m" in ds:     # windsnelheid op 10 m hoogte (m/s)
    wind = ds["ff10m"][:, ilat, ilon]
    print("\nWindsnelheid (m/s) komende uren:")
    for t, v in zip(ds["time"].values, wind.values):
        print(str(t)[:19], f"{v:.1f} m/s")

print("\n✅ Klaar. Data uit HARMONIE-AROME succesvol opgehaald.")

