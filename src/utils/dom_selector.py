import logging

def find_dom_element(page, selector: str = None, text: str = None):
    """
    Enhanced DOM element finder using multiple strategies.

    Args:
        page: Playwright page object.
        selector: CSS selector string.
        text: Text content to search for.

    Returns:
        The found element, or None if not found.
    """
    element = None

    # Try using the CSS selector first
    if selector:
        try:
            element = page.query_selector(selector)
            if element:
                logging.info(f"Element found using selector: {selector}")
                return element
        except Exception as e:
            logging.warning(f"Error finding element with selector '{selector}': {e}")

    # Fallback: search using text content
    if text:
        try:
            element = page.query_selector(f"text={text}")
            if element:
                logging.info(f"Element found using text search: {text}")
                return element
        except Exception as e:
            logging.warning(f"Error finding element with text '{text}': {e}")

    logging.error("Element not found using provided selector or text.")
    return None
