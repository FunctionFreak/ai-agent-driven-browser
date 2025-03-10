# File: src/dom/dom_explorer.py

from bs4 import BeautifulSoup

class DOMExplorer:
    def __init__(self, html_content):
        """
        Initialize the DOMExplorer with raw HTML content.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')

    def find_by_text(self, text):
        """
        Search for elements that contain the given text (case-insensitive).
        Returns a list of matching elements.
        """
        return self.soup.find_all(lambda tag: text.lower() in tag.get_text().lower())

    def find_interactive_elements(self):
        """
        Find common interactive elements such as buttons, links, and input fields.
        Returns a list of matching elements.
        """
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea']
        return self.soup.find_all(interactive_tags)

    def find_elements_with_attribute(self, attribute, value=None):
        """
        Find elements that have a specific attribute.
        If 'value' is provided, filter elements that match the attribute value.
        """
        if value:
            return self.soup.find_all(lambda tag: tag.has_attr(attribute) and tag[attribute] == value)
        return self.soup.find_all(lambda tag: tag.has_attr(attribute))

    def find_shadow_dom(self):
        """
        Placeholder for shadow DOM handling.
        Note: Direct shadow DOM traversal is not possible with BeautifulSoup.
        This function can be extended to interface with browser-based tools if needed.
        """
        # Implementation would require JavaScript execution in a real browser environment.
        return []
