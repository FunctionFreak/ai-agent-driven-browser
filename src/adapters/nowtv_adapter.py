# src/adapters/nowtv_adapter.py

class NowTVAdapter:
    """
    Adapter for interacting with NowTV's website.
    Provides common selectors and helper methods for actions like searching for content
    and handling cookie banners.
    """

    @staticmethod
    def get_search_box_selector():
        """
        Return the selector for NowTV's search box.
        (Adjust the selector based on the actual NowTV site structure)
        """
        return "input.search-input"  # Example selector; update if needed

    @staticmethod
    def get_search_button_selector():
        """
        Return the selector for NowTV's search button.
        (Adjust the selector based on the actual NowTV site structure)
        """
        return "button.search-button"  # Example selector; update if needed

    @staticmethod
    def is_content_page(page):
        """
        Check if the current page is a NowTV content page.
        For example, the URL might contain '/watch' or similar keywords.
        """
        url = page.url.lower()
        return "nowtv.com/watch" in url

    @staticmethod
    def handle_cookie_banner(page):
        """
        Attempt to handle NowTV's cookie banner if present.
        Returns True if a cookie banner was handled, otherwise False.
        """
        try:
            # Example: look for a cookie acceptance button
            if page.is_visible("button.cookie-accept"):
                page.click("button.cookie-accept")
                return True
        except Exception:
            pass
        return False
