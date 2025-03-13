import logging
import asyncio
import random
import time
from typing import List, Optional, Dict, Any, Union

async def dismiss_cookie_banner(page):
    """
    Attempt to dismiss cookie consent banners using multiple strategies.
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if a cookie banner was successfully dismissed, False otherwise
    """
    logging.info("Attempting to dismiss cookie banner...")
    
    # Strategy 1: Common cookie banner selectors - prioritizing reject buttons
    reject_selectors = [
        "button:has-text('Reject all')",
        "button:has-text('Reject cookies')",
        "button:has-text('Reject')",
        "button:has-text('Decline')",
        "button:has-text('No, thanks')",
        "#reject-button",
        "[aria-label*='reject' i]",
        "[data-testid*='reject' i]",
        ".reject-cookies"
    ]
    
    # Try reject buttons first
    for selector in reject_selectors:
        try:
            is_visible = await page.is_visible(selector, timeout=1000)
            if is_visible:
                # Add small random delay to appear more human-like
                await asyncio.sleep(random.uniform(0.2, 0.7))
                await page.click(selector)
                logging.info(f"Clicked reject cookie button: {selector}")
                await asyncio.sleep(random.uniform(0.5, 1.0))
                return True
        except Exception as e:
            logging.debug(f"Failed to click reject selector {selector}: {e}")
    
    # Strategy 2: Accept button selectors (if reject is not available)
    accept_selectors = [
        "button:has-text('Accept all')",
        "button:has-text('Accept cookies')",
        "button:has-text('Accept')",
        "button:has-text('Allow all')",
        "button:has-text('I agree')",
        "button:has-text('Agree')",
        "button#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
        "#accept-button",
        ".accept-cookies",
        "[aria-label*='accept' i]"
    ]
    
    # If reject fails, try accept buttons
    for selector in accept_selectors:
        try:
            is_visible = await page.is_visible(selector, timeout=1000)
            if is_visible:
                # Add small random delay to appear more human-like
                await asyncio.sleep(random.uniform(0.2, 0.7))
                await page.click(selector)
                logging.info(f"Clicked accept cookie button: {selector}")
                await asyncio.sleep(random.uniform(0.5, 1.0))
                return True
        except Exception as e:
            logging.debug(f"Failed to click accept selector {selector}: {e}")
    
    # Strategy 3: Check for cookie banners in iframes
    try:
        frames = page.frames
        for frame in frames:
            if "cookie" in frame.url.lower() or "consent" in frame.url.lower():
                logging.info(f"Found cookie iframe: {frame.url}")
                
                # Try reject selectors in the iframe
                for selector in reject_selectors:
                    try:
                        is_visible = await frame.is_visible(selector, timeout=1000)
                        if is_visible:
                            await frame.click(selector)
                            await page.wait_for_timeout(1000)
                            return True
                    except:
                        continue
                
                # If reject fails, try accept selectors in the iframe
                for selector in accept_selectors:
                    try:
                        is_visible = await frame.is_visible(selector, timeout=1000)
                        if is_visible:
                            await frame.click(selector)
                            await page.wait_for_timeout(1000)
                            return True
                    except:
                        continue
    except Exception as e:
        logging.debug(f"Failed to handle cookie iframe: {e}")
    
    # Strategy 4: JavaScript approach
    try:
        # Try to find and click reject buttons via JavaScript first
        reject_js = """
        function findAndClickButton(searchTexts) {
            // Get all buttons
            const buttons = Array.from(document.querySelectorAll('button, a.button, input[type="button"], div[role="button"], [aria-role="button"]'));
            
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
        
        result = await page.evaluate(reject_js)
        if result:
            logging.info("Successfully clicked reject button via JavaScript")
            await page.wait_for_timeout(1000)
            return True
            
        # If reject fails, try accept buttons
        accept_js = """
        function findAndClickButton(searchTexts) {
            // Get all buttons
            const buttons = Array.from(document.querySelectorAll('button, a.button, input[type="button"], div[role="button"], [aria-role="button"]'));
            
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
        
        // Try different accept button texts
        return findAndClickButton(['accept all', 'accept cookies', 'i agree', 'agree', 'allow all']);
        """
        
        result = await page.evaluate(accept_js)
        if result:
            logging.info("Successfully clicked accept button via JavaScript")
            await page.wait_for_timeout(1000)
            return True
    except Exception as e:
        logging.debug(f"JavaScript cookie handling failed: {e}")
    
    # Strategy 5: Site-specific handling for common websites
    current_url = page.url.lower()
    
    # Google-specific handling
    if "google.com" in current_url:
        try:
            google_js = """
            () => {
                const buttons = Array.from(document.querySelectorAll('button'));
                const acceptButton = buttons.find(button => 
                    (button.textContent.toLowerCase().includes('accept all') || 
                    button.textContent.toLowerCase().includes('i agree') ||
                    button.textContent.toLowerCase().includes('accept')) && 
                    button.offsetParent !== null
                );
                if (acceptButton) {
                    acceptButton.click();
                    return true;
                }
                return false;
            }
            """
            result = await page.evaluate(google_js)
            if result:
                logging.info("Successfully handled Google cookie notice")
                await page.wait_for_timeout(1000)
                return True
        except Exception as e:
            logging.debug(f"Google-specific cookie handling failed: {e}")
    
    # YouTube-specific handling
    elif "youtube.com" in current_url:
        try:
            await page.click("button.yt-spec-button-shape-next--call-to-action")
            logging.info("Successfully handled YouTube cookie notice")
            await page.wait_for_timeout(1000)
            return True
        except Exception:
            logging.debug("YouTube-specific cookie handling failed")
    
    # No cookie banner found or failed to dismiss
    logging.info("No cookie banner detected or failed to dismiss")
    return False

async def handle_captcha(page):
    """
    Attempt to detect and handle CAPTCHA challenges using various strategies.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dict: {
            "detected": bool - Whether a captcha was detected,
            "solved": bool - Whether the captcha was successfully solved,
            "method": str - The method used to solve the captcha (if any)
        }
    """
    logging.info("Checking for CAPTCHA...")
    result = {
        "detected": False,
        "solved": False,
        "method": None
    }
    
    # Strategy 1: Detect common CAPTCHA indicators in the page content
    captcha_indicators = [
        "captcha",
        "i'm not a robot",
        "human verification",
        "security check",
        "verify you're human",
        "bot check",
        "prove you're not a robot"
    ]
    
    try:
        # Check page title and content for CAPTCHA indicators
        page_title = await page.title()
        page_content = await page.content()
        
        for indicator in captcha_indicators:
            if (indicator.lower() in page_title.lower() or 
                indicator.lower() in page_content.lower()):
                result["detected"] = True
                logging.info(f"CAPTCHA detected via page content: '{indicator}'")
                break
                
        # Check for reCAPTCHA and hCaptcha iframe presence
        captcha_frames = []
        frames = page.frames
        for frame in frames:
            frame_url = frame.url.lower()
            if ("recaptcha" in frame_url or 
                "hcaptcha" in frame_url or 
                "captcha" in frame_url):
                captcha_frames.append(frame)
                result["detected"] = True
                logging.info(f"CAPTCHA iframe detected: {frame_url}")
        
        # Check for specific CAPTCHA elements
        captcha_selectors = [
            "iframe[src*='recaptcha']", 
            "iframe[src*='hcaptcha']",
            ".g-recaptcha",
            ".h-captcha",
            "#captcha",
            "[data-sitekey]"
        ]
        
        for selector in captcha_selectors:
            try:
                has_captcha = await page.is_visible(selector, timeout=1000)
                if has_captcha:
                    result["detected"] = True
                    logging.info(f"CAPTCHA element detected: {selector}")
                    break
            except Exception:
                pass
        
        # If a CAPTCHA is detected, we can attempt some basic solutions
        if result["detected"]:
            # For now, notify but don't attempt to solve complex CAPTCHAs
            # This is where you could integrate with CAPTCHA solving services if needed
            logging.warning("CAPTCHA detected but automatic solving is not implemented")
            
            # Some basic attempts for checkbox-style reCAPTCHAs
            try:
                # Try clicking on reCAPTCHA checkbox if present
                recaptcha_selectors = [
                    ".recaptcha-checkbox",
                    "#recaptcha-anchor",
                    "[role='checkbox'][aria-labelledby*='recaptcha']"
                ]
                
                for selector in recaptcha_selectors:
                    try:
                        is_visible = await page.is_visible(selector, timeout=1000)
                        if is_visible:
                            # Add human-like delay before clicking
                            await asyncio.sleep(random.uniform(1.0, 2.5))
                            await page.click(selector)
                            logging.info(f"Clicked on reCAPTCHA checkbox: {selector}")
                            
                            # Wait to see if the CAPTCHA is satisfied
                            await asyncio.sleep(3)
                            
                            # Check if CAPTCHA is still present
                            still_present = False
                            for check_selector in captcha_selectors:
                                try:
                                    still_present = await page.is_visible(check_selector, timeout=1000)
                                    if still_present:
                                        break
                                except:
                                    pass
                            
                            if not still_present:
                                result["solved"] = True
                                result["method"] = "checkbox_click"
                                logging.info("CAPTCHA appears to be solved")
                                return result
                            break
                    except Exception as e:
                        logging.debug(f"Failed to click reCAPTCHA checkbox {selector}: {e}")
            except Exception as e:
                logging.debug(f"Error in CAPTCHA solving attempt: {e}")
            
            # Wait a moment to see if CAPTCHA resolves or times out
            await asyncio.sleep(2)
    except Exception as e:
        logging.error(f"Error in CAPTCHA detection: {e}")
    
    return result

async def handle_cookie_captcha(page):
    """
    Comprehensive function to handle both cookie banners and CAPTCHAs.
    
    Args:
        page: Playwright page object
        
    Returns:
        Dict: Results of both cookie and CAPTCHA handling operations
    """
    results = {
        "cookie_banner_dismissed": False,
        "captcha_detected": False,
        "captcha_solved": False
    }
    
    # First try to dismiss any cookie banners
    results["cookie_banner_dismissed"] = await dismiss_cookie_banner(page)
    
    # Then check for and try to handle CAPTCHAs
    captcha_result = await handle_captcha(page)
    results["captcha_detected"] = captcha_result["detected"]
    results["captcha_solved"] = captcha_result["solved"]
    results["captcha_method"] = captcha_result.get("method")
    
    return results

# Synchronous versions of the cookie captcha handler functions for use in sync contexts
def dismiss_cookie_banner_sync(page):
    """
    Synchronous version of dismiss_cookie_banner for use with sync Playwright
    """
    try:
        # Create a new event loop for this function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(dismiss_cookie_banner(page))
        loop.close()
        return result
    except Exception as e:
        logging.error(f"Error in sync cookie banner dismissal: {e}")
        return False

def handle_captcha_sync(page):
    """
    Synchronous version of handle_captcha for use with sync Playwright
    """
    try:
        # Create a new event loop for this function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(handle_captcha(page))
        loop.close()
        return result
    except Exception as e:
        logging.error(f"Error in sync captcha handling: {e}")
        return {"detected": False, "solved": False, "method": None}

def handle_cookie_captcha_sync(page):
    """
    Synchronous version of handle_cookie_captcha for use with sync Playwright
    """
    try:
        # Create a new event loop for this function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(handle_cookie_captcha(page))
        loop.close()
        return result
    except Exception as e:
        logging.error(f"Error in sync cookie/captcha handling: {e}")
        return {
            "cookie_banner_dismissed": False,
            "captcha_detected": False,
            "captcha_solved": False
        }
