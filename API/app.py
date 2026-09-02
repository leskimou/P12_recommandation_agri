"""Interface Streamlit pour l'API de prediction de rendement agricole.

Ne contient aucune logique ML : appelle simplement l'API FastAPI (/predict, /recommend).
"""

import os

import pandas as pd
import requests
import streamlit as st

API_URL = os.environ.get("API_URL", "http://localhost:8000")

REGIONS = ["East", "North", "South", "West"]
SOIL_TYPES = ["Chalky", "Clay", "Loam", "Peaty", "Sandy", "Silt"]
CROPS = ["Barley", "Cotton", "Maize", "Rice", "Soybean", "Wheat"]
WEATHER_CONDITIONS = ["Cloudy", "Rainy", "Sunny"]

st.set_page_config(page_title="Prediction de rendement agricole", page_icon="🌾")
st.title("🌾 Prediction de rendement agricole")

mode = st.radio("Mode", ["Prediction", "Recommandation"], horizontal=True)

st.subheader("Contexte")
col1, col2 = st.columns(2)
with col1:
    region = st.selectbox("Region", REGIONS)
    soil_type = st.selectbox("Type de sol", SOIL_TYPES)
    weather = st.selectbox("Meteo", WEATHER_CONDITIONS)
    days_to_harvest = st.slider("Jours avant recolte", 60, 149, 100)
with col2:
    rainfall = st.slider("Precipitations (mm)", 100.0, 1000.0, 550.0)
    temperature = st.slider("Temperature (°C)", 15.0, 40.0, 25.0)
    pesticides = st.slider("Pesticides (tonnes, proxy)", 13735.0, 20043.0, 16300.0)

col3, col4 = st.columns(2)
with col3:
    fertilizer_used = st.checkbox("Engrais utilise", value=True)
with col4:
    irrigation_used = st.checkbox("Irrigation utilisee", value=True)

context = {
    "Region": region,
    "Soil_Type": soil_type,
    "Rainfall_mm": rainfall,
    "Temperature_Celsius": temperature,
    "Fertilizer_Used": fertilizer_used,
    "Irrigation_Used": irrigation_used,
    "Weather_Condition": weather,
    "Days_to_Harvest": days_to_harvest,
    "Pesticides_tonnes_avg_proxy": pesticides,
}

if mode == "Prediction":
    crop = st.selectbox("Culture", CROPS)

    if st.button("Predire"):
        try:
            response = requests.post(f"{API_URL}/predict", json={**context, "Crop": crop})
            response.raise_for_status()
            result = response.json()
            st.metric(f"Rendement predit pour {result['Crop']}", f"{result['predicted_yield']:.2f} t/ha")
        except requests.RequestException as e:
            st.error(f"Erreur lors de l'appel a l'API : {e}")

else:
    if st.button("Recommander"):
        try:
            response = requests.post(f"{API_URL}/recommend", json=context)
            response.raise_for_status()
            results = response.json()
            df = pd.DataFrame(results).rename(
                columns={"Crop": "Culture", "predicted_yield": "Rendement predit (t/ha)"}
            )
            st.bar_chart(df.set_index("Culture"))
            st.dataframe(df, width="stretch", hide_index=True)
        except requests.RequestException as e:
            st.error(f"Erreur lors de l'appel a l'API : {e}")
