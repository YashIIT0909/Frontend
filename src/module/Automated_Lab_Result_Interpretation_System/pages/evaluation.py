import streamlit as st
import requests
import pandas as pd
from src.module.Automated_Lab_Result_Interpretation_System.api import get_api_base_url, fetch_json

def render_evaluation():
    st.caption("The 'brain' of the module that analyzes patient lab results against active rules.")
    st.divider()

    st.markdown("### 🧠 Run Evaluation")
    eval_patient_id = st.text_input("Patient ID for Evaluation", key="eval_input")
    if st.button("🚀 Run AI Evaluation", use_container_width=True):
        if not eval_patient_id:
            st.error("Please enter a Patient ID first.")
        else:
            try:
                response = requests.post(f"{get_api_base_url()}/evaluate/{eval_patient_id}", timeout=10)
                if response.status_code in [200, 201]:
                    data = response.json()
                    message = data.get("message", "Evaluation successful")
                    st.success(message)
                    fetch_json.clear()  
                else:
                    st.error(f"Evaluation failed: {response.text}")
            except Exception as e:
                st.error(f"Error connecting to engine: {e}")

    st.markdown("---")

    st.markdown("### 📋 Generated Recommendations (Output)")
    rec_patient_id = st.text_input("View Recommendations for Patient ID", value=eval_patient_id)
    if rec_patient_id:
        recs, err = fetch_json(f"/patients/{rec_patient_id}/recommendations")
        if err:
            st.error(f"Failed to load recommendations: {err}")
        elif not recs:
            st.info("No recommendations found for this patient.")
        else:
            df = pd.DataFrame(recs)
            cols = ["SuggestionText", "FollowUpTestName", "CreatedTimestamp", "SourceRuleID"]
            available_cols = [c for c in cols if c in df.columns]
            st.dataframe(df[available_cols] if available_cols else df, use_container_width=True)
    else:
        st.info("Enter a Patient ID above to view generated recommendations.")
