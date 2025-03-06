# src/adapters/adapter_selector.py
from src.adapters.adapter_selector import select_adapter

adapter = select_adapter(page)
search_box_selector = adapter.get_search_box_selector()

def select_adapter(page):
    """
    Select and return the appropriate adapter based on the current page URL.
    
    Args:
        page: The Playwright page object.
        
    Returns:
        An instance of the selected adapter.
    """
    url = page.url.lower()
    if "amazon.com" in url:
        from src.adapters.amazon_adapter import AmazonAdapter
        return AmazonAdapter()
    elif "google.com" in url:
        from src.adapters.google_adapter import GoogleAdapter
        return GoogleAdapter()
    elif "nowtv.com" in url:
        from src.adapters.nowtv_adapter import NowTVAdapter
        return NowTVAdapter()
    else:
        from src.adapters.generic_ecommerce_adapter import GenericEcommerceAdapter
        return GenericEcommerceAdapter()
