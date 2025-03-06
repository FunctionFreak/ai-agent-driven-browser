# src/handlers/search_handler.py

import logging
import time
from playwright.sync_api import Page

class SearchHandler:
    """Handler for detecting and interacting with search interfaces across different websites"""
    
    def __init__(self):
        # Common search indicator text patterns
        self.search_text_patterns = [
            "search", "find", "look up", "browse", "explore"
        ]
        
        # Common search icon element patterns
        self.search_icon_patterns = [
            "magnifying glass", "search icon", "lens icon"
        ]
    
    def detect_search_interface(self, page: Page, ocr_results: list):
        """
        Detect search interface on current page using multiple strategies
        
        Args:
            page: Playwright page object
            ocr_results: List of OCR detected text items with bounding boxes
            
        Returns:
            dict: Information about detected search interface or None
        """
        logging.info("Attempting to detect search interface")
        
        # Strategy 1: Try common search input selectors
        search_input = self._try_common_selectors(page)
        if search_input:
            return search_input
            
        # Strategy 2: Look for search text in OCR results
        search_by_text = self._find_search_by_ocr(page, ocr_results)
        if search_by_text:
            return search_by_text
            
        # Strategy 3: Try to find and click search icons
        search_by_icon = self._find_and_click_search_icon(page, ocr_results)
        if search_by_icon:
            return search_by_icon
            
        logging.warning("No search interface detected using available strategies")
        return None
    
    def _try_common_selectors(self, page: Page):
        """Try common search input selectors across different websites"""
        common_selectors = [
            # Amazon
            "input[id='twotabsearchtextbox']", 
            
            # Google
            "textarea[name='q']",
            "input[name='q']",
            
            # Common patterns
            "input[type='search']",
            "input[placeholder*='search' i]",
            "input[aria-label*='search' i]",
            "[role='search'] input",
            ".search-box",
            "#search-box",
            "input.search"
        ]
        
        for selector in common_selectors:
            try:
                if page.is_visible(selector, timeout=500):
                    logging.info(f"Found search input with selector: {selector}")
                    return {
                        "type": "input",
                        "selector": selector,
                        "requires_submit": True,
                        "submit_selector": self._find_submit_button(page, selector)
                    }
            except Exception as e:
                continue
                
        return None
    
    def _find_submit_button(self, page: Page, input_selector: str):
        """Find the corresponding submit button for a search input"""
        # Common patterns for submit buttons related to search
        submit_selectors = [
            # Form submit button
            "form:has(#{0}) button[type='submit']",
            "form:has(#{0}) input[type='submit']",
            
            # Amazon specific
            "input[id='nav-search-submit-button']",
            
            # Generic patterns
            "button.search-submit",
            "button[aria-label*='search' i]",
            "button:has(.search-icon)",
            "button svg[aria-label*='search' i]"
        ]
        
        # Extract ID from the input selector if available
        input_id = None
        import re
        id_match = re.search(r"id=['\"]([^'\"]+)['\"]", input_selector)
        if id_match:
            input_id = id_match.group(1)
        
        # Try to find the submit button
        for selector in submit_selectors:
            if input_id:
                actual_selector = selector.format(input_id)
            else:
                actual_selector = selector
                
            try:
                if page.is_visible(actual_selector, timeout=500):
                    return actual_selector
            except:
                continue
                
        # Default to just pressing Enter if no submit button found
        return None
    
    def _find_search_by_ocr(self, page: Page, ocr_results: list):
        """Find search elements using OCR text results"""
        search_texts = []
        
        # Find all texts that might indicate search functionality
        for item in ocr_results:
            text = item.get('text', '').lower()
            for pattern in self.search_text_patterns:
                if pattern in text:
                    search_texts.append(item)
                    break
        
        # Try clicking on search text elements to reveal search inputs
        for item in search_texts:
            try:
                # Get center of bounding box
                bbox = item.get('bbox', [])
                if not bbox:
                    continue
                    
                # Calculate center point
                center_x = (bbox[0][0] + bbox[2][0]) / 2
                center_y = (bbox[0][1] + bbox[2][1]) / 2
                
                # Click at the center point
                page.mouse.click(center_x, center_y)
                
                # Wait for potential search input to appear
                time.sleep(0.5)
                
                # Check if any search input is now visible
                search_input = self._try_common_selectors(page)
                if search_input:
                    return search_input
                    
            except Exception as e:
                logging.error(f"Error clicking search text: {e}")
                continue
                
        return None
        
    def _find_and_click_search_icon(self, page: Page, ocr_results: list):
        """Find and click on elements that might be search icons"""
        # Try common search icon selectors
        icon_selectors = [
            "button svg[aria-label*='search' i]",
            "a svg[aria-label*='search' i]",
            "button[aria-label*='search' i]",
            "a[aria-label*='search' i]",
            ".search-icon",
            "#search-icon",
            "[data-icon='search']"
        ]
        
        for selector in icon_selectors:
            try:
                if page.is_visible(selector, timeout=500):
                    # Click the icon
                    page.click(selector)
                    
                    # Wait for potential search input to appear
                    time.sleep(0.5)
                    
                    # Check if search input appeared
                    search_input = self._try_common_selectors(page)
                    if search_input:
                        return search_input
            except:
                continue
                
        # Search for magnifying glass icon in OCR
        for item in ocr_results:
            text = item.get('text', '').lower()
            if "🔍" in text or "search" in text:
                try:
                    # Get center of bounding box
                    bbox = item.get('bbox', [])
                    if not bbox:
                        continue
                        
                    # Calculate center point
                    center_x = (bbox[0][0] + bbox[2][0]) / 2
                    center_y = (bbox[0][1] + bbox[2][1]) / 2
                    
                    # Click at the center point
                    page.mouse.click(center_x, center_y)
                    
                    # Wait for potential search input to appear
                    time.sleep(0.5)
                    
                    # Check if any search input is now visible
                    search_input = self._try_common_selectors(page)
                    if search_input:
                        return search_input
                        
                except Exception as e:
                    logging.error(f"Error clicking search icon: {e}")
                    continue
        
        return None
    
    def perform_search(self, page: Page, search_term: str, ocr_results: list):
        """
        Perform search on the current page
        
        Args:
            page: Playwright page object
            search_term: The term to search for
            ocr_results: OCR results for additional context
            
        Returns:
            bool: True if search was successfully performed
        """
        # First detect the search interface
        search_interface = self.detect_search_interface(page, ocr_results)
        
        if not search_interface:
            logging.error("No search interface detected")
            return False
            
        try:
            # Get the selector for the search input
            selector = search_interface.get('selector')
            
            # Click and focus on the search input
            page.click(selector)
            
            # Clear existing text
            page.fill(selector, "")
            
            # Type search term with humanlike delays
            import random
            for char in search_term:
                page.type(selector, char, delay=random.randint(50, 150))
                time.sleep(random.uniform(0.01, 0.03))
                
            # Submit the search
            submit_selector = search_interface.get('submit_selector')
            if submit_selector:
                # Use the submit button
                page.click(submit_selector)
            else:
                # Press Enter to submit
                page.press(selector, "Enter")
                
            # Wait for results to load
            page.wait_for_timeout(3000)
            
            logging.info(f"Successfully performed search for: {search_term}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to perform search: {e}")
            return False