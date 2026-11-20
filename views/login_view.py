"""
EduGuard AI - Modern Authentication View
Provides secure user login, role badges, and quick-access demo credentials.
"""

import streamlit as st
from backend.authentication import authenticate_user
from assets.branding import get_logo_svg

def render_login_view():
    """Renders the login view and handles authentication state."""
    
    # Outer layout with centered container
    col_spacer_left, center_col, col_spacer_right = st.columns([1, 1.8, 1])
    
    with center_col:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        
        # Brand Card
        st.markdown(f"""
        <div style="
            text-align: center;
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 60%, #4F46E5 100%);
            padding: 30px 20px;
            border-radius: 16px 16px 0 0;
            box-shadow: 0 4px 20px rgba(37, 99, 235, 0.25);
        ">
            <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                {get_logo_svg(64, 64)}
            </div>
            <h1 style="color: #FFFFFF !important; font-size: 2rem; margin: 0; font-weight: 800; letter-spacing: -0.02em;">
                EduGuard <span style="color: #93C5FD;">AI</span>
            </h1>
            <p style="color: #DBEAFE; font-size: 0.95rem; margin-top: 6px; font-weight: 500;">
                Predict Early. Intervene Smartly. Protect Every Future.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login Form Container
        with st.container():
            st.markdown("""
            <div style="
                background: #FFFFFF;
                padding: 30px 32px 20px 32px;
                border-left: 1px solid #E2E8F0;
                border-right: 1px solid #E2E8F0;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
            ">
                <h3 style="margin-top: 0; color: #0F172A; font-size: 1.25rem;">Sign In to Portal</h3>
                <p style="color: #64748B; font-size: 0.88rem; margin-bottom: 18px;">
                    Enter your academic credentials or select a pre-configured role below.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.form("login_form", clear_on_submit=False):
                username_input = st.text_input(
                    "Username or Institutional Email",
                    placeholder="e.g. admin or counselor@eduguard.edu",
                    help="Authorized staff username or registered institutional email address."
                )
                
                password_input = st.text_input(
                    "Password",
                    type="password",
                    placeholder="••••••••••••",
                    help="Enter your password."
                )
                
                remember_col, _ = st.columns([1, 1])
                with remember_col:
                    st.checkbox("Remember this workstation", value=True)
                    
                submitted = st.form_submit_button("Sign In to EduGuard AI", use_container_width=True)
                
                if submitted:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    else:
                        user = authenticate_user(username_input, password_input)
                        if user:
                            st.session_state["logged_in"] = True
                            st.session_state["user"] = user
                            st.session_state["current_page"] = "Overview Dashboard"
                            st.success(f"Welcome back, {user['full_name']}!")
                            st.rerun()
                        else:
                            st.error("Invalid username or password. Please verify credentials.")
                            
            # Quick Demo Login Section
            st.markdown("""
            <div style="
                background: #F8FAFC;
                padding: 20px 32px 30px 32px;
                border-radius: 0 0 16px 16px;
                border: 1px solid #E2E8F0;
                border-top: 1px dashed #CBD5E1;
                box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08);
            ">
                <div style="font-size: 0.82rem; font-weight: 700; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; text-align: center;">
                    ⚡ Quick Demo Access (One-Click Sign In)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            qc1, qc2, qc3 = st.columns(3)
            with qc1:
                if st.button("👑 Administrator", use_container_width=True, help="Login as Dr. Sarah Jenkins (Institutional Admin)"):
                    user = authenticate_user("admin", "admin123")
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
                        st.session_state["current_page"] = "Overview Dashboard"
                        st.rerun()
            with qc2:
                if st.button("🎓 Counselor", use_container_width=True, help="Login as Elena Vance, M.Ed. (Student Support)"):
                    user = authenticate_user("counselor", "counselor123")
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
                        st.session_state["current_page"] = "Overview Dashboard"
                        st.rerun()
            with qc3:
                if st.button("👨‍🏫 Faculty", use_container_width=True, help="Login as Prof. Rajesh Sharma (CS Faculty)"):
                    user = authenticate_user("prof_sharma", "faculty123")
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
                        st.session_state["current_page"] = "Overview Dashboard"
                        st.rerun()
                        
            st.markdown("""
            <div style="text-align: center; margin-top: 24px; color: #94A3B8; font-size: 0.80rem;">
                Protected by Scikit-Learn Random Forest ML & SQLite Persistence<br>
                EduGuard AI v2.4 Enterprise Edition
            </div>
            """, unsafe_allow_html=True)
