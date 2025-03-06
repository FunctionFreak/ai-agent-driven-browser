# src/adapters/generic_ecommerce_adapter.py

class GenericEcommerceAdapter:
    """
    Adapter for interacting with generic e-commerce websites.
    Provides common selectors and helper methods for actions like product search and cookie banner handling.
    """

    @staticmethod
    def get_search_box_selector():
        """
        Return a generic selector for a search box.
        This may need adjustment depending on the website's structure.
        """
        return "input[type='search'], input[name='q'], input[placeholder*='search' i]"

    @staticmethod
    def get_search_button_selector():
        """
        Return a generic selector for a search button.
        This is a best-guess selector; adjust based on your needs.
        """
        return "button[type='submit'], input[type='submit']"

    @staticmethod
    def is_product_page(page):
        """
        Check if the current page appears to be a product detail page.
        For instance, the URL might include keywords like 'product' or 'item'.
        """
        url = page.url.lower()
        return "product" in url or "item" in url

    @staticmethod
    def handle_cookie_banner(page):
        """
        Attempt to handle a generic cookie banner.
        Looks for common cookie banner buttons like 'Accept' or 'I agree'.
        Returns True if a cookie banner was handled, otherwise False.
        """
        try:
            buttons = page.query_selector_all("button")
            for button in buttons:
                text = button.inner_text().lower()
                if "accept" in text or "agree" in text:
                    button.click()
                    return True
        except Exception:
            pass
        return False
