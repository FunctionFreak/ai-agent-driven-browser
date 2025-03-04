# In src/automation/playwright_controller.py

import os
import shutil
import tempfile
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def launch_browser_with_profile():
    """
    Launches a persistent Chrome browser session using a temporary copy of 
    the user profile defined in CHROME_PROFILE_PATH.
    """
    chrome_profile_path = os.getenv("CHROME_PROFILE_PATH")
    if not chrome_profile_path:
        raise ValueError("CHROME_PROFILE_PATH not set in environment variables.")
    
    # Create a temporary directory for the profile copy
    temp_profile_path = tempfile.mkdtemp(prefix="chrome_profile_copy_")
    print(f"Creating temporary Chrome profile at: {temp_profile_path}")
    
    try:
        # Copy essential profile data
        os.makedirs(os.path.join(temp_profile_path, "Default"), exist_ok=True)
        
        source_default = os.path.join(chrome_profile_path, "Default")
        target_default = os.path.join(temp_profile_path, "Default")
        
        essential_files = ["Preferences", "Cookies", "Login Data", "Web Data"]
        
        for file in essential_files:
            source = os.path.join(source_default, file)
            target = os.path.join(target_default, file)
            if os.path.exists(source):
                try:
                    shutil.copy2(source, target)
                except:
                    pass
        
        # Launch Playwright with the temporary profile and maximized window
        playwright = sync_playwright().start()
        browser_context = playwright.chromium.launch_persistent_context(
            user_data_dir=temp_profile_path,
            headless=False,
            args=["--start-maximized", "--window-size=1920,1080"]  # Force maximized window
        )
        
        # Set viewport for all pages
        default_viewport = {"width": 1920, "height": 1080}
        for page in browser_context.pages:
            page.set_viewport_size(default_viewport)
        
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
