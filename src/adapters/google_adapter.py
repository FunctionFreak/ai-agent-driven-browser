# src/adapters/google_adapter.py

class GoogleAdapter:
    """
    Adapter for interacting with Google's website.
    Provides common selectors and helper methods for actions like searching and handling cookie banners.
    """

    @staticmethod
    def get_search_box_selector():
        """
        Return the selector for Google's search box.
        Note: Google may use a textarea or input for search queries.
        """
        return "textarea[name='q'], input[name='q']"

    @staticmethod
    def get_search_button_selector():
        """
        Return the selector for Google's search button.
        Note: In many cases, pressing Enter on the search box is sufficient.
        """
        return "input[name='btnK']"

    @staticmethod
    def is_search_results_page(page):
        """
        Check if the current page is a Google search results page.
        """
        url = page.url.lower()
        return "google.com/search" in url

    @staticmethod
    def handle_cookie_banner(page):
        """
        Attempt to handle Google's cookie banner if present.
        Returns True if a banner is handled, otherwise False.
        """
        try:
            # Look for a button with text like "I agree" or "Accept"
            buttons = page.query_selector_all("button")
            for button in buttons:
                text = button.inner_text().lower()
                if "agree" in text or "accept" in text:
                    button.click()
                    return True
        except Exception:
            pass
        return False
