# src/utils/dom_utils.py

import logging
from playwright.sync_api import Page, TimeoutError

class DOMExplorer:
    """
    Utility class for exploring and interacting with DOM elements
    using Playwright's capabilities, reducing reliance on vision.
    """
    
    @staticmethod
    def find_element_by_role(page: Page, role: str, name: str = None, timeout: int = 3000):
        """
        Find an element by its ARIA role and optional name.
        
        Args:
            page: Playwright page object
            role: ARIA role (button, link, textbox, etc.)
            name: Optional name or text content
            timeout: Time to wait for element in ms
            
        Returns:
            Element if found, None otherwise
        """
        try:
            if name:
                locator = page.get_by_role(role, name=name)
            else:
                locator = page.get_by_role(role)
                
            return locator.first.element_handle(timeout=timeout) if locator.count() > 0 else None
        except Exception as e:
            logging.debug(f"Could not find element with role {role}, name {name}: {e}")
            return None
    
    @staticmethod
    def find_interactive_elements(page: Page):
        """
        Find all potentially interactive elements on the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary of interactive elements grouped by type
        """
        try:
            # Get counts of various interactive elements
            elements = {
                "buttons": page.get_by_role("button").count(),
                "links": page.get_by_role("link").count(),
                "inputs": page.locator("input, textarea").count(),
                "selects": page.get_by_role("combobox").count()
            }
            
            # Get details about search-related elements
            search_elements = page.locator("input[type='search'], input[name='q'], input[placeholder*='search' i]").all()
            elements["search_boxes"] = [{
                "selector": page.evaluate("el => el.outerHTML", element),
                "placeholder": page.evaluate("el => el.placeholder || ''", element)
            } for element in search_elements]
            
            return elements
        except Exception as e:
            logging.error(f"Error finding interactive elements: {e}")
            return {}
        
    @staticmethod
    def extract_page_content(page: Page):
        """
        Extract meaningful text content from the page.
        
        Args:
            page: Playwright page object
            
        Returns:
            Dictionary with page title, headings, and main content
        """
        try:
            # Basic page information
            content = {
                "url": page.url,
                "title": page.title()
            }
            
            # Extract headings
            headings = {}
            for level in range(1, 7):
                elements = page.locator(f"h{level}").all()
                if elements:
                    headings[f"h{level}"] = [page.evaluate("el => el.textContent", element) for element in elements]
            
            content["headings"] = headings
            
            # Extract main content text
            content["main_text"] = page.evaluate("""() => {
                const article = document.querySelector('article');
                if (article) return article.textContent.trim();
                
                const main = document.querySelector('main');
                if (main) return main.textContent.trim();
                
                // Fallback to body text, excluding scripts
                return Array.from(document.body.childNodes)
                    .filter(node => node.nodeType === Node.TEXT_NODE || 
                                  (node.nodeType === Node.ELEMENT_NODE && 
                                   node.tagName !== 'SCRIPT' && 
                                   node.tagName !== 'STYLE'))
                    .map(node => node.textContent)
                    .join(' ')
                    .replace(/\\s+/g, ' ')
                    .trim();
            }""")
            
            return content
        except Exception as e:
            logging.error(f"Error extracting page content: {e}")
            return {"url": page.url, "error": str(e)}
    
    @staticmethod
    def find_and_interact(page: Page, element_type: str, identifier: str, action: str = "click", value: str = None):
        """
        Find an element and interact with it based on the specified action.
        
        Args:
            page: Playwright page object
            element_type: Type of element (button, link, input, etc.)
            identifier: Text, placeholder, or other identifying attribute
            action: Action to perform (click, fill, etc.)
            value: Value to fill if action is 'fill'
            
        Returns:
            True if interaction was successful, False otherwise
        """
        try:
            locator = None
            
            # Select appropriate locator strategy based on element type
            if element_type == "button":
                locator = page.get_by_role("button", name=identifier)
                
            elif element_type == "link":
                locator = page.get_by_role("link", name=identifier)
                
            elif element_type == "input":
                # Try multiple strategies to find the input
                input_selectors = [
                    f"input[placeholder='{identifier}']",
                    f"input[name='{identifier}']",
                    f"input[aria-label='{identifier}']",
                    f"textarea[placeholder='{identifier}']"
                ]
                
                for selector in input_selectors:
                    if page.locator(selector).count() > 0:
                        locator = page.locator(selector)
                        break
            
            # Fallback to text search if no element found yet
            if not locator or locator.count() == 0:
                locator = page.get_by_text(identifier, exact=False)
            
            # Perform the requested action
            if locator and locator.count() > 0:
                if action == "click":
                    locator.first.click()
                    return True
                elif action == "fill" and value:
                    locator.first.fill(value)
                    return True
            
            return False
        except Exception as e:
            logging.error(f"Error interacting with {element_type} {identifier}: {e}")
            return False
    
    @staticmethod
    def find_cookie_consent(page: Page):
        """
        Detect and handle cookie consent dialogs using DOM properties.
        
        Args:
            page: Playwright page object
            
        Returns:
            True if consent was handled, False otherwise
        """
        try:
            # Common text patterns in cookie consent buttons
            consent_buttons = [
                {"text": "Reject all", "priority": 1},  # Higher priority (lower number)
                {"text": "Reject", "priority": 1},
                {"text": "Decline", "priority": 1},
                {"text": "Accept all", "priority": 2},
                {"text": "Accept cookies", "priority": 2},
                {"text": "I agree", "priority": 2},
                {"text": "Agree", "priority": 2},
                {"text": "Allow all", "priority": 2}
            ]
            
            # Sort by priority (reject first, then accept)
            consent_buttons.sort(key=lambda x: x["priority"])
            
            for button in consent_buttons:
                try:
                    locator = page.get_by_role("button", name=button["text"], exact=False)
                    if locator.count() > 0 and locator.first.is_visible():
                        locator.first.click()
                        logging.info(f"Clicked cookie consent button: {button['text']}")
                        return True
                except:
                    continue
            
            # Try common consent dialog selectors
            consent_selectors = [
                "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
                "#onetrust-accept-btn-handler",
                ".cookie-banner__button",
                "[aria-label*='cookie' i]",
                "#accept-cookie-banner"
            ]
            
            for selector in consent_selectors:
                try:
                    if page.locator(selector).count() > 0 and page.locator(selector).first.is_visible():
                        page.locator(selector).first.click()
                        logging.info(f"Clicked cookie consent selector: {selector}")
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            logging.error(f"Error handling cookie consent: {e}")
            return False