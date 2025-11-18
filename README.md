
# THI Forecast & Alert System

## Overview
This system monitors predicted stable conditions based on KNMI weather forecasts. It sends a WhatsApp alert to the farmer when the calculated Temperature Humidity Index (THI) exceeds a critical threshold.

## Logic & Model
1.  **Data Ingestion**: Fetch weather forecast (Temperature & Humidity) from **KNMI API**.
2.  **Indoor Prediction**: Predict indoor temperature ($T_{in}$) based on outdoor forecast ($T_{out}$) using the linear regression model (derived from "Hendrik Jan" analysis):
    $$T_{in} = 0.81 \cdot T_{out} + 5.60$$
3.  **THI Calculation**:
    $$THI = 0.8 \cdot T_{in} + \frac{RH}{100} \cdot (T_{in} - 14.4) + 46.4$$
4.  **Notification**: Trigger WhatsApp message if $THI > THI_{limit}$.

## Validation
The model has been validated via SQL analysis (`validatie.sql`) by comparing:
* **Observed Indoor THI**: Based on actual sensors (Koenders/climate computer).
* **Calculated Indoor THI**: Derived from external weather station data passed through the prediction model.

## Prerequisites
* Python 3.9+
* KNMI Data Platform Account
* WhatsApp Provider (Twilio / Meta)

## Installation

1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
````

## Configuration (`.env`)

```ini
# KNMI Source
KNMI_API_KEY=your_key
STATION_ID=260

# Indoor Prediction Model (Linear Regression)
MODEL_SLOPE=0.81
MODEL_INTERCEPT=5.60

# Limits
THI_THRESHOLD=72

# Notification
WHATSAPP_PROVIDER_TOKEN=your_token
PHONE_NUMBER=+31612345678
```

## Usage

```bash
python src/main.py
```

```
