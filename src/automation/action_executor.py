import json
import re
import logging

def extract_json(response_text: str):
    """
    Extract the JSON object from the response text.
    This function finds the first occurrence of a JSON object
    (i.e. starting with '{' and ending with '}') and returns it as a dict.
    """
    # Find the JSON portion using a regex
    match = re.search(r'({.*})', response_text, re.DOTALL)
    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except Exception as e:
            logging.error("JSON parsing error: %s", e)
            return None
    else:
        logging.error("No JSON found in response.")
        return None

def execute_actions(page, ai_response: str):
    """
    Parse the AI response (expected in JSON format, possibly with extra text) and execute the corresponding actions
    on the given Playwright page.
    
    The AI response should include a 'commands' array, e.g.:
    {
      "commands": [
         { "action": "navigate", "url": "https://www.google.com" }
      ]
    }
    
    :param page: A Playwright page instance.
    :param ai_response: The AI-generated response as a string.
    """
    # Extract the JSON from the response text
    commands_data = extract_json(ai_response)
    if commands_data is None:
        logging.error("Failed to extract commands from AI response.")
        return

    commands = commands_data.get("commands", [])
    for cmd in commands:
        action = cmd.get("action")
        if action == "click":
            selector = cmd.get("selector")
            if selector:
                logging.info("Clicking on element with selector: %s", selector)
                page.click(selector)
            else:
                logging.error("No selector provided for click action.")
        elif action == "navigate":
            url = cmd.get("url")
            if url:
                logging.info("Navigating to URL: %s", url)
                page.goto(url)
            else:
                logging.error("No URL provided for navigate action.")
        elif action == "input":
            selector = cmd.get("selector")
            text = cmd.get("text", "")
            if selector:
                logging.info("Typing text '%s' into element with selector: %s", text, selector)
                page.fill(selector, text)
            else:
                logging.error("No selector provided for input action.")
        else:
            logging.warning("Unknown action: %s", action)

# Example usage:
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    sample_ai_response = """
    <think>
    ... internal reasoning text ...
    </think>
    {"commands": [{"action": "navigate", "url": "https://www.google.com"}]}
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Ensure headless is False so you can see the browser
        context = browser.new_context()
        page = context.new_page()
        # Execute the commands from the sample AI response.
        execute_actions(page, sample_ai_response)
        # Wait to observe the actions
        page.wait_for_timeout(5000)
        browser.close()
