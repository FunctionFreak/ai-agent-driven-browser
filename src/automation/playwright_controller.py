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
    Launches a persistent Chrome browser session with stealth mode to avoid detection.
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH not set in environment variables.")
    
    # Get path to Chrome executable (try default locations)
    chrome_executable_path = None
    possible_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            chrome_executable_path = path
            break
    
    # Create a temporary directory for the profile copy
    temp_profile_path = tempfile.mkdtemp(prefix="chrome_profile_copy_")
    print(f"Creating temporary Chrome profile at: {temp_profile_path}")
    
    try:
        # Copy essential profile data
        os.makedirs(os.path.join(temp_profile_path, "Default"), exist_ok=True)
        
        source_default = os.path.join(chrome_profile_path, "Default")
        target_default = os.path.join(temp_profile_path, "Default")
        
        # Copy more profile files for better persistence of cookies and login state
        essential_files = [
            "Preferences", "Cookies", "Login Data", "Web Data", 
            "History", "Bookmarks", "Favicons", "TransportSecurity",
            "Network Action Predictor", "Extension Cookies"
        ]
        
        for file in essential_files:
            source = os.path.join(source_default, file)
            target = os.path.join(target_default, file)
            if os.path.exists(source):
                try:
                    shutil.copy2(source, target)
                except Exception as e:
                    print(f"Could not copy {file}: {e}")
        
        # Launch Playwright with the profile and stealth mode
        playwright = sync_playwright().start()
        browser_context = playwright.chromium.launch_persistent_context(
            user_data_dir=temp_profile_path,
            headless=False,
            executable_path=chrome_executable_path,
            args=[
                "--start-maximized", 
                "--window-size=1920,1080",
                "--disable-blink-features=AutomationControlled"  # Critical for avoiding detection
            ]
        )
        
        # Set viewport for all pages and apply stealth mode
        default_viewport = {"width": 1920, "height": 1080}
        for page in browser_context.pages:
            page.set_viewport_size(default_viewport)
            apply_stealth_mode(page)
        
        return browser_context, temp_profile_path
    except Exception as e:
        # Clean up the temporary directory if something goes wrong
        shutil.rmtree(temp_profile_path, ignore_errors=True)
        raise e
# Example usage:
#if __name__ == "__main__":
    browser = launch_browser_with_profile()
    page = browser.new_page()
    page.goto("https://example.com")
    print("Page title:", page.title())
    browser.close()
