import re

def count_tokens(text: str) -> int:
    """
    Approximate the number of tokens in a given text.
    This naive implementation splits text by whitespace and punctuation.

    Args:
        text: The text for which to count tokens.
    
    Returns:
        int: Estimated token count.
    """
    tokens = re.findall(r'\w+', text)
    return len(tokens)

def prune_text(text: str, max_tokens: int) -> str:
    """
    Prune the text so that its token count does not exceed the specified maximum.
    
    Args:
        text: The original text.
        max_tokens: Maximum allowed tokens.
        
    Returns:
        str: Pruned text containing approximately max_tokens tokens.
    """
    tokens = re.findall(r'\w+', text)
    if len(tokens) <= max_tokens:
        return text
    
    pruned_tokens = tokens[:max_tokens]
    return ' '.join(pruned_tokens)
