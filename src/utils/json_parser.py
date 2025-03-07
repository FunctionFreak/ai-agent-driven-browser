
import json
import re
import logging

logger = logging.getLogger(__name__)

def extract_json(response_text: str):
    """
    Extract JSON from various response formats with multiple fallback strategies.
    
    Args:
        response_text (str): Response text that might contain JSON.
        
    Returns:
        dict: Parsed JSON object or None if parsing fails.
    """
    # Pre-processing: Remove any <think> blocks (including tags) from the response.
    cleaned_text = re.sub(r'<think>[\s\S]*?</think>', '', response_text, flags=re.IGNORECASE)
    cleaned_text = cleaned_text.strip()
    
    # Strategy 1: Try to parse directly if it's already valid JSON.
    try:
        return json.loads(cleaned_text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Try to extract JSON from code blocks.
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned_text)
    if code_block_match:
        json_str = code_block_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common issues in the code block.
            fixed_str = json_str.replace("'", '"').replace("\n", " ")
            try:
                return json.loads(fixed_str)
            except json.JSONDecodeError:
                pass
    
    # Strategy 3: Find JSON between curly braces.
    plain_json_match = re.search(r'({[\s\S]*?})', cleaned_text)
    if plain_json_match:
        json_str = plain_json_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            # Try to fix common issues.
            fixed_str = json_str.replace("'", '"').replace("\n", " ")
            try:
                return json.loads(fixed_str)
            except json.JSONDecodeError:
                pass
    
    logger.error("Could not parse JSON from response")
    return None