# File: src/handlers/consent_handler.py

import asyncio

async def handle_cookie_banner(page):
    """
    Handle cookie consent banners using multiple strategies:
    1. Try common selectors.
    2. Fallback to a JavaScript evaluation to find buttons.
    3. Scan iframes for consent banners.
    Returns True if a banner was handled, else False.
    """
    selectors = [
        "button#CybotCookiebotDialogBodyButtonAccept",
        "button.cookie-accept",
        "button[aria-label='Accept cookies']",
        "button:has-text('Accept all')",
        "button:has-text('I agree')",
        "#accept-all-cookies",
        ".accept-cookies-button"
    ]
    
    for selector in selectors:
        try:
            if await page.is_visible(selector, timeout=1000):
                await page.click(selector)
                await page.wait_for_timeout(1000)
                return True
        except Exception:
            continue
    
    # Fallback: Use JavaScript to find an appropriate button.
    try:
        clicked = await page.evaluate('''() => {
            const buttons = Array.from(document.querySelectorAll('button'));
            const acceptButton = buttons.find(button =>
                button.textContent.toLowerCase().includes('accept') ||
                button.textContent.toLowerCase().includes('agree')
            );
            if (acceptButton) {
                acceptButton.click();
                return true;
            }
            return false;
        }''')
        if clicked:
            await page.wait_for_timeout(1000)
            return True
    except Exception:
        pass
    
    # Try handling consent banners within iframes.
    try:
        frames = page.frames
        for frame in frames:
            if "cookie" in frame.url.lower() or "consent" in frame.url.lower():
                for selector in selectors:
                    try:
                        if await frame.is_visible(selector, timeout=1000):
                            await frame.click(selector)
                            await page.wait_for_timeout(1000)
                            return True
                    except Exception:
                        continue
    except Exception:
        pass
    
    return False

async def detect_captcha(page):
    """
    Detect CAPTCHA challenges on the page.
    Checks for common CAPTCHA-related keywords and elements.
    Returns True if a CAPTCHA is detected, else False.
    """
    captcha_indicators = [
        "recaptcha", "captcha", "security check", "verify you're human", "prove you're not a robot"
    ]
    
    content = await page.content()
    if any(indicator in content.lower() for indicator in captcha_indicators):
        return True
    
    for indicator in captcha_indicators:
        try:
            element = await page.query_selector(f"text/{indicator}")
            if element:
                return True
        except Exception:
            continue
    
    return False
