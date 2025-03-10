# File: src/utils/output_parser.py

import json
import re
import logging
from json_repair import repair_json
from jsonschema import validate, ValidationError

# Set up a logger for detailed output
logger = logging.getLogger("output_parser")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

# Define the expected JSON schema for LLM responses
LLM_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "analysis": {"type": "string"},
        "state": {"type": "string"},
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"}
                    # You can add more properties as needed for each command
                },
                "required": ["action"]
            }
        },
        "complete": {"type": "boolean"}
    },
    "required": ["analysis", "state", "commands", "complete"]
}

def validate_json_structure(data):
    """
    Validate the parsed JSON object against the expected schema.
    Raises a ValidationError if the object does not conform.
    """
    try:
        validate(instance=data, schema=LLM_RESPONSE_SCHEMA)
        logger.debug("JSON schema validation passed.")
    except ValidationError as ve:
        logger.error("JSON schema validation failed: %s", ve)
        raise

def extract_json_from_llm_output(text):
    """
    Extract JSON from LLM output using multiple strategies:
    1. Direct JSON parsing.
    2. Extract JSON from markdown code blocks.
    3. Apply common fixes for malformed JSON.
    4. Use json-repair as a last resort.
    After extraction, validate the structure using a JSON schema.
    """
    logger.debug("Attempting to parse JSON directly from text.")
    # Attempt direct parsing
    try:
        data = json.loads(text)
        validate_json_structure(data)
        return data
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("Direct JSON parsing failed: %s", e)

    # Try extracting JSON from markdown code blocks
    logger.debug("Trying to extract JSON from markdown code blocks.")
    code_block_pattern = r'```(?:json)?\s*([\s\S]*?)\s*```'
    match = re.search(code_block_pattern, text)
    if match:
        try:
            data = json.loads(match.group(1))
            validate_json_structure(data)
            return data
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning("Markdown code block JSON parsing failed: %s", e)

    # Apply simple fixes: replace single quotes, remove trailing commas
    logger.debug("Applying common fixes to JSON text.")
    fixed_text = text.replace("'", '"')
    fixed_text = re.sub(r',\s*}', '}', fixed_text)
    fixed_text = re.sub(r',\s*]', ']', fixed_text)
    try:
        data = json.loads(fixed_text)
        validate_json_structure(data)
        return data
    except (json.JSONDecodeError, ValidationError) as e:
        logger.warning("Fixed JSON parsing failed: %s", e)

    # Last resort: use json-repair to attempt to fix malformed JSON
    logger.debug("Attempting to repair JSON using json-repair.")
    try:
        repaired = repair_json(fixed_text)
        data = json.loads(repaired)
        validate_json_structure(data)
        return data
    except Exception as e:
        logger.error("json-repair failed: %s", e)
        raise ValueError(f"Failed to extract valid JSON from LLM output: {e}")