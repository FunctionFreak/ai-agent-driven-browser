# In src/automation/playwright_controller.py
import os
import random
import shutil
import tempfile
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import logging
import asyncio

# Load environment variables from .env file
load_dotenv()

class PlaywrightController:
    def __init__(self, config=None):
        """Initialize the Playwright controller with configuration."""
        self.config = config or PlaywrightConfig()
        self.navigation_history = None
        self.browser_context = None
        self.playwright = None

class PlaywrightConfig:
    """Configuration for the Playwright browser controller."""
    def __init__(self, 
                 headless=False,
                 allowed_domains=None,
                 minimum_wait_time=0.5,
                 max_wait_time=5.0,
                 network_idle_time=1.0,
                 wait_between_actions=0.5):
        """
        Initialize configuration with sensible defaults.
        
        Args:
            headless: Whether to run browser in headless mode
            allowed_domains: List of allowed domains, if None all domains are allowed
            minimum_wait_time: Minimum time to wait for any page load
            max_wait_time: Maximum time to wait for page load before proceeding
            network_idle_time: Time for network to be idle before considering page loaded
            wait_between_actions: Time to wait between browser actions
        """
        self.headless = headless
        self.allowed_domains = allowed_domains
        self.minimum_wait_time = minimum_wait_time
        self.max_wait_time = max_wait_time
        self.network_idle_time = network_idle_time
        self.wait_between_actions = wait_between_actions

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

def launch_browser_with_profile(self):
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
        
        # Initialize navigation history
        self.initialize_navigation_history()
        return browser_context, None  # Return None as second param since we don't need to clean up
    except Exception as e:
        print(f"Error launching browser: {e}")
        raise e

def is_url_allowed(self, url: str, allowed_domains: list | None = None) -> bool:
    """Check if a URL is allowed based on the allowlist configuration."""
    if not allowed_domains:
        return True

    try:
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()

        # Remove port number if present
        if ':' in domain:
            domain = domain.split(':')[0]

        # Check if domain matches any allowed domain pattern
        return any(
            domain == allowed_domain.lower() or domain.endswith('.' + allowed_domain.lower())
            for allowed_domain in allowed_domains
        )
    except Exception as e:
        logging.error(f'Error checking URL allowlist: {str(e)}')
        return False

def initialize_navigation_history(self):
    """Initialize navigation history tracking for the browser session."""
    self.navigation_history = {
        "urls": [],
        "current_index": -1,
        "max_history": 100  # Maximum number of URLs to keep in history
    }

def add_to_navigation_history(self, url):
    """Add a URL to navigation history."""
    # If we've gone back and now navigate somewhere new, truncate forward history
    if self.navigation_history["current_index"] < len(self.navigation_history["urls"]) - 1:
        self.navigation_history["urls"] = self.navigation_history["urls"][:self.navigation_history["current_index"] + 1]
    
    # Add the new URL to history
    self.navigation_history["urls"].append(url)
    self.navigation_history["current_index"] += 1
    
    # Maintain maximum history size
    if len(self.navigation_history["urls"]) > self.navigation_history["max_history"]:
        self.navigation_history["urls"].pop(0)
        self.navigation_history["current_index"] -= 1

async def navigate_to_url(self, url, max_retries=3, retry_delay=1.0):
    """
    Enhanced navigation method with retry mechanism and history tracking.
    
    Args:
        url: URL to navigate to
        max_retries: Maximum number of retries on navigation failure
        retry_delay: Delay between retries in seconds
    
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    if not self._is_url_allowed(url):
        raise ValueError(f"Navigation to non-allowed URL: {url}")
    
    page = await self.get_current_page()
    retries = 0
    
    while retries <= max_retries:
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await self._wait_for_page_and_frames_load()
            
            # Add successful navigation to history
            self.add_to_navigation_history(url)
            return True
            
        except Exception as e:
            retries += 1
            if retries > max_retries:
                logging.error(f"Failed to navigate to {url} after {max_retries} attempts: {e}")
                return False
            
            logging.warning(f"Navigation attempt {retries} failed: {e}. Retrying in {retry_delay} seconds...")
            await asyncio.sleep(retry_delay)
            
            # Increase delay for each retry (exponential backoff)
            retry_delay *= 1.5
    
    return False

async def go_back_in_history(self, wait_for_load=True):
    """
    Go back in navigation history with enhanced error handling.
    
    Args:
        wait_for_load: Whether to wait for page to load after navigation
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    if self.navigation_history["current_index"] <= 0:
        logging.info("No previous page in history to go back to")
        return False
    
    page = await self.get_current_page()
    try:
        await page.go_back(timeout=10000)
        self.navigation_history["current_index"] -= 1
        
        if wait_for_load:
            await self._wait_for_page_and_frames_load()
        return True
    except Exception as e:
        logging.error(f"Failed to go back in history: {e}")
        return False

async def go_forward_in_history(self, wait_for_load=True):
    """
    Go forward in navigation history with enhanced error handling.
    
    Args:
        wait_for_load: Whether to wait for page to load after navigation
        
    Returns:
        bool: True if navigation was successful, False otherwise
    """
    if self.navigation_history["current_index"] >= len(self.navigation_history["urls"]) - 1:
        logging.info("No forward page in history to go to")
        return False
    
    page = await self.get_current_page()
    try:
        await page.go_forward(timeout=10000)
        self.navigation_history["current_index"] += 1
        
        if wait_for_load:
            await self._wait_for_page_and_frames_load()
        return True
    except Exception as e:
        logging.error(f"Failed to go forward in history: {e}")
        return False

def execute_dom_action(page, command):
    """
    Attempt to execute a command using DOM-based interaction first.
    Fallback to other methods if necessary.
    
    Args:
        page: The Playwright page object.
        command: A dict containing the action and any required parameters.
        
    Returns:
        bool: True if the action was successful, False otherwise.
    """
    from src.utils.dom_utils import DOMExplorer

    action = command.get("action")
    success = False

    if action == "click":
        # Try using a selector first, then text if selector isn't provided.
        if "selector" in command:
            success = DOMExplorer.find_and_interact(page, "button", command["selector"], action="click")
        elif "text" in command:
            success = DOMExplorer.find_and_interact(page, "button", command["text"], action="click")
    
    elif action == "input":
        if "selector" in command and "text" in command:
            success = DOMExplorer.find_and_interact(page, "input", command["selector"], action="fill", value=command["text"])
    
    elif action == "navigate":
        # Direct navigation using Playwright's goto method.
        try:
            page.goto(command.get("url"), timeout=60000)
            success = True
        except Exception as e:
            success = False

    # Add further actions (scroll, wait, etc.) as needed.

    return success

async def _wait_for_page_and_frames_load(self, timeout_ms=10000):
    """
    Enhanced method to wait for page and all frames to load completely.
    Handles timeouts gracefully and ensures all network activity is settled.
    
    Args:
        timeout_ms: Maximum time to wait in milliseconds
        
    Returns:
        bool: True if page loaded successfully, False if timeout occurred
    """
    page = await self.get_current_page()
    start_time = time.time()
    timeout_seconds = timeout_ms / 1000
    
    try:
        # First wait for domcontentloaded as a baseline
        await page.wait_for_load_state("domcontentloaded", timeout=timeout_ms)
        
        # Then wait for network to be mostly idle
        pending_requests = []
        completed = False
        
        # Set up request monitoring
        def on_request(request):
            pending_requests.append(request)
            
        def on_response(response):
            if response.request in pending_requests:
                pending_requests.remove(response.request)
                
        page.on("request", on_request)
        page.on("response", on_response)
        
        # Wait for network idle with timeout
        while time.time() - start_time < timeout_seconds:
            if len(pending_requests) == 0:
                # No pending requests for at least 500ms indicates network idle
                if not completed:
                    await asyncio.sleep(0.5)
                    if len(pending_requests) == 0:
                        completed = True
                        break
            await asyncio.sleep(0.1)
            
        # Clean up listeners
        page.remove_listener("request", on_request)
        page.remove_listener("response", on_response)
        
        # Try to wait for load state, but continue even if it times out
        try:
            await page.wait_for_load_state("load", timeout=2000)
        except:
            pass
            
        return completed
    except Exception as e:
        logging.warning(f"Page load wait timed out: {e}")
        return False

# Example usage:
#if __name__ == "__main__":
    browser = launch_browser_with_profile()
    page = browser.new_page()
    page.goto("https://example.com")
    print("Page title:", page.title())
    browser.close()
