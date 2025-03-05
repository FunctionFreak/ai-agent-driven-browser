# In src/automation/playwright_controller.py
import os
import random
import shutil
import tempfile
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def apply_stealth_mode(page):
    """
    Apply stealth mode JavaScript to hide automation markers.
    """
    stealth_js = """
    // Override webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => false,
    });
    
    // Override Chrome's automation property
    window.navigator.chrome = {
        runtime: {},
    };
    
    // Modify plugins to look like regular browser
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5],
    });
    
    // Modify languages 
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en'],
    });
    
    // Prevent detection via permissions
    if (window.navigator.permissions) {
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
            Promise.resolve({ state: Notification.permission }) :
            originalQuery(parameters)
        );
    }
    
    // Hide automation-specific Chrome DevTools Protocol (CDP)
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    
    // Set a consistent user agent
    Object.defineProperty(navigator, 'userAgent', {
        get: () => 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    });
    """
    page.add_init_script(stealth_js)

def launch_browser_with_profile():
    """
    Launches Chrome browser using your actual profile to maintain all settings/login state
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH not set in environment variables.")
    
    # Verify this is the User Data directory and not a specific profile
    if chrome_profile_path.endswith("Default"):
        # Strip off the "Default" part if it was incorrectly included
        chrome_profile_path = chrome_profile_path.replace("\\Default", "")
        print(f"Adjusting profile path to: {chrome_profile_path}")
    
    # Get path to Chrome executable
    chrome_executable_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if not os.path.exists(chrome_executable_path):
        # Fallback to auto-detection
        chrome_executable_path = None
        print("Chrome executable not found at expected path, using auto-detection")
    
    try:
        # Launch Playwright with the actual profile (no temporary copy)
        playwright = sync_playwright().start()
        
        # Use a specific browser profile if needed (e.g., profile 1)
        # If you want to use the Default profile, don't set this parameter
        # profile_name = None  # For Default profile
        # profile_name = "Profile 1"  # For a specific named profile
        
        browser_context = playwright.chromium.launch_persistent_context(
            user_data_dir=chrome_profile_path,  # Your actual Chrome profile directory
            headless=False,
            executable_path=chrome_executable_path,
            # channel="chrome",  # Uncomment to use your installed Chrome instead of bundled Chromium
            args=[
                "--start-maximized", 
                "--window-size=1920,1080",
                "--disable-blink-features=AutomationControlled"  # Critical for avoiding detection
            ]
        )
        
        # Apply stealth mode to all pages
        for page in browser_context.pages:
            page.set_viewport_size({"width": 1920, "height": 1080})
            apply_stealth_mode(page)
        
        return browser_context, None  # Return None as second param since we don't need to clean up
    except Exception as e:
        print(f"Error launching browser: {e}")
        raise e
# Example usage:
#if __name__ == "__main__":
    browser = launch_browser_with_profile()
    page = browser.new_page()
    page.goto("https://example.com")
    print("Page title:", page.title())
    browser.close()
