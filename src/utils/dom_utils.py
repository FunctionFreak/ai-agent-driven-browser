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
    """
    Safely retrieve the outerHTML of an element specified by a selector.
    Waits for the element to appear for a given timeout, then returns its outerHTML.
    Returns None if the element is not found.
    """
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        element = await page.query_selector(selector)
        if element:
            outer_html = await element.evaluate("el => el.outerHTML")
            logger.debug("Successfully retrieved outerHTML for selector: %s", selector)
            return outer_html
        else:
            logger.warning("Element not found for selector: %s", selector)
            return None
    except Exception as e:
        logger.error("Error retrieving outerHTML for selector %s: %s", selector, e)
        return None

async def safe_click(page, selector, timeout=5000):
    """
    Safely click on an element specified by a selector.
    Waits for the element to be visible and clickable.
    Returns True if the click action is successful, otherwise False.
    """
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.click(selector)
        logger.debug("Successfully clicked on selector: %s", selector)
        return True
    except Exception as e:
        logger.error("Error clicking on selector %s: %s", selector, e)
        return False

async def safe_fill(page, selector, text, timeout=5000):
    """
    Safely fill an input field specified by a selector with given text.
    Waits for the element to be visible before filling it.
    Returns True if the fill action is successful, otherwise False.
    """
    try:
        await page.wait_for_selector(selector, timeout=timeout)
        await page.fill(selector, text)
        logger.debug("Successfully filled selector %s with text: '%s'", selector, text)
        return True
    except Exception as e:
        logger.error("Error filling selector %s with text '%s': %s", selector, text, e)
        return False
