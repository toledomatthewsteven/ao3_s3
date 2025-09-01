# scraping/scrape_history.py
import sys, asyncio

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from playwright.sync_api import sync_playwright

# scraping/scrape_history.py
import requests
from bs4 import BeautifulSoup

def scrape_history(username: str, password: str):
    # Start a session to persist cookies
    session = requests.Session()

    # 1. Get the login page to grab the CSRF token
    login_url = "https://archiveofourown.org/users/login"
    resp = session.get(login_url)
    soup = BeautifulSoup(resp.text, "lxml")

    # AO3 hides CSRF in a hidden <input name="authenticity_token">
    token = soup.find("input", {"name": "authenticity_token"})
    if not token:
        print("❌ Could not find CSRF token — login page may have changed")
        return
    authenticity_token = token["value"]

    # 2. Send POST request with username, password, and CSRF token
    payload = {
        "user[login]": username,
        "user[password]": password,
        "authenticity_token": authenticity_token,
        "commit": "Log in",
    }

    resp = session.post(login_url, data=payload)

    # 3. Check if login worked (look for logout link as proof)
    if "Log Out" in resp.text or "log out" in resp.text.lower():
        print("✅ Login successful!")
        # Example: fetch user’s history page
        history_url = f"https://archiveofourown.org/users/{username}/readings"
        history_resp = session.get(history_url)
        print("History page title snippet:", history_resp.text[:200])
    else:
        print("❌ Login failed — check username/password or AO3 form update")


    if f"/users/{username}" in resp.text and "Log Out" in resp.text:
        print("✅ Definitely logged in as", username)
    else:
        print("❌ Still not logged in")

    print(session.cookies.get_dict())

