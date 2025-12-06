import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np
import folium
from streamlit_folium import st_folium

API_URL = "http://127.0.0.1:8000/predict"

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(page_title="FWI Predictor Dashboard", page_icon="🔥", layout="wide")
st.markdown("<h1 style='text-align:center;'>🔥 Fire Weather Index (FWI) Prediction Dashboard</h1>", unsafe_allow_html=True)
st.write("---")

# ----------------------------------------------------
# SESSION STATE INITIALIZATION
# ----------------------------------------------------
if "fwi_value" not in st.session_state:
    st.session_state.fwi_value = None

if "category" not in st.session_state:
    st.session_state.category = None

if "deviations" not in st.session_state:
    st.session_state.deviations = None

if "map_obj" not in st.session_state:
    st.session_state.map_obj = None

# ----------------------------------------------------
# INPUT SLIDERS
# ----------------------------------------------------
st.subheader("📥 Input Environmental Parameters")

col1, col2, col3 = st.columns(3)

with col1:
    Temperature = st.slider("🌡 Temperature (°C)", 0, 50, 30)
    RH = st.slider("💧 Relative Humidity (%)", 0, 100, 40)
    WS = st.slider("🍃 Wind Speed (km/h)", 0, 100, 15)

with col2:
    Rain = st.slider("🌧 Rain (mm)", 0.0, 20.0, 0.5)
    FFMC = st.slider("🔥 FFMC", 0.0, 100.0, 85.0)
    DMC = st.slider("🔥 DMC", 0.0, 200.0, 50.0)

with col3:
    DC = st.slider("🔥 DC", 0.0, 1000.0, 150.0)
    ISI = st.slider("⚡ ISI", 0.0, 50.0, 10.0)
    BUI = st.slider("📛 BUI", 0.0, 200.0, 30.0)

data = {
    "Temperature": Temperature,
    "RH": RH,
    "Ws": WS,
    "Rain": Rain,
    "FFMC": FFMC,
    "DMC": DMC,
    "DC": DC,
    "ISI": ISI,
    "BUI": BUI
}

# ----------------------------------------------------
# BUTTON → SAVE RESULT IN SESSION STATE
# ----------------------------------------------------
if st.button("🚀 Predict FWI", use_container_width=True):

    try:
        response = requests.post(API_URL, json=data).json()
        fwi_value = response["FWI_prediction"]

        # Store prediction
        st.session_state.fwi_value = fwi_value

        # Categorization
        def categorize_fwi(fwi):
            if fwi < 5: return "Low Risk", "🟢"
            elif fwi < 15: return "Moderate Risk", "🟡"
            elif fwi < 30: return "High Risk", "🟠"
            else: return "Extreme Risk", "🔴"

        category, emoji = categorize_fwi(fwi_value)
        st.session_state.category = (category, emoji)

        # Analysis
        df = pd.DataFrame([data])
        deviations = (df.loc[0] - df.loc[0].mean()).abs().sort_values(ascending=False)
        st.session_state.deviations = deviations

        # MAP CREATION
        lat, lon = 20.5937, 78.9629

        def risk_color(f):
            if f < 5: return "green"
            elif f < 15: return "yellow"
            elif f < 30: return "orange"
            return "red"

        color = risk_color(fwi_value)

        m = folium.Map(location=[lat, lon], zoom_start=5)
        folium.CircleMarker(
            location=[lat, lon],
            radius=12,
            popup=f"FWI: {fwi_value:.2f}",
            color=color,
            fill=True,
            fill_color=color,
        ).add_to(m)

        st.session_state.map_obj = m

    except Exception as e:
        st.error("❌ API Error")
        st.code(str(e))

# ----------------------------------------------------
# DISPLAY STABLE OUTPUT (NEVER DISAPPEARS)
# ----------------------------------------------------
if st.session_state.fwi_value is not None:

    fwi_value = st.session_state.fwi_value
    category, emoji = st.session_state.category
    deviations = st.session_state.deviations

    st.success(f"### 🔥 Predicted Fire Weather Index (FWI): **{fwi_value:.2f}**")
    st.markdown(f"""
    <div style='padding:15px;border-radius:10px;background-color:#262730;color:white;text-align:center;'>
        <h3>{emoji} Fire Danger Level: <b>{category}</b></h3>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("📊 Analytical Insights")

    st.write("### ⚠ Factors With Highest Contribution")
    st.bar_chart(deviations)

    st.subheader("📌 Top Parameter Contribution Pie Chart")
    pie_df = deviations.head(5)
    fig_pie = px.pie(
        names=pie_df.index,
        values=pie_df.values,
        title="Top Influencing Parameters"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("🌍 FWI Risk Map")
    st_folium(st.session_state.map_obj, width=900, height=500)

else:
    st.info("👆 Adjust sliders and click **Predict FWI** to begin.")
