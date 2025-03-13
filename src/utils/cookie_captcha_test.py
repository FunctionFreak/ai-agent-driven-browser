# Test script for cookie_captcha_handler.py

import asyncio
import logging
from playwright.async_api import async_playwright
from src.utils.cookie_captcha_handler import dismiss_cookie_banner, handle_captcha, handle_cookie_captcha

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def test_cookie_captcha_handler():
    """
    Test the cookie and CAPTCHA handling functions on common websites.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        
        # Test sites with cookie notices
        cookie_test_sites = [
            "https://www.theguardian.com",
            "https://www.youtube.com",
            "https://www.amazon.com"
        ]
        
        # Test sites that might show CAPTCHAs (use with caution)
        captcha_test_sites = [
            "https://www.google.com/recaptcha/api2/demo"
        ]
        
        # Test cookie banner dismissal
        print("\n=== Testing Cookie Banner Dismissal ===")
        for site in cookie_test_sites:
            print(f"\nTesting cookie banner on: {site}")
            page = await context.new_page()
            try:
                await page.goto(site, timeout=30000)
                print("Page loaded, looking for cookie banners...")
                
                result = await dismiss_cookie_banner(page)
                print(f"Cookie banner dismissed: {result}")
                
                # Take a screenshot after dismissal attempt
                await page.screenshot(path=f"cookie_test_{site.split('//')[1].split('/')[0]}.png")
            except Exception as e:
                print(f"Error testing {site}: {e}")
            finally:
                await page.close()
        
        # Test CAPTCHA handling (optional)
        print("\n=== Testing CAPTCHA Detection ===")
        for site in captcha_test_sites:
            print(f"\nTesting CAPTCHA detection on: {site}")
            page = await context.new_page()
            try:
                await page.goto(site, timeout=30000)
                print("Page loaded, checking for CAPTCHAs...")
                
                result = await handle_captcha(page)
                print(f"CAPTCHA result: {result}")
                
                # Take a screenshot after handling attempt
                await page.screenshot(path=f"captcha_test_{site.split('//')[1].split('/')[0]}.png")
            except Exception as e:
                print(f"Error testing {site}: {e}")
            finally:
                await page.close()
        
        # Test the combined handler
        print("\n=== Testing Combined Handler ===")
        page = await context.new_page()
        try:
            await page.goto("https://www.theguardian.com", timeout=30000)
            print("Page loaded, testing combined handler...")
            
            result = await handle_cookie_captcha(page)
            print(f"Combined handler result: {result}")
        except Exception as e:
            print(f"Error testing combined handler: {e}")
        finally:
            await page.close()
        
        await context.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_cookie_captcha_handler())
