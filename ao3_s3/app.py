import streamlit as st
from scraping.login import ao3_login
import time

st.set_page_config(page_title="AO3-S3", layout="wide")

# --- Session state setup ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "pfp_url" not in st.session_state:
    st.session_state.pfp_url = ""
if "session" not in st.session_state:
    st.session_state.session = None
if "login_attempted" not in st.session_state:
    st.session_state.login_attempted = False

# --- Login Page ---
def login_screen():
    st.title("🔑 AO3-S3 Login")

    # Use form to prevent multiple rapid submissions
    with st.form("login_form"):
        username = st.text_input("Username", value=st.session_state.get("input_username", ""))
        password = st.text_input("Password", type="password", value=st.session_state.get("input_password", ""))
        submitted = st.form_submit_button("Log In")
        
        if submitted:
            st.session_state.login_attempted = True
            st.session_state.input_username = username
            st.session_state.input_password = password

    if st.session_state.login_attempted:
        # Show loading spinner and status
        with st.spinner("Logging in... This may take a while."):
            # Attempt login
            session, pfp_url = ao3_login(
                st.session_state.input_username, 
                st.session_state.input_password
            )
        
        if session:
            st.session_state.logged_in = True
            st.session_state.username = st.session_state.input_username
            st.session_state.session = session
            st.session_state.pfp_url = pfp_url
            st.session_state.login_attempted = False
            
            # Clear sensitive data
            st.session_state.input_password = ""
            
            # Rerun to show dashboard immediately
            st.rerun()
        else:
            st.error("Login failed. Please check credentials.")
            st.session_state.login_attempted = False

# --- Dashboard Page ---
def dashboard():
    cols = st.columns([6, 1, 1])
    with cols[0]:
        st.subheader(f"Welcome to AO3-S3, {st.session_state.username} 👋")
    with cols[1]:
        if st.session_state.pfp_url:
            st.image(st.session_state.pfp_url, width=50)
    with cols[2]:
        if st.button("🚪 Logout"):
            # Clear all session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.markdown("---")
    if st.button("📊 Generate / Manage Reports"):
        st.info("➡️ Reports module coming soon...")
    if st.button("🗂️ Create / Manage Datasets"):
        st.info("➡️ Dataset manager coming soon...")

# --- Router ---
if not st.session_state.logged_in:
    login_screen()
else:
    dashboard()