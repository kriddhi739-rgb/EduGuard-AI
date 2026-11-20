"""
EduGuard AI - Modern Authentication View
Provides a cohesive, responsive, eye-catching login portal with demo role selection,
password visibility toggle, and instant error feedback.
"""

import streamlit as st
from backend.authentication import authenticate_user
from assets.branding import get_logo_svg

DEMO_ACCOUNTS = {
    "admin": {
        "label": "👑 Administrator",
        "username": "admin",
        "password": "admin123",
        "name": "Dr. Sarah Jenkins",
        "role_desc": "Institutional Executive & Policy Director"
    },
    "counselor": {
        "label": "🎓 Counselor",
        "username": "counselor",
        "password": "counselor123",
        "name": "Elena Vance, M.Ed.",
        "role_desc": "Senior Student Retention Counselor"
    },
    "prof_sharma": {
        "label": "👨‍🏫 Faculty",
        "username": "prof_sharma",
        "password": "faculty123",
        "name": "Prof. Rajesh Sharma",
        "role_desc": "CS & Data Analytics Faculty Mentor"
    }
}

def render_login_view():
    """Renders the cohesive, modern authentication portal."""
    
    # Session state initialization for pre-filled demo credentials
    if "login_username" not in st.session_state:
        st.session_state["login_username"] = ""
    if "login_password" not in st.session_state:
        st.session_state["login_password"] = ""
    if "show_password" not in st.session_state:
        st.session_state["show_password"] = False
        
    # Responsive centered column layout
    _, center_col, _ = st.columns([1, 2.2, 1])
    
    with center_col:
        # 1. Branded Header Card (Unindented raw HTML to prevent Markdown code-block parsing)
        logo_svg = get_logo_svg(56, 56)
        header_html = (
            '<div style="text-align: center; background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #4F46E5 100%); '
            'padding: 26px 20px 22px 20px; border-radius: 16px 16px 0 0; box-shadow: 0 4px 20px rgba(37, 99, 235, 0.22);">'
            f'<div style="display: flex; justify-content: center; margin-bottom: 12px;">{logo_svg}</div>'
            '<h1 style="color: #FFFFFF !important; font-size: 1.85rem; margin: 0; font-weight: 800; letter-spacing: -0.02em;">'
            'EduGuard <span style="color: #93C5FD;">AI</span>'
            '</h1>'
            '<p style="color: #DBEAFE; font-size: 0.88rem; margin-top: 6px; font-weight: 500; letter-spacing: 0.02em; margin-bottom: 0;">'
            'Predict Early. Intervene Smartly. Protect Every Future.'
            '</p>'
            '</div>'
        )
        st.markdown(header_html, unsafe_allow_html=True)
        
        # 2. Main Login Subheader Card
        sub_html = (
            '<div style="background: #FFFFFF; padding: 20px 24px 10px 24px; border-left: 1px solid #E2E8F0; border-right: 1px solid #E2E8F0;">'
            '<div style="font-size: 1.15rem; font-weight: 700; color: #0F172A;">Authorized Staff Access</div>'
            '<div style="font-size: 0.82rem; color: #64748B; margin-top: 2px;">Select a demo role below to auto-fill or enter your institutional credentials.</div>'
            '</div>'
        )
        st.markdown(sub_html, unsafe_allow_html=True)
        
        # 3. Demo Role Quick-Select Buttons
        demo_cols = st.columns(3)
        for idx, (key, info) in enumerate(DEMO_ACCOUNTS.items()):
            with demo_cols[idx]:
                if st.button(info["label"], key=f"demo_btn_{key}", use_container_width=True, help=f"Auto-fill as {info['name']}"):
                    st.session_state["login_username"] = info["username"]
                    st.session_state["login_password"] = info["password"]
                    st.rerun()
                    
        # 4. Standard Login Form
        with st.form("login_form", clear_on_submit=False):
            username_input = st.text_input(
                "Username or Institutional Email",
                value=st.session_state["login_username"],
                placeholder="e.g. admin or counselor@eduguard.edu"
            )
            
            pwd_type = "text" if st.session_state["show_password"] else "password"
            password_input = st.text_input(
                "Password",
                value=st.session_state["login_password"],
                type=pwd_type,
                placeholder="••••••••••••"
            )
            
            ctrl_c1, ctrl_c2 = st.columns(2)
            with ctrl_c1:
                show_pwd = st.checkbox("👁️ Show Password", value=st.session_state["show_password"])
                if show_pwd != st.session_state["show_password"]:
                    st.session_state["show_password"] = show_pwd
                    st.rerun()
            with ctrl_c2:
                remember_me = st.checkbox("Remember device", value=True)
                
            st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🚀 Sign In to EduGuard AI", use_container_width=True, type="primary")
            
            if submitted:
                clean_user = username_input.strip()
                clean_pass = password_input.strip()
                
                if not clean_user or not clean_pass:
                    st.error("Please provide both username and password to proceed.")
                else:
                    user = authenticate_user(clean_user, clean_pass)
                    if user:
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
                        st.session_state["current_page"] = "Overview Dashboard"
                        st.success(f"✓ Authenticated as {user['full_name']} ({user['role'].title()})")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please verify your username and password, or use one of the quick demo buttons above.")
                        
        # 5. Footer Info Bar
        footer_html = (
            '<div style="background: #F8FAFC; padding: 14px 20px; border-radius: 0 0 16px 16px; border: 1px solid #E2E8F0; '
            'border-top: 1px dashed #CBD5E1; box-shadow: 0 8px 18px -4px rgba(0, 0, 0, 0.06); text-align: center;">'
            '<div style="font-size: 0.78rem; color: #64748B;">'
            '🔒 Secured with <b>SHA-256 Hashing</b> & <b>SQLite Persistence</b><br>EduGuard AI Enterprise Edition v2.4'
            '</div>'
            '</div>'
        )
        st.markdown(footer_html, unsafe_allow_html=True)
