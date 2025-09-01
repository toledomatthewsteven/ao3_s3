#login.py
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "https://archiveofourown.org/users/login"
PROFILE_URL = "https://archiveofourown.org/users/{username}/profile"

def ao3_login(username: str, password: str):
    """Logs into AO3 and returns (session, profile_picture_url) if successful, else (None, None)."""
    session = requests.Session()

    # 1. Get authenticity token
    resp = session.get(LOGIN_URL)
    soup = BeautifulSoup(resp.text, "html.parser")
    token = soup.find("input", {"name": "authenticity_token"})["value"]

    # 2. Post login form
    payload = {
        "user[login]": username,
        "user[password]": password,
        "authenticity_token": token,
        "commit": "Log in",
    }
    resp = session.post(LOGIN_URL, data=payload)

    if "Log Out" not in resp.text:
        return None, None

    # 3. Fetch profile page for avatar
    profile_resp = session.get(PROFILE_URL.format(username=username))
    soup = BeautifulSoup(profile_resp.text, "html.parser")

    avatar_tag = soup.find("img", {"class": "icon"})  # AO3 uses class="icon" for pfps
    pfp_url = avatar_tag["src"] if avatar_tag else None

    return session, pfp_url
