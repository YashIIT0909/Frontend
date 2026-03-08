import streamlit as st
import requests
import pandas as pd
from datetime import datetime
from src.module.Automated_Lab_Result_Interpretation_System.api import get_api_base_url, fetch_json

def render_lab_records():
    st.caption("Input and view raw data for patient lab results.")
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### ➕ Add New Lab Result")
        with st.form("add_lab_result_form"):
            patient_id = st.text_input("Patient ID", help="Required")
            test_name = st.text_input("Test Name", help="e.g. Glucose")
            test_value = st.number_input("Test Value", value=0.0)
            units = st.text_input("Units", help="e.g. mg/dL")
            
            submitted = st.form_submit_button("Submit Lab Result")
            if submitted:
                if not patient_id or not test_name:
                    st.error("Patient ID and Test Name are required.")
                else:
                    payload = {
                        "PatientID": patient_id,
                        "TestName": test_name,
                        "TestValue": test_value,
                        "Units": units,
                        "ResultTimestamp": datetime.utcnow().isoformat()
                    }
                    try:
                        response = requests.post(f"{get_api_base_url()}/lab-results/", json=payload, timeout=5)
                        if response.status_code == 201:
                            st.success("Lab result created successfully!")
                            fetch_json.clear()
                        else:
                            st.error(f"Failed to create (Status {response.status_code}): {response.text}")
                    except Exception as e:
                        st.error(f"Backend connection error: {e}")

    with col2:
        st.markdown("### 📋 Patient History")
        search_patient_id = st.text_input("Search History by Patient ID")
        if search_patient_id:
            results, err = fetch_json(f"/patients/{search_patient_id}/results")
            if err:
                st.error(f"Could not load history: {err}")
            elif not results:
                st.info("No records found for this patient.")
            else:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
        else:
            st.info("Enter a Patient ID above to view history.")
