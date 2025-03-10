import json
import re
import logging
import random
import time
from src.vision.ocr_processor import OCRProcessor
from src.capture.screen_capture import capture_screenshot
from src.utils.json_parser import extract_json

def simulate_human_mouse_movement(page):
    """Simulate random mouse movements like a human would make"""
    try:
        viewport_size = page.viewport_size
        if not viewport_size:
            return
            
        width, height = viewport_size["width"], viewport_size["height"]
        
        # Random mouse movements (1-3 movements)
        for _ in range(random.randint(1, 3)):
            # Move to random position on screen
            x = random.randint(100, width - 100)
            y = random.randint(100, height - 100)
            
            move_mouse_naturally(page, x, y)
            
            # Small pause between movements
            time.sleep(random.uniform(0.1, 0.5))
    except Exception as e:
        logging.error(f"Mouse movement simulation failed: {e}")

def move_mouse_naturally(page, target_x, target_y):
    """Move mouse in a natural curve rather than straight line"""
    try:
        # Get current position
        current_position = page.evaluate("""() => { 
            return {x: window.mouseX || 100, y: window.mouseY || 100}; 
        }""")
        
        start_x = current_position.get('x', 100)
        start_y = current_position.get('y', 100)
        
        # Calculate distance
        distance = ((target_x - start_x)**2 + (target_y - start_y)**2)**0.5
        
        # More points for longer distances
        steps = max(5, int(distance / 30))
        
        # Generate curve control point (for natural arc)
        control_x = (start_x + target_x) / 2 + random.randint(-100, 100)
        control_y = (start_y + target_y) / 2 + random.randint(-100, 100)
        
        # Move mouse along a quadratic curve
        for step in range(steps + 1):
            t = step / steps
            # Quadratic bezier curve
            x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * target_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * target_y
            
            page.mouse.move(x, y)
            
            # Add small delay between movements
            time.sleep(random.uniform(0.005, 0.02))
            
    except Exception as e:
        logging.error(f"Natural mouse movement failed: {e}")
        # Fallback to direct movement
        page.mouse.move(target_x, target_y)

def execute_actions(page, ai_response: str):
    """
    Execute actions from AI response with enhanced human-like behavior
    
    :param page: A Playwright page instance
    :param ai_response: The AI-generated response
    :return: List of actions performed
    """
    commands_data = extract_json(ai_response)
    if commands_data is None:
        logging.error("Failed to extract commands from AI response.")
        return []
    
    if "analysis" in commands_data:
        logging.info("AI Analysis: %s", commands_data["analysis"])
    
    actions_performed = []
    commands = commands_data.get("commands", [])
    
    for cmd in commands:
        # Add human-like delay between actions (1-2 seconds)
        delay = random.uniform(0.5, 2.0)
        logging.info(f"Adding human-like delay of {delay:.1f} seconds")
        time.sleep(delay)
        
        # Simulate random mouse movements
        simulate_human_mouse_movement(page)
        
        action = cmd.get("action")
        
        if action == "navigate":
            url = cmd.get("url")
            if url:
                logging.info("Navigating to URL: %s", url)
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)  # Wait for page to stabilize
                    actions_performed.append(f"Navigated to {url}")
                except Exception as e:
                    logging.error(f"Navigation failed: {e}")
        
        elif action == "click":
            selector = cmd.get("selector")
            text = cmd.get("text")
            submit = cmd.get("submit", False)
            
            # Special handling for Google cookie consent
            if text and ("accept" in text.lower() or "agree" in text.lower()):
                try:
                    # Consent button selectors for various sites
                    consent_selectors = [
                        "button[aria-label='Accept all']",
                        "#L2AGLb",  # Google's consent button ID
                        ".tHlp8d",  # Google's consent button class
                        "form[action*='consent'] button",
                        "div[role='dialog'] button:last-child",
                        "button:has-text('Accept')",
                        "button:has-text('Accept all')",
                        "button:has-text('I agree')"
                    ]
                    
                    for consent_selector in consent_selectors:
                        try:
                            if page.is_visible(consent_selector, timeout=1000):
                                # Move mouse naturally to the element
                                element_position = page.evaluate(f"""() => {{
                                    const element = document.querySelector('{consent_selector}');
                                    if (!element) return null;
                                    const rect = element.getBoundingClientRect();
                                    return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                                }}""")
                                
                                if element_position:
                                    move_mouse_naturally(page, element_position['x'], element_position['y'])
                                
                                page.click(consent_selector)
                                actions_performed.append(f"Clicked consent button: {consent_selector}")
                                # Wait to ensure the action completes
                                page.wait_for_timeout(1000)
                                break
                        except Exception as e:
                            continue
                    
                    # If we couldn't click using selectors, try visible elements with matching text
                    if not actions_performed:
                        # Use evaluate to find and click the button via JavaScript
                        clicked = page.evaluate('''() => {
                            const buttons = Array.from(document.querySelectorAll('button'));
                            const acceptButton = buttons.find(button => 
                                (button.textContent.toLowerCase().includes('accept all') || 
                                button.textContent.toLowerCase().includes('i agree') ||
                                button.textContent.toLowerCase().includes('agree')) && 
                                button.offsetParent !== null
                            );
                            if (acceptButton) {
                                acceptButton.click();
                                return true;
                            }
                            return false;
                        }''')
                        
                        if clicked:
                            actions_performed.append("Clicked Accept button via JavaScript")
                            page.wait_for_timeout(1000)
                            
                except Exception as e:
                    logging.error(f"Consent click action failed: {e}")
            
            # Regular element clicking with human-like mouse movement
            elif selector:
                try:
                    if page.is_visible(selector, timeout=3000):
                        # Move mouse naturally to the element
                        element_position = page.evaluate(f"""() => {{
                            const element = document.querySelector('{selector}');
                            if (!element) return null;
                            const rect = element.getBoundingClientRect();
                            return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                        }}""")
                        
                        if element_position:
                            move_mouse_naturally(page, element_position['x'], element_position['y'])
                        
                        # Add a small random delay before clicking (like a human deciding)
                        time.sleep(random.uniform(0.1, 0.5))
                        page.click(selector)
                        actions_performed.append(f"Clicked element with selector: {selector}")
                    else:
                        logging.error(f"Element with selector {selector} not visible")
                except Exception as e:
                    logging.error(f"Click action failed: {e}")
            
            # Click by text as fallback
            elif text:
                try:
                    # Try different text matching strategies
                    text_strategies = [
                        f"text=\"{text}\"",            # Exact match
                        f"text='{text}'",              # Contains match
                        f"text=/^{text}$/i",           # Case-insensitive exact match
                        f"text=/.*{text}.*/i",         # Case-insensitive contains
                        f"[aria-label*='{text}']",     # Aria label contains
                        f"button:has-text('{text}')",  # Button with text
                        f":text('{text}')"             # Any element with text
                    ]
                    
                    for strategy in text_strategies:
                        try:
                            if page.is_visible(strategy, timeout=1000):
                                # Get element position for natural mouse movement
                                element_position = page.evaluate(f"""() => {{
                                    const element = document.querySelector('{strategy}');
                                    if (!element) return null;
                                    const rect = element.getBoundingClientRect();
                                    return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                                }}""")
                                
                                if element_position:
                                    move_mouse_naturally(page, element_position['x'], element_position['y'])
                                
                                time.sleep(random.uniform(0.1, 0.3))
                                page.click(strategy)
                                actions_performed.append(f"Clicked element with text: {text}")
                                break
                        except:
                            continue
                except Exception as e:
                    logging.error(f"Text click failed: {e}")
        
        elif action == "input":
            selector = cmd.get("selector")
            text = cmd.get("text", "")
            submit = cmd.get("submit", False)
            
            # Special handling for Amazon search
            if "amazon" in page.url and (selector == "input[name='q']" or "search" in selector.lower()):
                # Use the correct Amazon search box selector
                amazon_search = "input[id='twotabsearchtextbox']"
                try:
                    if page.is_visible(amazon_search, timeout=2000):
                        # Move mouse naturally to the element
                        element_position = page.evaluate(f"""() => {{
                            const element = document.querySelector('{amazon_search}');
                            if (!element) return null;
                            const rect = element.getBoundingClientRect();
                            return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                        }}""")
                        
                        if element_position:
                            move_mouse_naturally(page, element_position['x'], element_position['y'])
                        
                        page.click(amazon_search)
                        page.fill(amazon_search, "")
                        
                        # Type with human-like delays
                        for char in text:
                            page.type(amazon_search, char, delay=random.randint(50, 200))
                            time.sleep(random.uniform(0.01, 0.05))
                        
                        actions_performed.append(f"Typed '{text}' into Amazon search box")
                        
                        if submit:
                            # Use Amazon's search submit button
                            submit_button = "input[id='nav-search-submit-button']"
                            if page.is_visible(submit_button, timeout=1000):
                                page.click(submit_button)
                            else:
                                # Or press Enter if button not found
                                page.press(amazon_search, "Enter")
                            actions_performed.append("Submitted Amazon search")
                            page.wait_for_timeout(3000)
                        return actions_performed
                    else:
                        logging.error(f"Amazon search box not visible")
                except Exception as e:
                    logging.error(f"Amazon search failed: {e}")
            
            # Regular input handling with human-like typing
            elif selector:
                try:
                    if page.is_visible(selector, timeout=3000):
                        # Move mouse to input field naturally
                        element_position = page.evaluate(f"""() => {{
                            const element = document.querySelector('{selector}');
                            if (!element) return null;
                            const rect = element.getBoundingClientRect();
                            return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                        }}""")
                        
                        if element_position:
                            move_mouse_naturally(page, element_position['x'], element_position['y'])
                        
                        page.click(selector)
                        
                        # Clear field
                        page.fill(selector, "")
                        
                        # Type with human-like delays
                        for char in text:
                            page.type(selector, char, delay=random.randint(50, 200))
                            time.sleep(random.uniform(0.01, 0.05))
                        
                        actions_performed.append(f"Typed '{text}' into {selector}")
                        
                        if submit:
                            # Pause before pressing Enter
                            time.sleep(random.uniform(0.5, 1.5))
                            page.press(selector, "Enter")
                            actions_performed.append("Pressed Enter to submit")
                    else:
                        logging.error(f"Input field {selector} not visible")
                except Exception as e:
                    logging.error(f"Input action failed: {e}")
        
        elif action == "scroll":
            direction = cmd.get("direction", "down")
            amount = cmd.get("amount", 300)
            
            try:
                # Make scrolling more natural with variable speed
                total_scroll = 0
                target_amount = amount
                
                # Break scrolling into smaller, variable chunks
                while total_scroll < target_amount:
                    # Variable chunk size
                    chunk = min(random.randint(50, 120), target_amount - total_scroll)
                    total_scroll += chunk
                    
                    if direction == "down":
                        page.evaluate(f"window.scrollBy(0, {chunk})")
                    elif direction == "up":
                        page.evaluate(f"window.scrollBy(0, -{chunk})")
                    
                    # Variable pause between scroll chunks
                    time.sleep(random.uniform(0.03, 0.10))
                
                actions_performed.append(f"Scrolled {direction} {amount} pixels")
            except Exception as e:
                logging.error(f"Scroll failed: {e}")
        
        # Wait after each action with a variable delay
        page.wait_for_timeout(random.randint(300, 1000))
    
    return actions_performed

# Add this function to action_executor.py after the existing functions

def handle_cookie_banner(page):
    """
    Enhanced function to handle cookie banners with multiple strategies.
    Prioritizes rejecting cookies when possible, falls back to accepting if needed.
    Returns True if successfully handled, False otherwise.
    """
    print("Attempting to handle cookie banner with multiple strategies...")
    
    # # Strategy 1: Try to REJECT cookies first using common button selectors
    reject_selectors = [
        "button#CybotCookiebotDialogBodyButtonDecline",  # Common Cookiebot reject button
        "button:has-text('Reject all')",
        "button:has-text('Reject')",
        "button:has-text('Decline')",
        "button:has-text('No, thanks')",
        "#reject-all-cookies",
        ".reject-cookies-button",
        "[aria-label='Reject all']"
    ]
    
    for selector in reject_selectors:
        try:
            if page.is_visible(selector, timeout=1000):
                print(f"Found reject button with selector: {selector}")
                page.click(selector)
                page.wait_for_timeout(1000)
                return True
        except Exception as e:
            print(f"Failed to click reject selector {selector}: {e}")        
    # Strategy 2: If reject fails, try ACCEPT buttons (fallback)
    accept_selectors = [
        "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        "#cookie-accept-all",
        ".cookie-accept-all",
        ".accept-cookies-button",
        "button[aria-label='Accept all']",
        "#accept-all-cookies",
        ".accept-all-cookies",
        "button:has-text('Accept all')",
        "button:has-text('Allow all')"
    ]
    
    for selector in accept_selectors:
        try:
            if page.is_visible(selector, timeout=1000):
                print(f"Found accept button with selector: {selector}")
                page.click(selector)
                page.wait_for_timeout(1000)
                return True
        except Exception as e:
            print(f"Failed to click accept selector {selector}: {e}")
    
    # Strategy 3: Try iframe handling (many cookie banners are in iframes)
    try:
        frames = page.frames
        for frame in frames:
            if "cookie" in frame.url.lower() or "consent" in frame.url.lower():
                print(f"Found cookie iframe: {frame.url}")
                
                # Try reject first in the iframe
                frame_reject_selectors = [
                    "button:has-text('Reject all')",
                    "button:has-text('Reject')",
                    "#reject-button"
                ]
                
                for selector in frame_reject_selectors:
                    try:
                        if frame.is_visible(selector, timeout=1000):
                            frame.click(selector)
                            page.wait_for_timeout(1000)
                            return True
                    except:
                        continue
                
                # Then try accept buttons in the iframe
                frame_accept_selectors = [
                    "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                    "button:has-text('Accept all')",
                    "button:has-text('Allow all')",
                    ".accept-all"
                ]
                
                for selector in frame_accept_selectors:
                    try:
                        if frame.is_visible(selector, timeout=1000):
                            frame.click(selector)
                            page.wait_for_timeout(1000)
                            return True
                    except:
                        continue
    except Exception as e:
        print(f"Failed to handle cookie frame: {e}")
    
    # Strategy 4: JavaScript approach - first reject, then accept as fallback
    try:
        # First try to find and click reject buttons via JavaScript
        reject_js = """
        function findAndClickButton(searchTexts) {
            // Get all buttons
            const buttons = Array.from(document.querySelectorAll('button, a.button, input[type="button"], div[role="button"]'));
            
            // Check each button for text match
            for (const button of buttons) {
                const buttonText = button.textContent || button.value || '';
                for (const searchText of searchTexts) {
                    if (buttonText.toLowerCase().includes(searchText.toLowerCase()) && 
                        button.offsetParent !== null) {
                        button.click();
                        return true;
                    }
                }
            }
            return false;
        }
        
        // Try different reject button texts
        return findAndClickButton(['reject all', 'reject', 'decline', 'no thanks']);
        """
        
        result = page.evaluate(reject_js)
        if result:
            print("Successfully clicked reject button via JavaScript")
            page.wait_for_timeout(1000)
            return True
            
        # If reject fails, try accept buttons
        accept_js = """
        function findAndClickButton(searchTexts) {
            // Get all buttons
            const buttons = Array.from(document.querySelectorAll('button, a.button, input[type="button"], div[role="button"]'));
            
            // Check each button for text match
            for (const button of buttons) {
                const buttonText = button.textContent || button.value || '';
                for (const searchText of searchTexts) {
                    if (buttonText.toLowerCase().includes(searchText.toLowerCase()) && 
                        button.offsetParent !== null) {
                        button.click();
                        return true;
                    }
                }
            }
            return false;
        }
        
        // Try different common accept button texts
        return findAndClickButton(['allow all', 'accept all', 'accept cookies', 'agree', 'accept']);
        """
        
        result = page.evaluate(accept_js)
        if result:
            print("Successfully clicked accept button via JavaScript")
            page.wait_for_timeout(1000)
            return True
    except Exception as e:
        print(f"JavaScript cookie handling failed: {e}")
    
    # Strategy 5: Click at positions where cookie buttons typically appear
    try:
        # Common positions for buttons (percentages of viewport)
        width = page.viewport_size["width"]
        height = page.viewport_size["height"]
        
        # Common positions for Reject buttons (usually on the left side)
        reject_positions = [
            (width * 0.25, height * 0.9),  # Bottom left
            (width * 0.35, height * 0.9)   # Bottom left-center
        ]
        
        for x, y in reject_positions:
            try:
                page.mouse.click(x, y)
                print(f"Attempted click at position x={x}, y={y} (reject)")
                page.wait_for_timeout(1000)
                
                # Check if banner is still visible
                ocr_text = " ".join([item.get('text', '').lower() for item in OCRProcessor().process_image(capture_screenshot(page))])
                if "cookie" not in ocr_text and "consent" not in ocr_text:
                    print("Banner appears to be gone after position click")
                    return True
            except:
                continue
        
        # Common positions for Accept buttons (usually on the right side)
        accept_positions = [
            (width * 0.85, height * 0.9),  # Bottom right
            (width * 0.75, height * 0.9),  # Bottom right-center
            (width * 0.65, height * 0.9)   # Bottom center-right
        ]
        
        for x, y in accept_positions:
            try:
                page.mouse.click(x, y)
                print(f"Attempted click at position x={x}, y={y} (accept)")
                page.wait_for_timeout(1000)
                
                # Check if banner is still visible
                ocr_text = " ".join([item.get('text', '').lower() for item in OCRProcessor().process_image(capture_screenshot(page))])
                if "cookie" not in ocr_text and "consent" not in ocr_text:
                    print("Banner appears to be gone after position click")
                    return True
            except:
                continue
    except Exception as e:
        print(f"Position-based cookie handling failed: {e}")
    
    print("All cookie banner handling strategies failed")
    return False

def find_natural_search_results(page):
    """Find natural (non-sponsored) search result links"""
    try:
        # Try to identify natural results while avoiding ads
        natural_selectors = [
            "div:not([data-text-ad]) a[ping]",
            ".g:not(.ads-ad) a[href]",
            "#search a[href]:not([data-jsarwt])",
            "h3[class*='LC20lb']" # Google's organic result heading class
        ]
        
        for selector in natural_selectors:
            try:
                # Get all natural results
                links = page.query_selector_all(selector)
                if links and len(links) > 0:
                    # Return the first natural result
                    return links[0]
            except Exception as e:
                logging.error(f"Error finding results with selector {selector}: {e}")
                continue
        
        return None
    except Exception as e:
        logging.error(f"Error finding natural search results: {e}")
        return None