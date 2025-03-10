# File: src/browser/navigation_manager.py

class NavigationManager:
    def __init__(self):
        """
        Initializes the navigation manager with an empty history.
        """
        self.history = []
        self.current_url = None

    def navigate_to_url(self, page, url):
        """
        Navigates to the specified URL using the given browser page.
        Updates the navigation history and sets the current URL.
        Returns the result of the page.goto() call.
        """
        self.current_url = url
        self.history.append(url)
        return page.goto(url)

    def handle_redirects(self, page):
        """
        Checks for URL redirects after a navigation action.
        If a redirect occurs, updates the current URL and history accordingly.
        Returns the final URL after redirects.
        """
        new_url = page.url  # Assuming page.url is updated after navigation
        if new_url != self.current_url:
            self.current_url = new_url
            self.history.append(new_url)
        return new_url

    def get_history(self):
        """
        Returns the list of URLs visited in the current session.
        """
        return self.history
