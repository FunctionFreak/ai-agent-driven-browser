# File: src/utils/debug.py

import logging

def setup_debug_logger():
    """
    Set up and return a logger configured for debugging.
    The logger outputs debug messages to the console with timestamps.
    """
    logger = logging.getLogger("debug")
    logger.setLevel(logging.DEBUG)
    
    # Avoid adding multiple handlers if already configured
    if not logger.handlers:
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger

def print_debug_tree(tree, indent=0):
    """
    Recursively print a structured representation of a tree (e.g., a DOM tree).
    
    Parameters:
      - tree (dict): A dictionary representing the tree with keys like 'tag', 'attributes', and 'children'.
      - indent (int): Current indentation level for printing.
    """
    prefix = " " * indent
    tag = tree.get("tag", "Unknown")
    attrs = tree.get("attributes", {})
    print(f"{prefix}{tag}: {attrs}")
    for child in tree.get("children", []):
        print_debug_tree(child, indent=indent+2)

# Example usage:
if __name__ == "__main__":
    logger = setup_debug_logger()
    logger.debug("Debug logger initialized.")
    
    # Example tree for visualization
    sample_tree = {
        "tag": "div",
        "attributes": {"id": "main"},
        "children": [
            {"tag": "p", "attributes": {"class": "text"}, "children": []},
            {"tag": "a", "attributes": {"href": "http://example.com"}, "children": []}
        ]
    }
    print_debug_tree(sample_tree)
