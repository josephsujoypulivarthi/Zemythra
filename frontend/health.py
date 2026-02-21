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
        # Dummy visualization
        st.subheader("Risk Output")
        st.metric("Risk Score", 0.62)
        st.metric("Risk Level", "Medium")
        st.info("No emergency detected")

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
