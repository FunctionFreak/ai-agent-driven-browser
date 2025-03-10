# File: src/dom/enhanced_tree_processor.py

from bs4 import BeautifulSoup

class EnhancedDOMTreeProcessor:
    def __init__(self, html_content):
        """
        Initialize the processor with the raw HTML content.
        """
        self.soup = BeautifulSoup(html_content, 'html.parser')
        self.dom_tree = None

    def build_dom_tree(self):
        """
        Build the enhanced DOM tree with detailed element information,
        including visibility and interactivity status.
        Returns a structured representation of the DOM.
        """
        self.dom_tree = self._process_element(self.soup)
        return self.dom_tree

    def _process_element(self, element):
        """
        Recursively process an element and its children.
        Check for visibility, interactivity, and gather relevant attributes.
        """
        # Build a node representation for the current element
        node = {
            'tag': element.name,
            'attributes': element.attrs,
            'visible': self._is_visible(element),
            'interactive': self._is_interactive(element),
            'children': []
        }
        # Process child elements recursively
        for child in element.children:
            if child.name is not None:
                node['children'].append(self._process_element(child))
        return node

    def _is_visible(self, element):
        """
        Determine if an element is visible based on its style attributes or properties.
        Checks for inline styles like 'display:none' or 'visibility:hidden'.
        """
        style = element.get('style', '')
        if 'display:none' in style or 'visibility:hidden' in style:
            return False
        return True

    def _is_interactive(self, element):
        """
        Determine if an element is interactive.
        Heuristics include checking the tag name (e.g., button, a, input)
        and the presence of event handler attributes like 'onclick'.
        """
        interactive_tags = ['button', 'a', 'input', 'select', 'textarea']
        if element.name in interactive_tags:
            return True
        if element.get('onclick'):
            return True
        return False
