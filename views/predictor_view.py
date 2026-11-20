"""
EduGuard AI - Single Student Risk Predictor View
Interactive real-time prediction module using trained Random Forest Classifier,
evaluates class probabilities, generates explainable factors, and suggests interventions.
"""

import streamlit as st
import pandas as pd
from ml.predict import predict_student
from backend.student_service import get_all_students_with_predictions, add_student, update_student
from utils.charts import create_probability_breakdown_bar
from utils.helpers import get_risk_badge_html, format_currency, render_banner

def render_predictor_view():
    """Renders the Single Student Prediction module."""
    user = st.session_state.get("user") or {}
    
    st.markdown(
        render_banner(
            title="Single Student Dropout Risk Predictor",
            subtitle="Real-time Random Forest inference with factor diagnostics & tailored advisories",
            role_badge=f"Logged as {user.get('full_name', 'Faculty/Counselor')}"
        ),
        unsafe_allow_html=True
    )
    
    # Mode selector
    mode = st.radio(
        "Evaluation Source",
        ["Custom Scenario / Prospective Student", "Load Existing Enrolled Student"],
        horizontal=True
    )
    
    default_id = "NEW_STU"
    default_name = "Candidate Student"
    default_dept = "Computer Science"
    default_att = 75.0
    default_cgpa = 6.80
    default_lms = 60.0
    default_fee = 0.0
    
    if mode == "Load Existing Enrolled Student":
        students_df = get_all_students_with_predictions()
        if not students_df.empty:
            stu_choices = [f"{r['student_id']} - {r['student_name']}" for _, r in students_df.iterrows()]
            selected_choice = st.selectbox("Select Student to Pre-fill Inputs:", stu_choices)
            if selected_choice:
                sel_id = selected_choice.split(" - ")[0]
                row = students_df[students_df["student_id"] == sel_id].iloc[0]
                default_id = str(row["student_id"])
                default_name = str(row["student_name"])
                default_dept = str(row["department"])
                default_att = float(row["attendance"])
                default_cgpa = float(row["cgpa"])
                default_lms = float(row["lms_activity"])
                default_fee = float(row["fee_dues"])
                
    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
    
    # Input Form
    with st.form("single_predictor_form"):
        st.subheader("Student Identity & Evaluation Parameters")
        
        info_c1, info_c2, info_c3 = st.columns(3)
        with info_c1:
            stu_id_val = st.text_input("Student ID", value=default_id)
        with info_c2:
            stu_name_val = st.text_input("Student Full Name", value=default_name)
        with info_c3:
            dept_val = st.selectbox(
                "Department",
                ["Computer Science", "AI & Data Science", "Information Technology", "Electronics & Comm.", "Mechanical Engineering"],
                index=0
            )
            
        st.markdown("---")
        st.write("**Machine Learning Feature Dimensions:**")
        
        param_c1, param_c2 = st.columns(2)
        with param_c1:
            att_val = st.slider(
                "Attendance Percentage (%)",
                min_value=0.0, max_value=100.0, value=default_att, step=0.5,
                help="Regulatory institutional threshold: 75%"
            )
            cgpa_val = st.slider(
                "Cumulative GPA (0.00 – 10.00)",
                min_value=0.0, max_value=10.0, value=default_cgpa, step=0.05,
                help="Academic probation threshold: 5.0"
            )
        with param_c2:
            lms_val = st.slider(
                "LMS Activity Score (%)",
                min_value=0.0, max_value=100.0, value=default_lms, step=0.5,
                help="Online portal logins, quiz completion and digital assignment submissions"
            )
            fee_val = st.number_input(
                "Pending Tuition & Fee Arrears ($)",
                min_value=0.0, max_value=25000.0, value=default_fee, step=100.0,
                help="Outstanding institutional fees causing financial hold"
            )
            
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        predict_btn = st.form_submit_button("🔮 Predict Dropout Risk via Random Forest", use_container_width=True, type="primary")
        
    # Execute Prediction and Display Results
    if predict_btn or "last_prediction" in st.session_state:
        if predict_btn:
            result = predict_student(att_val, cgpa_val, lms_val, fee_val)
            result["student_id"] = stu_id_val
            result["student_name"] = stu_name_val
            result["department"] = dept_val
            result["attendance"] = att_val
            result["cgpa"] = cgpa_val
            result["lms_activity"] = lms_val
            result["fee_dues"] = fee_val
            st.session_state["last_prediction"] = result
        else:
            result = st.session_state["last_prediction"]
            
        st.markdown("---")
        st.subheader("🎯 Machine Learning Prediction Results & Action Intelligence")
        
        risk_level = result["risk_level"]
        risk_score = result["risk_score"]
        probs = result["probabilities"]
        
        # Result Showcase Cards
        res_col1, res_col2 = st.columns([1.2, 1.8])
        
        with res_col1:
            res_card_html = (
                '<div style="background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 14px; padding: 24px 20px; '
                'box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05); text-align: center;">'
                '<div style="font-size: 0.82rem; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.06em;">PREDICTED ATTRITION RISK</div>'
                f'<div style="margin: 14px 0;">{get_risk_badge_html(risk_level)}</div>'
                f'<div style="font-size: 2.8rem; font-weight: 800; color: #0F172A; line-height: 1.1; font-family: \'Plus Jakarta Sans\', sans-serif;">{risk_score:.1f}<span style="font-size: 1.2rem; color: #94A3B8;">/100</span></div>'
                '<div style="font-size: 0.82rem; color: #64748B; margin-top: 6px;">Continuous Dropout Risk Index</div>'
                f'<div style="margin-top: 18px; padding-top: 14px; border-top: 1px solid #F1F5F9; font-size: 0.88rem; color: #334155;"><b>{result["student_name"]}</b> ({result["student_id"]})<br><span style="color: #64748B; font-size: 0.82rem;">{result["department"]}</span></div>'
                '</div>'
            )
            st.markdown(res_card_html, unsafe_allow_html=True)
            
        with res_col2:
            st.subheader("📊 Multiclass Probability Breakdown")
            st.caption("Model confidence distribution evaluated across the 160 Random Forest decision trees")
            p_fig = create_probability_breakdown_bar(probs)
            st.plotly_chart(p_fig, use_container_width=True)
            
            p1, p2, p3 = st.columns(3)
            p1.metric("Low Risk Prob.", f"{probs.get('Low Risk', 0.0)*100:.1f}%")
            p2.metric("Medium Risk Prob.", f"{probs.get('Medium Risk', 0.0)*100:.1f}%")
            p3.metric("High Risk Prob.", f"{probs.get('High Risk', 0.0)*100:.1f}%")
            
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        
        # Contributing Factors & Advisory
        fact_col1, fact_col2 = st.columns(2)
        with fact_col1:
            st.subheader("🔍 Primary Contributing Factors")
            for f in result["factors"]:
                if f["type"] == "danger":
                    st.error(f"**{f['metric']}:** {f['text']}")
                elif f["type"] == "warning":
                    st.warning(f"**{f['metric']}:** {f['text']}")
                else:
                    st.success(f"**{f['metric']}:** {f['text']}")
                    
        with fact_col2:
            st.subheader("🛡️ AI-Recommended Early Intervention Plan")
            advisory_box_html = (
                f'<div style="background: #EFF6FF; border-left: 4px solid #2563EB; border-radius: 8px; '
                f'padding: 16px; font-size: 0.92rem; color: #1E3A8A; line-height: 1.5;">'
                f'<b>Action Strategy:</b><br>{result["advisory"]}'
                f'</div>'
            )
            st.markdown(advisory_box_html, unsafe_allow_html=True)
            
            rec_type = 'Academic Counseling' if result['cgpa'] < 6.0 else ('Attendance Improvement' if result['attendance'] < 70 else ('Financial Assistance' if result['fee_dues'] > 1500 else 'Academic Mentoring'))
            st.caption(f"Recommended Intervention Category: **{rec_type}**")
            
        # Post-Prediction Actions
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        btn_c1, btn_c2 = st.columns(2)
        with btn_c1:
            if st.button("💾 Enroll / Update in Student Database", use_container_width=True):
                save_data = {
                    "student_id": result["student_id"],
                    "student_name": result["student_name"],
                    "department": result["department"],
                    "attendance": result["attendance"],
                    "cgpa": result["cgpa"],
                    "lms_activity": result["lms_activity"],
                    "fee_dues": result["fee_dues"],
                    "semester": 4,
                    "email": f"{result['student_id'].lower()}@eduguard.edu"
                }
                success, msg = add_student(save_data)
                if success:
                    st.success(f"✓ {msg}")
                else:
                    succ_up, msg_up = update_student(result["student_id"], save_data)
                    if succ_up:
                        st.success(f"✓ Refreshed: {msg_up}")
                    else:
                        st.error(msg)
                        
        with btn_c2:
            if st.button("🛡️ Launch Intervention Case for This Student", use_container_width=True, type="primary"):
                st.session_state["prefill_intervention_student_id"] = result["student_id"]
                st.session_state["prefill_intervention_advisory"] = result["advisory"]
                st.session_state["current_page"] = "Intervention Action Center"
                st.rerun()
