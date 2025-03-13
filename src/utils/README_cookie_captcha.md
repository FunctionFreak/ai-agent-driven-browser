# Cookie and CAPTCHA Handler

This utility provides robust handling for cookie consent banners and CAPTCHA challenges that may appear during browser automation.

## Features

- Multiple strategies for detecting and dismissing cookie consent banners
- CAPTCHA detection across various formats (reCAPTCHA, hCaptcha, etc.)
- Limited CAPTCHA solving capabilities for simple checkbox-style challenges
- Asynchronous API compatible with Playwright
- Site-specific handling for popular websites

## Usage

### Basic Usage

```python
import asyncio
from playwright.async_api import async_playwright
from src.utils.cookie_captcha_handler import handle_cookie_captcha

async def navigate_with_cookie_captcha_handling():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate to a site
        await page.goto("https://www.example.com")
        
        # Handle any cookie banners or CAPTCHAs
        result = await handle_cookie_captcha(page)
        print(f"Cookie banner dismissed: {result['cookie_banner_dismissed']}")
        print(f"CAPTCHA detected: {result['captcha_detected']}")
        print(f"CAPTCHA solved: {result['captcha_solved']}")
        
        # Continue with your automation...
        
        await browser.close()

asyncio.run(navigate_with_cookie_captcha_handling())
```

### Individual Functions

You can also use the individual functions for more specific control:

```python
# Just handle cookie banners
dismissed = await dismiss_cookie_banner(page)

# Just detect and try to solve CAPTCHAs
captcha_result = await handle_captcha(page)
```

## How It Works

### Cookie Banner Dismissal

Uses multiple strategies in this order:
1. Tries common selectors for "reject" buttons (privacy-friendly approach)
2. Falls back to "accept" buttons if reject isn't available
3. Looks for cookie banners in iframes
4. Uses JavaScript to find and click buttons based on text content
5. Applies site-specific handling for popular websites

### CAPTCHA Detection

Detects CAPTCHAs using:
1. Keywords in page title and content
2. Presence of CAPTCHA-related iframes
3. Common CAPTCHA DOM elements

### CAPTCHA Solving

Currently handles:
- Basic checkbox-style reCAPTCHAs

For more complex CAPTCHAs, integration with external solving services would be required.

## Testing

Run the test script to see the handlers in action:

```
python -m src.utils.cookie_captcha_test
```

## Limitations

- Cannot solve complex image/audio CAPTCHAs without external services
- Some cookie banners with unusual designs may be missed
- Heavily obfuscated cookie consent mechanisms might not be detected
