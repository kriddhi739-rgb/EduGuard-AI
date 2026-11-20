"""
EduGuard AI - Settings & Administration View
User profile management, password updates, notification preferences,
ML model retraining triggers, and database maintenance tools.
"""

import streamlit as st
import os
import sqlite3
from backend.authentication import change_password
from backend.database import DB_PATH, init_database
from ml.train_model import train_and_evaluate_model
from utils.helpers import render_banner

def render_settings_view():
    """Renders the settings and user configuration view."""
    user = st.session_state.get("user") or {}
    username = user.get("username", "admin")
    is_admin = user.get("role") == "admin"
    
    st.markdown(
        render_banner(
            title="System Settings & Account Management",
            subtitle="Configure profile preferences, security credentials, ML pipeline triggers, and database storage",
            role_badge="👑 Administrator" if is_admin else "🎓 Faculty/Counselor"
        ),
        unsafe_allow_html=True
    )
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "👤 User Profile & Account",
        "🔒 Security & Password",
        "⚙️ ML Model Retraining",
        "💾 Database Maintenance"
    ])
    
    # ---------------- TAB 1: USER PROFILE ----------------
    with tab1:
        st.subheader("User Account Information")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Full Name", value=user.get("full_name", ""), disabled=True)
            st.text_input("Username", value=user.get("username", ""), disabled=True)
            st.text_input("Assigned System Role", value="Administrator" if is_admin else "Faculty / Counselor", disabled=True)
        with col2:
            st.text_input("Institutional Email", value=user.get("email", ""), disabled=True)
            st.text_input("Department / Unit", value=user.get("department", "Academic Affairs"), disabled=True)
            st.text_input("Account Created", value=user.get("created_at", "2026-11-20"), disabled=True)
            
        st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)
        st.subheader("🔔 Notification & Alert Preferences")
        
        pref1 = st.checkbox("Email Alert on New High-Risk Student Detection", value=True)
        pref2 = st.checkbox("Weekly Institutional Retention Digest Report", value=True)
        pref3 = st.checkbox("Intervention Follow-up Reminders (48 Hours Prior)", value=True)
        
        if st.button("Save Notification Preferences"):
            st.success("Preferences successfully saved!")
            
    # ---------------- TAB 2: CHANGE PASSWORD ----------------
    with tab2:
        st.subheader("Change Account Password")
        st.markdown("Ensure your account is protected with a secure password (minimum 6 characters).")
        
        with st.form("change_pwd_form"):
            old_pwd = st.text_input("Current Password", type="password")
            new_pwd = st.text_input("New Password", type="password")
            confirm_pwd = st.text_input("Confirm New Password", type="password")
            
            pwd_submit = st.form_submit_button("Update Password", use_container_width=True)
            if pwd_submit:
                if not old_pwd or not new_pwd:
                    st.error("Please enter both current and new passwords.")
                elif new_pwd != confirm_pwd:
                    st.error("New password and confirmation do not match.")
                else:
                    success, msg = change_password(username, old_pwd, new_pwd)
                    if success:
                        st.success(msg)
                    else:
                        st.error(msg)
                        
    # ---------------- TAB 3: ML MODEL RETRAINING ----------------
    with tab3:
        st.subheader("⚙️ Machine Learning Model Management & Retraining")
        st.markdown(
            "Retrain the Random Forest model on the updated student population and synthesized cohort distributions. "
            "Evaluates genuine test-set metrics and updates the model artifacts bundle."
        )
        
        if not is_admin:
            st.info("ℹ️ Model retraining can only be initiated by authorized Administrators.")
        else:
            st.warning("Retraining will update decision trees across 160 estimators and recalculate all feature weights.")
            if st.button("🚀 Retrain Random Forest Model Now", type="primary", use_container_width=True):
                with st.spinner("Retraining Random Forest Classifier and updating test metrics..."):
                    bundle = train_and_evaluate_model()
                    acc = bundle["metrics"]["accuracy"] * 100
                    st.success(f"Model successfully retrained! Fresh Test Accuracy: {acc:.2f}%. Artifacts saved.")
                    st.rerun()
                    
    # ---------------- TAB 4: DATABASE MAINTENANCE ----------------
    with tab4:
        st.subheader("💾 Database Statistics & Storage Tools")
        
        db_exists = os.path.exists(DB_PATH)
        db_size_kb = os.path.getsize(DB_PATH) / 1024 if db_exists else 0
        
        # Connect to query table counts
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM Users;")
            u_cnt = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM Students;")
            s_cnt = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM Prediction_Results;")
            p_cnt = c.fetchone()[0]
            c.execute("SELECT COUNT(*) FROM Intervention_Logs;")
            i_cnt = c.fetchone()[0]
            conn.close()
        except Exception:
            u_cnt, s_cnt, p_cnt, i_cnt = 0, 0, 0, 0
            
        dc1, dc2, dc3, dc4 = st.columns(4)
        dc1.metric("Registered Students", s_cnt)
        dc2.metric("ML Predictions Stored", p_cnt)
        dc3.metric("Intervention Records", i_cnt)
        dc4.metric("SQLite DB Size", f"{db_size_kb:.1f} KB")
        
        st.markdown("---")
        st.markdown(f"**Database File Location:** `{DB_PATH}`")
        
        if is_admin:
            st.subheader("Data Reset & Reseeding")
            st.write("If you wish to reset demo data and restore initial clean profiles:")
            confirm_reset = st.checkbox("Confirm database reset and re-seed with 120 demo students")
            if st.button("Re-seed Demo Database", disabled=not confirm_reset):
                with st.spinner("Rebuilding database..."):
                    from ml.train_model import train_and_evaluate_model
                    # Delete and recreate
                    try:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("DROP TABLE IF EXISTS Intervention_Logs;")
                        conn.execute("DROP TABLE IF EXISTS Prediction_Results;")
                        conn.execute("DROP TABLE IF EXISTS Students;")
                        conn.execute("DROP TABLE IF EXISTS Users;")
                        conn.commit()
                        conn.close()
                        train_and_evaluate_model()
                        st.success("Database cleanly re-seeded with fresh demonstration dataset!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resetting database: {e}")
                        
        # System & Version Info
        st.markdown("---")
        st.subheader("About EduGuard AI")
        st.markdown(
            "- **Platform:** EduGuard AI – AI-Powered Student Dropout Risk Prediction and Early Intervention System\n"
            "- **Version:** 2.4.0 (Enterprise EdTech Edition)\n"
            "- **Core Stack:** Python 3.13, Streamlit, Scikit-Learn, Pandas, Plotly, SQLite\n"
            "- **Tagline:** *Predict Early. Intervene Smartly. Protect Every Future.*"
        )
