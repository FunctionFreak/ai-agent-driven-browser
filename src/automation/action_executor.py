import json
import re
import logging
import time

# In src/automation/action_executor.py

def extract_json(response_text: str):
    """
    Extract the JSON object from the response text, handling different formats.
    """
    # Try to find JSON in code blocks
    code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
    if code_block_match:
        json_str = code_block_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error in code block: {e}")
            # Try to fix common issues
            fixed_str = json_str.replace("'", '"').replace("\n", " ")
            try:
                return json.loads(fixed_str)
            except:
                pass
    
    # Try to find JSON between curly braces
    plain_json_match = re.search(r'({[\s\S]*?})', response_text)
    if plain_json_match:
        json_str = plain_json_match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logging.error(f"JSON parsing error in plain text: {e}")
            # Try to fix common issues
            fixed_str = json_str.replace("'", '"').replace("\n", " ")
            try:
                return json.loads(fixed_str)
            except:
                pass
    
    logging.error("No valid JSON found in response")
    return None

def execute_actions(page, ai_response: str):
    """
    Execute actions from AI response with enhanced capabilities
    
    :param page: A Playwright page instance
    :param ai_response: The AI-generated response
    :return: List of actions performed
    """
    commands_data = extract_json(ai_response)
    if commands_data is None:
        logging.error("Failed to extract commands from AI response.")
        return []
    
    if "analysis" in commands_data:
        logging.info("AI Analysis: %s", commands_data["analysis"])
    
    actions_performed = []
    commands = commands_data.get("commands", [])
    
    for cmd in commands:
        action = cmd.get("action")
        
        if action == "navigate":
            url = cmd.get("url")
            if url:
                logging.info("Navigating to URL: %s", url)
                try:
                    page.goto(url, wait_until="domcontentloaded")
                    page.wait_for_timeout(2000)  # Wait for page to stabilize
                    actions_performed.append(f"Navigated to {url}")
                except Exception as e:
                    logging.error(f"Navigation failed: {e}")
        
        elif action == "click":
            selector = cmd.get("selector")
            text = cmd.get("text")
            
            # Special handling for Google cookie consent
            if text and "accept" in text.lower():
                try:
                    # Try direct selectors for Google consent buttons
                    consent_selectors = [
                        "button[aria-label='Accept all']",
                        "#L2AGLb",  # Google's consent button ID
                        ".tHlp8d",  # Google's consent button class
                        "form[action*='consent'] button",
                        "div[role='dialog'] button:last-child",
                        "button:has-text('Accept')",
                        "button:has-text('Accept all')"
                    ]
                    
                    for consent_selector in consent_selectors:
                        try:
                            if page.is_visible(consent_selector, timeout=1000):
                                page.click(consent_selector)
                                actions_performed.append(f"Clicked consent button with selector: {consent_selector}")
                                # Wait to ensure the action completes
                                page.wait_for_timeout(1000)
                                break
                        except:
                            continue
                    
                    # If we couldn't click using selectors, try visible elements with matching text
                    if not actions_performed:
                        try:
                            # Use evaluate to find and click the button via JavaScript
                            page.evaluate('''() => {
                                const buttons = Array.from(document.querySelectorAll('button'));
                                const acceptButton = buttons.find(button => 
                                    button.textContent.toLowerCase().includes('accept all') && 
                                    button.offsetParent !== null
                                );
                                if (acceptButton) acceptButton.click();
                            }''')
                            actions_performed.append("Attempted to click Accept button via JavaScript")
                            page.wait_for_timeout(1000)
                        except Exception as e:
                            logging.error(f"JavaScript click failed: {e}")
                            
                except Exception as e:
                    logging.error(f"Consent click action failed: {e}")
            
            # Regular clicking logic
            elif selector:
                try:
                    if page.is_visible(selector, timeout=3000):
                        page.click(selector)
                        actions_performed.append(f"Clicked element with selector: {selector}")
                    else:
                        logging.error(f"Element with selector {selector} not visible")
                except Exception as e:
                    logging.error(f"Click action failed: {e}")
            
            # Click by text as fallback
            elif text:
                try:
                    page.click(f"text='{text}'")
                    actions_performed.append(f"Clicked element with text: {text}")
                except Exception as e:
                    logging.error(f"Text click failed: {e}")
        
        elif action == "input":
            selector = cmd.get("selector")
            text = cmd.get("text", "")
            submit = cmd.get("submit", False)
            
            # Check if we're trying to use Google search
            if text and not selector:
                # If no selector is provided but we have search text, try to find the Google search box
                search_selectors = [
                    "input[name='q']", 
                    "textarea[name='q']",
                    "[aria-label='Search']",
                    "input[title='Search']"
                ]
                
                for search_selector in search_selectors:
                    try:
                        if page.is_visible(search_selector, timeout=1000):
                            page.click(search_selector)
                            page.fill(search_selector, text)
                            actions_performed.append(f"Typed '{text}' into search box")
                            
                            if submit:
                                page.press(search_selector, "Enter")
                                actions_performed.append("Pressed Enter to search")
                            
                            break
                    except:
                        continue
            
            elif selector:
                try:
                    if page.is_visible(selector, timeout=3000):
                        page.click(selector)
                        page.fill(selector, text)
                        actions_performed.append(f"Typed '{text}' into {selector}")
                        
                        if submit:
                            page.press(selector, "Enter")
                            actions_performed.append("Pressed Enter to submit")
                    else:
                        logging.error(f"Input field {selector} not visible")
                except Exception as e:
                    logging.error(f"Input action failed: {e}")
        
        elif action == "scroll":
            direction = cmd.get("direction", "down")
            amount = cmd.get("amount", 300)
            
            try:
                if direction == "down":
                    page.evaluate(f"window.scrollBy(0, {amount})")
                    actions_performed.append(f"Scrolled down {amount} pixels")
                elif direction == "up":
                    page.evaluate(f"window.scrollBy(0, -{amount})")
                    actions_performed.append(f"Scrolled up {amount} pixels")
            except Exception as e:
                logging.error(f"Scroll failed: {e}")
        
        # Wait after each action
        page.wait_for_timeout(1000)
    
    return actions_performed

# Example usage:
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    sample_ai_response = """
    {
      "analysis": "I can see a Google search page",
      "state": "Ready to search for products",
      "commands": [
        {"action": "input", "selector": "input[name='q']", "text": "iPhone 16 Pro", "submit": true}
      ],
      "complete": false
    }
    """

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://www.google.com")
        
        # Execute the commands from the sample AI response
        actions = execute_actions(page, sample_ai_response)
        print("Actions performed:", actions)
        
        # Wait to observe the results
        page.wait_for_timeout(5000)
        browser.close()