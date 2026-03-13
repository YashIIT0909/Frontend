import streamlit as st
import requests
import pandas as pd
from src.module.Automated_Lab_Result_Interpretation_System.api import get_api_base_url, fetch_json

def render_rules_admin():
    st.caption("Admins can define what constitutes 'Normal' vs 'Critical'.")
    st.divider()

    st.markdown("### 📝 Create New Interpretation Rule")
    with st.form("create_rule_form"):
        rule_name = st.text_input("Rule Name", placeholder="e.g. High Glucose")
        rule_desc = st.text_input("Rule Description", placeholder="e.g. Glucose is critically high")
        rule_type = st.selectbox("Rule Type", ["Single", "Multiple", "Temporal"])
        
        st.markdown("**Logic Condition**")
        st.caption("Format must be: `TestValue [operator] [number]`. Example: `TestValue >= 125.5`")
        logic_condition = st.text_input("Logic Condition", placeholder="TestValue >= 125.5")
        
        rule_severity = st.selectbox("Severity", ["Normal", "Abnormal", "Critical"])
        rule_confidence = st.slider("Confidence", 0.0, 1.0, 0.9)

        submitted = st.form_submit_button("Create Rule")
        if submitted:
            if not rule_name or not logic_condition:
                st.error("Rule Name and Logic Condition are required.")
            else:
                payload = {
                    "RuleName": rule_name,
                    "RuleDescription": rule_desc,
                    "RuleType": rule_type,
                    "LogicCondition": logic_condition,
                    "RuleSeverity": rule_severity,
                    "RuleConfidence": rule_confidence,
                    "DetectedPatternIDs": []
                }
                try:
                    response = requests.post(f"{get_api_base_url()}/rules/", json=payload, timeout=5)
                    if response.status_code == 201:
                        st.success("Rule created successfully!")
                        fetch_json.clear()
                    else:
                        st.error(f"Failed to create rule: {response.text}")
                except Exception as e:
                    st.error(f"Backend error: {e}")

    st.markdown("---")

    st.markdown("### ⚙️ Active Rules")
    rules, err = fetch_json("/rules/")
    if err:
        st.error(f"Could not load rules: {err}")
    elif not rules:
        st.info("No rules exist currently.")
    else:
        df = pd.DataFrame(rules)
        st.dataframe(df, use_container_width=True)
