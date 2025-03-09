# File: src/utils/output_parser.py

import json
import re
from json_repair import repair_json

def extract_json_from_llm_output(text):
    """
    Extract JSON from LLM output using multiple strategies.
    1. Direct JSON parsing.
    2. Extract JSON from markdown code blocks.
    3. Apply common fixes for malformed JSON.
    4. Use json-repair as a last resort.
    """
    # Attempt direct parsing
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON from markdown code blocks
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(code_block_pattern, text)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Apply simple fixes: replace single quotes, remove trailing commas
    text = text.replace("'", '"')
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Use json-repair as a last resort
        repaired = repair_json(text)
        return json.loads(repaired)
