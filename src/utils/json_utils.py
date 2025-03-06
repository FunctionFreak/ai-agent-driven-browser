# src/utils/json_utils.py

import json
import re
import logging

def extract_json(response_text: str):
    """
    Extract and parse JSON from AI response text with multiple fallback strategies.
    
    Args:
        response_text: The text response from the AI that might contain JSON
        
    Returns:
        dict: Parsed JSON object or fallback command if parsing fails
    """
    # Try multiple parsing methods
    parsed_json = (try_parse_code_block(response_text) or 
                  try_parse_direct(response_text) or
                  try_parse_with_fixes(response_text))
    
    if parsed_json:
        return parsed_json
    
    # If all parsing fails, return a fallback command
    logging.error("All JSON parsing methods failed")
    return generate_fallback_command()

def try_parse_code_block(text):
    """Try to extract and parse JSON from a code block"""
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
    if code_block_match:
        json_str = code_block_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            return None
    return None

def try_parse_direct(text):
    """Try to parse the text directly as JSON"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def try_parse_with_fixes(text):
    """Try to fix common JSON syntax errors before parsing"""
    # Find anything that looks like a JSON object
    json_match = re.search(r'({[\s\S]*?})', text)
    if not json_match:
        return None
        
    json_str = json_match.group(1)
    
    # Apply fixes one by one, trying to parse after each fix
    fixes = [
        # Fix 1: Replace single quotes with double quotes
        lambda s: s.replace("'", '"'),
        
        # Fix 2: Add missing commas between objects
        lambda s: re.sub(r'}\s*{', '},{', s),
        
        # Fix 3: Remove trailing commas before closing braces
        lambda s: re.sub(r',\s*}', '}', s),
        
        # Fix 4: Fix missing quotes around property names
        lambda s: re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', s),
        
        # Fix 5: Remove control characters
        lambda s: re.sub(r'[\x00-\x1F\x7F]', '', s)
    ]
    
    # Try each fix separately
    for fix_func in fixes:
        try:
            fixed = fix_func(json_str)
            return json.loads(fixed)
        except json.JSONDecodeError:
            continue
    
    # Try applying all fixes together
    try:
        for fix_func in fixes:
            json_str = fix_func(json_str)
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None

def generate_fallback_command():
    """Generate a fallback command when JSON parsing fails"""
    return {
        "commands": [
            {"action": "navigate", "url": "https://www.google.com"}
        ]
    }