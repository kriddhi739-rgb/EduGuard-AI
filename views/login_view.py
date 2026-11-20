"""
EduGuard AI - Modern Authentication View
Cohesive, responsive login portal using 100% native Streamlit components.
"""

import streamlit as st
from backend.authentication import authenticate_user

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
    """Renders the authentication portal using native Streamlit components."""
    
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
        # 1. Native Streamlit Header (No raw HTML)
        st.title("🎓 EduGuard AI")
        st.markdown("**Predict Early. Intervene Smartly. Protect Every Future.**")
        st.caption("AI-Powered Student Dropout Risk Prediction & Early Intervention System")
        st.divider()
        
        st.subheader("Authorized Staff Access")
        st.caption("Select a demo role below to auto-fill, or enter your institutional credentials:")
        
        # 2. Demo Role Quick-Select Buttons
        demo_cols = st.columns(3)
        for idx, (key, info) in enumerate(DEMO_ACCOUNTS.items()):
            with demo_cols[idx]:
                if st.button(info["label"], key=f"demo_btn_{key}", use_container_width=True, help=f"Auto-fill as {info['name']}"):
                    st.session_state["login_username"] = info["username"]
                    st.session_state["login_password"] = info["password"]
                    st.rerun()
                    
        # 3. Standard Login Form
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
                        
        # 4. Native Footer
        st.divider()
        st.caption("🔒 Secured with SHA-256 Hashing & SQLite Persistence · EduGuard AI Enterprise Edition v2.4")
