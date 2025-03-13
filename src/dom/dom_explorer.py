# File: src/dom/dom_explorer.py

import logging

# Try to import BeautifulSoup but don't fail if it's not available
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    logging.warning("BeautifulSoup4 (bs4) not found. Some DOM parsing features will be unavailable. Install with: pip install beautifulsoup4")

class DOMExplorer:
    def __init__(self, html_content=None):
        if BS4_AVAILABLE and html_content:
            self.soup = BeautifulSoup(html_content, 'html.parser')
        else:
            self.soup = None

    def find_by_text(self, text):
        if not self.soup:
            return []
        return self.soup.find_all(text=lambda t: text.lower() in t.lower())

    def find_interactive_elements(self):
        if not self.soup:
            return {}
        
        buttons = self.soup.find_all(['button', 'input[type="button"]', 'input[type="submit"]'])
        links = self.soup.find_all('a')
        inputs = self.soup.find_all(['input[type="text"]', 'input[type="email"]', 'textarea'])
        selects = self.soup.find_all('select')
        
        return {
            'buttons': len(buttons),
            'links': len(links),
            'inputs': len(inputs),
            'selects': len(selects)
        }

    def find_elements_with_attribute(self, attribute, value=None):
        if not self.soup:
            return []
        
        if value:
            return self.soup.find_all(lambda tag: tag.has_attr(attribute) and tag[attribute] == value)
        else:
            return self.soup.find_all(lambda tag: tag.has_attr(attribute))

    def find_shadow_dom(self):
        # This is a placeholder as BeautifulSoup can't directly handle shadow DOM
        pass
    
    @staticmethod
    def find_interactive_elements(page):
        """
        Find interactive elements on the page using page evaluation.
        
        Args:
            page: Playwright page object
            
        Returns:
            dict: Counts of different interactive element types
        """
        try:
            result = page.evaluate("""() => {
                const buttons = document.querySelectorAll('button, input[type="button"], input[type="submit"], [role="button"]');
                const links = document.querySelectorAll('a');
                const inputs = document.querySelectorAll('input[type="text"], input[type="email"], textarea, [contenteditable="true"]');
                const selects = document.querySelectorAll('select, [role="listbox"]');
                const searchBoxes = Array.from(document.querySelectorAll('input[type="search"], input[name="q"], input[placeholder*="search" i], input[aria-label*="search" i]'))
                    .map(el => ({
                        id: el.id,
                        name: el.name,
                        placeholder: el.placeholder,
                        ariaLabel: el.getAttribute('aria-label')
                    }));
                
                // Extract heading text content
                const headings = {};
                for (let i = 1; i <= 6; i++) {
                    const headingEls = document.querySelectorAll(`h${i}`);
                    if (headingEls.length > 0) {
                        headings[`h${i}`] = Array.from(headingEls).map(el => el.textContent.trim()).slice(0, 3);
                    }
                }
                
                return {
                    buttons: buttons.length,
                    links: links.length,
                    inputs: inputs.length,
                    selects: selects.length,
                    search_boxes: searchBoxes,
                    headings: headings
                };
            }""")
            return result
        except Exception as e:
            logging.error(f"Error finding interactive elements: {e}")
            return {
                "buttons": 0,
                "links": 0,
                "inputs": 0,
                "selects": 0,
                "search_boxes": [],
                "headings": {}
            }
    
    @staticmethod
    def find_cookie_consent(page):
        """
        Find and handle cookie consent banners using DOM techniques.
        
        Args:
            page: Playwright page object
            
        Returns:
            bool: True if a cookie banner was successfully handled, False otherwise
        """
        try:
            result = page.evaluate("""() => {
                // Common cookie banner selectors
                const cookieSelectors = [
                    '[id*="cookie" i]',
                    '[class*="cookie" i]',
                    '[id*="consent" i]',
                    '[class*="consent" i]',
                    '[id*="gdpr" i]',
                    '[class*="gdpr" i]',
                    '[aria-label*="cookie" i]',
                    '#CybotCookiebotDialog',
                    '.cc-window',
                    '.cookie-banner',
                    '.cookie-policy',
                    '.cookie-notice'
                ];
                
                // Check if any cookie banner is present
                let cookieBanner = null;
                for (const selector of cookieSelectors) {
                    const element = document.querySelector(selector);
                    if (element && element.offsetParent !== null) {
                        cookieBanner = element;
                        break;
                    }
                }
                
                // If found, try to handle it
                if (cookieBanner) {
                    // First try to find and click reject/decline buttons
                    const rejectTexts = ['reject', 'decline', 'no, thanks', 'opt-out', 'refuse'];
                    for (const text of rejectTexts) {
                        const buttons = Array.from(cookieBanner.querySelectorAll('button, a, .button'));
                        for (const button of buttons) {
                            if (button.textContent.toLowerCase().includes(text) && button.offsetParent !== null) {
                                button.click();
                                return true;
                            }
                        }
                    }
                    
                    // If no reject button found, try accept/agree buttons
                    const acceptTexts = ['accept', 'agree', 'allow', 'got it', 'understand', 'i accept', 'ok', 'continue'];
                    for (const text of acceptTexts) {
                        const buttons = Array.from(cookieBanner.querySelectorAll('button, a, .button'));
                        for (const button of buttons) {
                            if (button.textContent.toLowerCase().includes(text) && button.offsetParent !== null) {
                                button.click();
                                return true;
                            }
                        }
                    }
                }
                
                return false;
            }""")
            
            return result
        except Exception as e:
            logging.error(f"Error handling cookie consent: {e}")
            return False
