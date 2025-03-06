# src/utils/json_utils.py

import json
import re
import logging

# Define the expected schema for the AI response
RESPONSE_SCHEMA = {
    "type": "object",
    "required": ["commands"],
    "properties": {
        "analysis": {"type": "string"},
        "state": {"type": "string"},
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["action"],
                "properties": {
                    "action": {"type": "string", "enum": ["navigate", "click", "input", "scroll", "wait"]},
                    "url": {"type": "string"},
                    "selector": {"type": "string"},
                    "text": {"type": "string"},
                    "submit": {"type": "boolean"},
                    "direction": {"type": "string", "enum": ["up", "down"]},
                    "amount": {"type": "number"}
                }
            }
        },
        "complete": {"type": "boolean"}
    }
}

def extract_json(response_text: str, context=None):
    """
    Extract and parse JSON from AI response text with multiple fallback strategies.
    
    Args:
        response_text: The text response from the AI that might contain JSON
        context: Optional execution context for more intelligent fallbacks
        
    Returns:
        dict: Parsed JSON object or fallback command if parsing fails
    """
    # Try multiple parsing methods
    parsed_json = (try_parse_code_block(response_text) or 
                  try_parse_direct(response_text) or
                  try_parse_with_fixes(response_text))
    
    if parsed_json:
        # Try to fix the structure and validate it
        fixed_json = fix_json_structure(parsed_json)
        return fixed_json
    
    # If all parsing fails, return a fallback command
    logging.error("All JSON parsing methods failed")
    logging.error("Trying alternative approach from self-reasoning")
    return generate_fallback_command(context)

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
    json_match = re.search(r'({[\s\S]*?})(?:\s*$|\n)', text)
    if not json_match:
        # Try a more relaxed pattern if the first one fails
        json_match = re.search(r'({[\s\S]*})', text)
        if not json_match:
            return None
        
    json_str = json_match.group(1)
    
    # Apply fixes one by one, trying to parse after each fix
    fixes = [
        # Fix 1: Replace single quotes with double quotes
        lambda s: s.replace("'", '"'),
        
        # Fix 2: Fix missing commas between objects
        lambda s: re.sub(r'}\s*{', '},{', s),
        
        # Fix 3: Remove trailing commas before closing braces
        lambda s: re.sub(r',\s*}', '}', s),
        
        # Fix 4: Fix missing quotes around property names
        lambda s: re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', s),
        
        # Fix 5: Remove control characters
        lambda s: re.sub(r'[\x00-\x1F\x7F]', '', s),
        
        # Fix 6: Fix extra commas in arrays
        lambda s: re.sub(r',\s*]', ']', s),
        
        # Fix 7: Add missing quotes around string values
        lambda s: re.sub(r': *([a-zA-Z][a-zA-Z0-9_]*)(,|})', r': "\1"\2', s),
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

def fix_json_structure(json_obj):
    """
    Fix common structural issues in JSON objects to match the expected schema
    
    Args:
        json_obj: The parsed JSON object with potential structural issues
        
    Returns:
        dict: Fixed JSON object
    """
    # Create a copy to avoid modifying the input
    fixed = {**json_obj}
    
    # Ensure commands is a list
    if "commands" not in fixed or not isinstance(fixed["commands"], list):
        fixed["commands"] = []
        
        # If we found a single command-like object, move it to the commands array
        for key in json_obj:
            if key in ["navigate", "click", "input", "scroll"]:
                fixed["commands"].append({"action": key, **json_obj[key]})
    
    # Ensure each command has an action field
    for cmd in fixed.get("commands", []):
        if not isinstance(cmd, dict):
            continue
            
        if "action" not in cmd:
            # Try to infer action from keys
            if "url" in cmd:
                cmd["action"] = "navigate"
            elif "selector" in cmd and "text" in cmd:
                cmd["action"] = "input"
            elif "selector" in cmd or "text" in cmd:
                cmd["action"] = "click"
            elif "direction" in cmd:
                cmd["action"] = "scroll"
    
    # Ensure complete field exists
    if "complete" not in fixed:
        fixed["complete"] = False
    
    return fixed

def generate_fallback_command(context=None):
    """
    Generate a fallback command when JSON parsing fails.
    Attempts to return to previous successful state if context is available.
    
    Args:
        context: Optional execution context containing history
        
    Returns:
        dict: Fallback command object
    """
    # If we have context, try to return to previous successful state
    if context and context.get("previous_successful_url"):
        return {
            "analysis": "JSON parsing failed - returning to previous successful state",
            "state": "Error recovery - rolling back",
            "commands": [
                {"action": "navigate", "url": context["previous_successful_url"]}
            ],
            "complete": False
        }
    # Otherwise, go to Google as a last resort
    return {
        "analysis": "Failed to parse valid JSON from AI response",
        "state": "Error recovery - restarting from search",
        "commands": [
            {"action": "navigate", "url": "https://www.google.com"}
        ],
        "complete": False
    }