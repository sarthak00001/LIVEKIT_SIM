import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://admin.thefuture.university/liveclasses/simulation", wait_until="domcontentloaded", timeout=60000)
    
    print("==> Browser is open.")
    print("==> Click 'Sign in with Google' in the browser window")
    print("==> Complete the Google login manually in the browser")
    print("==> Once you see the Simulations Dashboard, come back to terminal")
    input("==> Press ENTER here after you are fully logged in: ")
    
    context.storage_state(path="auth_state.json")
    print("Session saved to auth_state.json")
    browser.close()
