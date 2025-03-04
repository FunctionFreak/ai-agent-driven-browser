import os
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def launch_browser_with_profile():
    """
    Launches a persistent Chrome browser session using the user profile defined in CHROME_PROFILE_PATH.
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH not set in environment variables.")
    
    playwright = sync_playwright().start()
    # Launch a persistent Chromium instance using the user data directory
    browser_context = playwright.chromium.launch_persistent_context(
        user_data_dir=chrome_profile_path,
        headless=False  # Set to False if you want to see the browser window during debugging
    )
    return browser_context

# Example usage:
if __name__ == "__main__":
    browser = launch_browser_with_profile()
    page = browser.new_page()
    page.goto("https://example.com")
    print("Page title:", page.title())
    browser.close()
