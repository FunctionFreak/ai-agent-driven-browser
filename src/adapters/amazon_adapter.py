# src/adapters/amazon_adapter.py

class AmazonAdapter:
    """
    Adapter for interacting with Amazon's website.
    Provides common selectors and helper methods for actions like product search and add-to-cart.
    """

    @staticmethod
    def get_search_box_selector():
        """
        Return the selector for Amazon's search box.
        """
        return "input#twotabsearchtextbox"

    @staticmethod
    def get_search_button_selector():
        """
        Return the selector for Amazon's search button.
        """
        return "input.nav-input[type='submit']"

    @staticmethod
    def get_product_link_selector():
        """
        Return a generic selector for product links in search results.
        """
        return "div.s-main-slot a.a-link-normal.s-no-outline"

    @staticmethod
    def get_add_to_cart_selector():
        """
        Return the selector for the Add to Cart button on a product detail page.
        """
        return "#add-to-cart-button"

    @staticmethod
    def is_product_page(page):
        """
        Check if the current page is a product detail page on Amazon.
        For example, the URL should contain '/dp/'.
        """
        url = page.url.lower()
        return "amazon.com" in url and "/dp/" in url

    @staticmethod
    def handle_cookie_banner(page):
        """
        Attempt to handle Amazon's cookie banner if present.
        Returns True if a cookie banner was handled, otherwise False.
        """
        try:
            # Example: Check if a common cookie banner element is visible and click it.
            if page.is_visible("#sp-cc"):
                page.click("#sp-cc")
                return True
        except Exception:
            pass
        return False