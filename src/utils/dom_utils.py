# File: src/utils/dom_utils.py

import asyncio
import logging

logger = logging.getLogger("dom_utils")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

async def safe_get_outer_html(page, selector, timeout=5000):
    """Safely get outer HTML of an element with timeout"""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        html = await page.evaluate(f'document.querySelector("{selector}").outerHTML')
        return html
    except Exception as e:
        logger.error(f"Error getting outer HTML for '{selector}': {e}")
        return None

async def safe_click(page, selector, timeout=5000):
    """Safely click an element with timeout"""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.click(selector)
        return True
    except Exception as e:
        logger.error(f"Error clicking '{selector}': {e}")
        return False

async def safe_fill(page, selector, text, timeout=5000):
    """Safely fill an input element with timeout"""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.fill(selector, text)
        return True
    except Exception as e:
        logger.error(f"Error filling '{selector}': {e}")
        return False

async def get_element_dimensions(page, selector, timeout=5000):
    """Get dimensions of an element"""
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        dimensions = await page.evaluate(f'''() => {{
            const element = document.querySelector("{selector}");
            if (!element) return null;
            const rect = element.getBoundingClientRect();
            return {{
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                right: rect.right,
                bottom: rect.bottom,
                left: rect.left
            }};
        }}''')
        return dimensions
    except Exception as e:
        logger.error(f"Error getting dimensions for '{selector}': {e}")
        return None

def has_element(page, selector, timeout=1000):
    """Check if element exists on the page (synchronous version)"""
    try:
        page.wait_for_selector(selector, timeout=timeout)
        return True
    except:
        return False

# Function to extract DOM information for AI context
async def extract_dom_context(page):
    """Extract key information about the DOM for AI context"""
    try:
        dom_context = await page.evaluate("""() => {
            const result = {
                title: document.title,
                url: window.location.href,
                elementCounts: {
                    buttons: document.querySelectorAll('button').length,
                    links: document.querySelectorAll('a').length,
                    inputs: document.querySelectorAll('input, textarea').length,
                    images: document.querySelectorAll('img').length
                },
                visibleText: Array.from(document.querySelectorAll('h1, h2, h3, p'))
                    .filter(el => el.offsetParent !== null)
                    .map(el => el.textContent.trim())
                    .filter(text => text.length > 0)
                    .slice(0, 10)
            };
            
            // Get form information
            const forms = document.querySelectorAll('form');
            result.forms = Array.from(forms).map(form => {
                const inputs = form.querySelectorAll('input');
                return {
                    id: form.id,
                    action: form.action,
                    method: form.method,
                    inputCount: inputs.length,
                    inputTypes: Array.from(inputs).map(input => input.type)
                };
            }).slice(0, 3);
            
            return result;
        }""")
        return dom_context
    except Exception as e:
        logger.error(f"Error extracting DOM context: {e}")
        return {
            "error": str(e),
            "title": "Error extracting DOM context",
            "elementCounts": {}
        }
