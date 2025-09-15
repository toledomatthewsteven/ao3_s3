#app.py
import datetime
import streamlit as st
from scraping.login import ao3_login
from scraping.scrape_history import scrape_history
from processing.storage import save_dataset, list_datasets, load_dataset, delete_dataset
import time

st.set_page_config(page_title="AO3-S3", layout="wide")
this_year = datetime.datetime.now().year

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
    if st.button("📊 Generate / Manage Reports", key="manage_reports"):
        st.info("➡️ Reports module coming soon...")

    with st.expander("🗂️ Create / Manage Datasets", expanded=False):
        st.subheader("Create New Dataset")
        timeframe = st.selectbox("Timeframe", ["this_year", "all_time"])
        if st.button("Start Scraping", key="start_scraping"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            # use local counter to compute a fake percentage (grows until done)
            total_seen = 0

            def update_progress(current_count, title):
                nonlocal total_seen
                total_seen = current_count
                # we don't know total fics in advance, so show an incremental bar
                pct = min(current_count / 200.0, 1.0)  # scale to 200 fics -> 100% (adjust as desired)
                progress_bar.progress(pct)
                status_text.text(f"Scraping #{current_count}: {title}")

            with st.spinner("Scraping AO3 history... please wait."):
                if timeframe == "this_year":
                    data = scrape_history(
                        st.session_state.session,
                        st.session_state.username,
                        start_year=this_year,
                        end_year=this_year,
                        progress_callback=update_progress,
                    )
                else:
                    data = scrape_history(
                        st.session_state.session,
                        st.session_state.username,
                        progress_callback=update_progress,
                    )
                fname, path = save_dataset(st.session_state.username, "history", timeframe, data)

            progress_bar.empty()
            status_text.empty()
            st.success(f"✅ Dataset saved as {fname}")



        st.subheader("Existing Datasets")
        datasets = list_datasets()
        if not datasets:
            st.info("No datasets saved yet.")
        else:
            for f in datasets:
                with st.expander(f):
                    dataset = load_dataset(f)
                    st.write(f"Contains {len(dataset.get('titles', []))} works")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"📂 View {f}", key=f"view_{f}"):
                            st.json(dataset)
                    with col2:
                        if st.button(f"🗑️ Delete {f}", key=f"del_{f}"):
                            delete_dataset(f)
                            st.success(f"Deleted {f}")
                            st.rerun()


# --- Router ---
if not st.session_state.logged_in:
    login_screen()
else:
    dashboard()