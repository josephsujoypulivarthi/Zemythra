"""
Zemythra - Frontend Dashboard
Block D: Visualization & User Interaction
"""

import streamlit as st
import pandas as pd
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Zemythra Dashboard",
    layout="centered"
)

# -------------------------
# Sidebar Login
# -------------------------
st.sidebar.title("Login")

role = st.sidebar.selectbox(
    "Role",
    ["User", "Admin"]
)

# -------------------------
# User View
# -------------------------
if role == "User":
    st.title("Patient Risk Assessment")

    with st.form("risk_form"):
        age = st.number_input("Age", 1, 120)
        glucose = st.number_input("Glucose")
        bp = st.number_input("Systolic BP")
        submit = st.form_submit_button("Predict Risk")

    if submit:
        payload = {
        "age": age,
        "gender": 1,
        "sys_bp": bp,
        "dia_bp": 80,
        "glucose": glucose,
        "cholesterol": 200,
        "bmi": 25,
        "heart_rate": 75
    }

    try:
        response = requests.post(
            f"{API_URL}/predict",
            json=payload
        )

        result = response.json()

        st.subheader("Risk Output")

        st.metric("Risk Score", result["risk_score"])
        st.metric("Risk Level", result["risk_level"])

        if result["emergency"]:
            st.error("🚨 Emergency Risk Detected")
        else:
            st.success("No Emergency")

        st.subheader("📋 Clinical Recommendation")
        st.write(result["recommendation"])

        st.subheader("📊 Model Uncertainty")
        st.write(result["uncertainty"])

        st.subheader("📈 Future Risk Forecast")
        st.json(result["future_forecast"])

    except Exception:
        st.error("Backend not reachable. Please start FastAPI server.")



# -------------------------
# Admin View
# -------------------------
if role == "Admin":
    st.title("Admin – Patient Timeline")

    patient_id = st.number_input(
        "Patient ID",
        min_value=1,
        step=1
    )

    if st.button("View Timeline"):
        dummy_data = {
            "month": [1, 2, 3, 4],
            "risk_score": [0.3, 0.45, 0.6, 0.75]
        }

        df = pd.DataFrame(dummy_data)
        st.line_chart(df.set_index("month"))
