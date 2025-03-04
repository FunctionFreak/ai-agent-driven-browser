import time

def capture_screenshot(page, filename_prefix="screenshot"):
    """
    Captures a screenshot of the current page using Playwright's screenshot method.
    
    :param page: The Playwright page object.
    :param filename_prefix: Optional prefix for the screenshot file.
    :return: The filename of the saved screenshot.
    """
    timestamp = int(time.time())
    filename = f"{filename_prefix}_{timestamp}.png"
    page.screenshot(path=filename)
    return filename

# Example usage:
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        # Launch browser (here we use headless=False for debugging; change to True for headless mode)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://example.com")
        screenshot_path = capture_screenshot(page)
        print("Screenshot saved at:", screenshot_path)
        browser.close()
