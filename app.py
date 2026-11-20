"""
=============================================================================
EduGuard AI – AI-Powered Student Dropout Risk Prediction & Early Intervention
Main Application Entry Point & Navigation Architecture
=============================================================================
Tagline: Predict Early. Intervene Smartly. Protect Every Future.
Stack: Streamlit, Scikit-Learn, Pandas, NumPy, Plotly, SQLite
"""

import streamlit as st
import os
import sys

# Ensure root directory is on Python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# 1. Page Configuration (Wide layout, custom branding)
st.set_page_config(
    page_title="EduGuard AI – Dropout Risk & Early Intervention",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject Custom SaaS Stylesheet
def inject_custom_css():
    css_path = os.path.join(ROOT_DIR, "assets", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)

inject_custom_css()

# 3. Initialize Database & ML Components
from backend.database import init_database
from ml.predict import get_model_bundle
from assets.branding import get_sidebar_brand_html

@st.cache_resource
def bootstrap_system():
    """Initializes SQLite schema, seeds demo records, and loads ML model bundle."""
    init_database()
    bundle = get_model_bundle()
    return bundle

model_bundle = bootstrap_system()

# 4. Session State Management
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user" not in st.session_state:
    st.session_state["user"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Overview Dashboard"

# Import Modular Views
from views.login_view import render_login_view
from views.dashboard_view import render_dashboard_view
from views.student_directory_view import render_student_directory_view
from views.predictor_view import render_predictor_view
from views.intervention_view import render_intervention_view
from views.reports_view import render_reports_view
from views.settings_view import render_settings_view

# 5. Authentication Router
if not st.session_state["logged_in"]:
    render_login_view()
    st.stop()

# =============================================================================
# AUTHENTICATED APPLICATION INTERFACE
# =============================================================================

current_user = st.session_state.get("user") or {}
user_role = current_user.get("role", "counselor")
is_admin = user_role == "admin"
role_display = "👑 Administrator" if is_admin else "🎓 Faculty/Counselor"

# ----------------- SIDEBAR NAVIGATION -----------------
with st.sidebar:
    # EduGuard AI Brand Header
    st.markdown(get_sidebar_brand_html(), unsafe_allow_html=True)
    
    # User Profile Pill Card
    st.markdown(f"""
    <div style="
        background: rgba(255, 255, 255, 0.07);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 12px;
        padding: 12px 14px;
        margin-bottom: 16px;
    ">
        <div style="font-size: 0.72rem; color: #94A3B8; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">
            ACTIVE SESSION
        </div>
        <div style="font-size: 0.95rem; font-weight: 700; color: #FFFFFF; margin-top: 3px;">
            {current_user.get('full_name', 'Authorized User')}
        </div>
        <div style="font-size: 0.78rem; color: #60A5FA; font-weight: 600; margin-top: 2px;">
            {role_display}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-size: 0.72rem; font-weight: 700; color: #94A3B8; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; padding-left: 4px;">
        NAVIGATION MENU
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation Items
    nav_items = [
        ("Overview Dashboard", "📊 Overview Dashboard"),
        ("Student Risk Directory", "📋 Student Risk Directory"),
        ("Single Student Predictor", "🎯 Single Student Predictor"),
        ("Intervention Action Center", "🛡️ Intervention Action Center"),
        ("Reports & Analytics", "📑 Reports & Analytics"),
        ("Settings", "⚙️ System Settings")
    ]
    
    for page_key, label in nav_items:
        is_active = st.session_state["current_page"] == page_key
        button_type = "primary" if is_active else "secondary"
        
        if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=button_type):
            st.session_state["current_page"] = page_key
            st.rerun()
            
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("---")
    
    # System & Model Status Widget
    metrics = model_bundle.get("metrics", {})
    acc_val = metrics.get("accuracy", 0.906) * 100
    st.markdown(f"""
    <div style="
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 8px;
        padding: 10px 12px;
        margin-bottom: 14px;
        font-size: 0.80rem;
        color: #A7F3D0;
    ">
        <div style="display: flex; align-items: center; gap: 6px; font-weight: 700;">
            <span style="color: #34D399; font-size: 10px;">●</span> Random Forest Active
        </div>
        <div style="font-size: 0.75rem; color: #D1FAE5; margin-top: 3px;">
            Test Accuracy: <b>{acc_val:.1f}%</b> · 160 Trees
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Logout Button
    if st.button("🚪 Logout from Portal", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["user"] = None
        st.session_state["current_page"] = "Overview Dashboard"
        st.rerun()

# ----------------- MAIN VIEW DISPATCHER -----------------
current_page = st.session_state.get("current_page", "Overview Dashboard")

if current_page == "Overview Dashboard":
    render_dashboard_view()
elif current_page == "Student Risk Directory":
    render_student_directory_view()
elif current_page == "Single Student Predictor":
    render_predictor_view()
elif current_page == "Intervention Action Center":
    render_intervention_view()
elif current_page == "Reports & Analytics":
    render_reports_view()
elif current_page == "Settings":
    render_settings_view()
else:
    st.error(f"Page '{current_page}' not found.")
    render_dashboard_view()
