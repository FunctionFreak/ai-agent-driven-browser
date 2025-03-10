import time
import json
import logging
import random
from playwright.sync_api import Page
from src.capture.screen_capture import capture_screenshot
from src.vision.yolov8_detector import YOLOv8Detector
from src.vision.ocr_processor import OCRProcessor
from src.metadata.metadata_generator import MetadataGenerator
from src.reasoning.deepseek_reasoner import DeepSeekReasoner
from src.automation.action_executor import execute_actions, simulate_human_mouse_movement
from src.utils.json_utils import extract_json
from src.automation.playwright_controller import apply_stealth_mode
from src.handlers.search_handler import SearchHandler
from src.utils.dom_utils import DOMExplorer
from src.tasks.task_manager import Task, Subtask
from src.automation.playwright_controller import execute_dom_action
from src.prompts.system_prompt import get_system_prompt
from src.utils.command_preprocessor import preprocess_command
from src.dom.dom_explorer import DOMExplorer

def create_task_from_goal(goal: str) -> Task:
    """
    Create a Task object from the user's high-level goal.
    This is a simplistic example; you can expand it with more logic.
    """
    task = Task(name=goal)

    # Example logic: if goal mentions 'iPhone'
    if "iphone" in goal.lower():
        task.add_subtask(Subtask("Define desired iPhone model/specs"))
        task.add_subtask(Subtask("Identify authorized sellers (Apple, Amazon, etc.)"))
        task.add_subtask(Subtask("Compare prices, availability, and policies"))
        task.add_subtask(Subtask("Select optimal seller and navigate to site"))
        task.add_subtask(Subtask("Locate iPhone and validate product details"))
        task.add_subtask(Subtask("Add iPhone to cart without checkout"))
    # Example logic: if goal mentions 'pizza recipe'
    elif "pizza" in goal.lower() and "recipe" in goal.lower():
        task.add_subtask(Subtask("Identify reliable recipe sources (Allrecipes, Food Network, etc.)"))
        task.add_subtask(Subtask("Navigate to chosen site"))
        task.add_subtask(Subtask("Locate desired pizza recipe"))
        task.add_subtask(Subtask("Review ingredients and instructions"))
    else:
        # Generic fallback if goal isn't recognized
        task.add_subtask(Subtask("Analyze the goal and decide on a search strategy"))
        task.add_subtask(Subtask("Navigate to a search engine (Google)"))
        task.add_subtask(Subtask("Perform a relevant search for the goal"))

    return task

def is_captcha_page(ocr_results):
    """Check if current page is showing a CAPTCHA or security challenge"""
    captcha_texts = ["robot", "captcha", "unusual traffic", "verify", "security check"]
    page_text = " ".join([r['text'].lower() for r in ocr_results])
    return any(captcha_text in page_text for captcha_text in captcha_texts)

def attempt_direct_recipe_search(page, context):
    """Try to bypass search engines by going to recipe sites directly"""
    # List of popular recipe sites with search built-in
    sites = [
        {"url": "https://www.allrecipes.com/search?q=pizza", "selector": ".card__title"},
        {"url": "https://www.epicurious.com/search/pizza", "selector": ".recipe-card"},
        {"url": "https://www.foodnetwork.com/search/pizza-", "selector": ".o-ResultCard"}
    ]
    # Use the site based on attempt count
    site_index = min(context.get("captcha_count", 0), len(sites) - 1)
    site = sites[site_index]
    
    print(f"Trying direct recipe site: {site['url']}")
    page.goto(site["url"])
    
    # Wait for results to load
    try:
        page.wait_for_selector(site["selector"], timeout=5000)
        # Click the first recipe result
        page.click(f"{site['selector']}:first-child")
        context["actions_taken"].append(f"Found recipe on {site['url'].split('/')[2]}")
        return True
    except:
        return False

def feedback_loop(page, initial_goal: str, max_iterations=20, interval: int = 3):
    """
    Enhanced feedback loop with progress tracking and human-like behavior
    """
    # Initialize handlers
    search_handler = SearchHandler()
    dom_explorer = DOMExplorer()
    # Apply stealth mode to the page
    apply_stealth_mode(page)
    
    # Try to make the browser fullscreen
    try:
        page.evaluate("() => { document.documentElement.requestFullscreen(); }")
    except:
        pass
        
    # Initialize modules
    detector = YOLOv8Detector(model_variant='yolov8l.pt')
    ocr_processor = OCRProcessor()
    metadata_gen = MetadataGenerator()
    reasoner = DeepSeekReasoner()
    
    # Initialize context
    context = {
        "original_goal": initial_goal,
        "current_state": "Starting browser automation",
        "iteration": 0,
        "actions_taken": [],
        "previous_actions": [],  # To detect loops
        "stuck_counter": 0,      # To track if we're stuck
        "captcha_count": 0       # To track CAPTCHA encounters
    }
    
    task = create_task_from_goal(initial_goal)
    context["task"] = task

    # Preprocess the high-level user command to generate a clear starting JSON command.
    preprocessed_command = preprocess_command(initial_goal)
    logging.info("Preprocessed command: %s", preprocessed_command)
    
    for iteration in range(1, max_iterations + 1):
        context["iteration"] = iteration
        print(f"\n--- Feedback Loop Iteration {iteration}/{max_iterations} ---")
        print(f"Current goal: {initial_goal}")
        print(f"Current state: {context['current_state']}")
        
        # Add human-like behavior: Random pause between iterations
        if iteration > 1:
            human_pause = random.uniform(1.0, 3.0)
            print(f"Taking a human-like pause of {human_pause:.1f} seconds...")
            time.sleep(human_pause)
        
        # Add random mouse movements before capturing screenshot
        simulate_human_mouse_movement(page)
        
        # Capture and process screenshot
        screenshot_path = capture_screenshot(page)
        print(f"Screenshot captured: {screenshot_path}")
        
        # Process the screenshot with vision models
        object_detections = detector.detect(screenshot_path)
        ocr_results = ocr_processor.process_image(screenshot_path)
        
        # Check for visible OCR text
        if ocr_results:
            texts = [r['text'] for r in ocr_results[:5]]
            print(f"Detected text on page: {', '.join(texts)}...")
        else:
            print("No text detected on page")
            # Analyze page with DOM explorer
            print("Analyzing page DOM structure...")
            interactive_elements = DOMExplorer.find_interactive_elements(page)
            print(f"Found {interactive_elements.get('buttons', 0)} buttons, {interactive_elements.get('links', 0)} links, {interactive_elements.get('inputs', 0)} input fields")
        
        # ---- Subtask Auto-Check Start ----
        current_subtask = context["task"].get_current_subtask()
        if current_subtask:
            if current_subtask.check_if_complete(page, context):
                current_subtask.mark_complete()
                print(f"Subtask '{current_subtask.description}' is already complete (auto-detected).")
                new_subtask = context["task"].get_current_subtask()
                if new_subtask:
                    print(f"Proceeding to next subtask: {new_subtask.description}")
                else:
                    print("All subtasks are complete. Exiting loop.")
                    break
        # ---- Subtask Auto-Check End ----

        # Check if there's a cookie consent banner using DOM
        cookie_banner_handled = DOMExplorer.find_cookie_consent(page)
        if cookie_banner_handled:
            context["actions_taken"].append("Handled cookie consent banner using DOM exploration")
            print("Cookie banner handled successfully via DOM")
            # Optionally, take a new screenshot and continue to next iteration if needed
            screenshot_path = capture_screenshot(page)
            continue
        
        # Always analyze the page DOM for context
        interactive_elements = DOMExplorer.find_interactive_elements(page)
        print(f"DOM context: {interactive_elements}")

        # Generate metadata
        metadata = metadata_gen.generate_metadata(object_detections, ocr_results)
        metadata_file = f"metadata_{iteration}.json"
        metadata_gen.save_metadata(metadata, file_path=metadata_file)

        # Check for cookie banners using OCR results
        if any(keyword in " ".join([r['text'].lower() for r in ocr_results]) for keyword in ["cookie", "consent", "accept", "allow"]):
            print("Cookie banner detected via OCR, attempting to handle...")
            from src.automation.action_executor import handle_cookie_banner
            cookie_handled = handle_cookie_banner(page)
            if cookie_handled:
                context["actions_taken"].append("Handled cookie consent banner")
                print("Cookie banner handled successfully")
                # Take a new screenshot to confirm
                screenshot_path = capture_screenshot(page)
                continue  # Skip to next iteration
        
        # Current URL info
        current_url = page.url
        # Retrieve current subtask from the task object
        current_subtask = context["task"].get_current_subtask()
        subtask_info = current_subtask.description if current_subtask else "No subtask defined"
        context_message = f"GOAL: {initial_goal}\nCURRENT SUBTASK: {subtask_info}\nCURRENT URL: {current_url}\nCURRENT STATE: {context['current_state']}\nITERATION: {iteration}/{max_iterations}"
        
        # Check for CAPTCHA
        if is_captcha_page(ocr_results):
            context["captcha_count"] += 1
            print(f"CAPTCHA detected! Count: {context['captcha_count']}")
            if context["captcha_count"] >= 2:
                print("Multiple CAPTCHAs encountered. Trying direct recipe site...")
                # Use specialized strategy based on the goal
                if "recipe" in initial_goal.lower() or "food" in initial_goal.lower():
                    # List of good recipe sites to try directly
                    recipe_sites = [
                        "https://www.allrecipes.com/recipes/250/main-dish/pizza/",
                        "https://www.simplyrecipes.com/recipes/homemade_pizza/",
                        "https://www.bbcgoodfood.com/recipes/collection/pizza-recipes"
                    ]
                    site_index = min(context["captcha_count"] - 2, len(recipe_sites) - 1)
                    recipe_site = recipe_sites[site_index]
                    print(f"Navigating directly to: {recipe_site}")
                    page.goto(recipe_site)
                    context["actions_taken"].append(f"Navigated to {recipe_site} after CAPTCHA detection")
                else:
                    print("Trying alternative approach due to CAPTCHA...")
                    page.goto("about:blank")
                    context["actions_taken"].append("Reset page due to CAPTCHA")
                wait_time = random.uniform(1.0, 3.0)
                print(f"Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                continue
        
        # If we're on Google and see a cookie notice, handle it directly
        if "google.com" in current_url and any("cookie" in r['text'].lower() for r in ocr_results):
            try:
                print("Detected Google cookie notice, attempting direct handling...")
                clicked = page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const acceptButton = buttons.find(button => 
                        (button.textContent.toLowerCase().includes('accept all') || 
                        button.textContent.toLowerCase().includes('i agree') ||
                        button.textContent.toLowerCase().includes('accept')) && 
                        button.offsetParent !== null
                    );
                    if (acceptButton) {
                        acceptButton.click();
                        return true;
                    }
                    return false;
                }''')
                if clicked:
                    print("Successfully clicked accept button via JavaScript")
                    context["actions_taken"].append("Accepted cookies on Google")
                    page.wait_for_timeout(2000)
                    time.sleep(random.uniform(1.0, 3.0))
                    continue
            except:
                pass
        
        # If we're on Google and already passed cookie notice, try direct search
        if "google.com" in current_url and not any("cookie" in r['text'].lower() for r in ocr_results):
            try:
                search_selectors = [
                    "textarea[name='q']",
                    "input[name='q']",
                    "[aria-label='Search']",
                    ".gLFyf"
                ]
                for search_selector in search_selectors:
                    try:
                        if page.is_visible(search_selector, timeout=1000):
                            if iteration <= 2 and not any(a.startswith("Typed") for a in context["actions_taken"]):
                                if "recipe" in initial_goal.lower():
                                    search_query = "best pizza recipe"
                                elif "iphone" in initial_goal.lower():
                                    search_query = "iphone 16 pro buy"
                                else:
                                    search_query = initial_goal
                                element_position = page.evaluate(f"""() => {{
                                    const element = document.querySelector('{search_selector}');
                                    if (!element) return null;
                                    const rect = element.getBoundingClientRect();
                                    return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                                }}""")
                                if element_position:
                                    from src.automation.action_executor import move_mouse_naturally
                                    move_mouse_naturally(page, element_position['x'], element_position['y'])
                                page.click(search_selector)
                                page.fill(search_selector, "")
                                for char in search_query:
                                    page.type(search_selector, char, delay=random.randint(50, 200))
                                    time.sleep(random.uniform(0.01, 0.05))
                                time.sleep(random.uniform(0.5, 1.5))
                                page.press(search_selector, "Enter")
                                print(f"Performed direct search with selector: {search_selector}")
                                page.wait_for_timeout(3000)
                                context["actions_taken"].append(f"Typed '{search_query}' into search box")
                                context["actions_taken"].append("Pressed Enter to search")
                                break
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"Direct search attempt failed: {e}")
        
        # Get AI decision with context
        try:
            ai_response = reasoner.get_response(context_message, metadata, dom_data=interactive_elements)
            print("AI Response:", ai_response)
        except Exception as e:
            print(f"AI API error: {e}")
            if "google.com" in current_url:
                print("Using fallback: Direct search for goal")
                search_term = "best pizza recipe" if "recipe" in initial_goal.lower() else initial_goal
                ai_response = f"""
                {{
                  "analysis": "On Google homepage, need to search.",
                  "state": "Ready to search",
                  "commands": [
                    {{"action": "input", "selector": "textarea[name='q']", "text": "{search_term}", "submit": true}}
                  ],
                  "complete": false
                }}
                """
            elif "allrecipes.com" in current_url or "recipe" in current_url:
                ai_response = """
                {
                  "analysis": "Found recipe page successfully.",
                  "state": "Recipe page loaded",
                  "commands": [
                    {"action": "scroll", "direction": "down", "amount": 300}
                  ],
                  "complete": true
                }
                """
            else:
                ai_response = """
                {
                  "analysis": "Fallback after API error.",
                  "state": "Error recovery",
                  "commands": [
                    {"action": "navigate", "url": "https://www.google.com"}
                  ],
                  "complete": false
                }
                """
        
        # Execute actions                      
        try:
            response_json = extract_json(ai_response)
            if not response_json:
                logging.error("Failed to extract valid JSON from AI response.")
                response_json = {
                    "analysis": "Failed to parse valid JSON from AI response",
                    "state": "Error recovery - restarting from search",
                    "commands": [
                        {"action": "navigate", "url": "https://www.google.com"}
                    ],
                    "complete": False
                }
            if "commands" in response_json:
                commands = response_json.get("commands", [])
                for cmd in commands:
                    if cmd.get("action") == "input" and cmd.get("text"):
                        if "search" in cmd.get("text", "").lower() or "q" in cmd.get("selector", "").lower():
                            print(f"Detected search command, using flexible search handler")
                            search_term = cmd.get("text", "")
                            search_success = search_handler.perform_search(page, search_term, ocr_results)
                            if search_success:
                                context["actions_taken"].append(f"Searched for '{search_term}' using flexible search handler")
                                print(f"Successfully searched for: {search_term}")
                                continue
                dom_executed = False
                for cmd in commands:
                    if cmd.get("action") in ["click", "input", "navigate"]:
                        success = execute_dom_action(page, cmd)
                        if success:
                            logging.info("Action executed successfully via DOM-based method for command: %s", cmd)
                            dom_executed = True
                        else:
                            logging.error("DOM-based action execution failed for command: %s", cmd)
                if not dom_executed:
                    logging.warning("No DOM-based actions succeeded. Falling back to standard action execution.")
                try:
                    actions = execute_actions(page, ai_response)
                except Exception as fallback_error:
                    logging.error("Fallback action execution failed: %s", fallback_error)
                    try:
                        self_prompt = f"""
                        I'm stuck while executing actions for the goal: {initial_goal}
                        Current URL: {page.url}
                        Please suggest an alternative approach.
                        """
                        alternative_response = reasoner.get_response(self_prompt, metadata, dom_data=interactive_elements)
                        logging.info("Self-reasoning fallback response: %s", alternative_response)
                        actions = execute_actions(page, alternative_response)
                    except Exception as e:
                        logging.critical("Self-reasoning fallback also failed: %s", e)
                        actions = []
                actions = execute_actions(page, ai_response)
            if actions == context["previous_actions"]:
                context["stuck_counter"] += 1
            else:
                context["stuck_counter"] = 0
            if context["stuck_counter"] >= 3:
                print("Detected loop, trying alternative approach...")
                self_prompt = f"""
                I'm stuck in a loop trying to accomplish: {initial_goal}
                Current page: {current_url}
                Current state: {context['current_state']}
                Last actions taken: {', '.join(context['actions_taken'][-3:])}
                OCR detected text: {', '.join([r['text'] for r in ocr_results[:10]])}
                What's probably going wrong and what alternative approach should I try?
                """
                try:
                    alternative_response = reasoner.get_response(self_prompt, metadata)
                    print("AI Response:", alternative_response)
                    alternative_json = extract_json(alternative_response)
                    if alternative_json and "commands" in alternative_json:
                        print("Trying alternative approach from self-reasoning")
                        alt_actions = execute_actions(page, alternative_response)
                        if alt_actions:
                            context["actions_taken"].extend(alt_actions)
                            context["stuck_counter"] = 0
                            continue
                except Exception as e:
                    print(f"Self-reasoning attempt failed: {e}")
                if "google.com" in current_url:
                    try:
                        search_selectors = [
                            "textarea[name='q']",
                            "input[name='q']",
                            "[aria-label='Search']",
                            ".gLFyf"
                        ]
                        for search_selector in search_selectors:
                            try:
                                if page.is_visible(search_selector, timeout=1000):
                                    if "recipe" in initial_goal.lower():
                                        search_query = "best pizza recipe"
                                    else:
                                        search_query = initial_goal
                                    page.click(search_selector)
                                    page.fill(search_selector, "")
                                    for char in search_query:
                                        page.type(search_selector, char, delay=random.randint(50, 150))
                                        time.sleep(random.uniform(0.01, 0.05))
                                    time.sleep(random.uniform(0.5, 1.0))
                                    page.press(search_selector, "Enter")
                                    print(f"Attempted direct search for '{search_query}' with selector {search_selector}")
                                    context["stuck_counter"] = 0
                                    page.wait_for_timeout(3000)
                                    break
                            except Exception as e:
                                continue
                        if context["stuck_counter"] > 0:
                            if "recipe" in initial_goal.lower():
                                print("Bypassing Google search and going directly to recipe site")
                                direct_success = attempt_direct_recipe_search(page, context)
                                if direct_success:
                                    context["stuck_counter"] = 0
                            else:
                                page.reload()
                                print("Reloaded the page to try again")
                                context["stuck_counter"] = 0
                    except Exception as e:
                        print(f"Alternative approach failed: {e}")
                        page.reload()
                        print("Reloaded the page to try again")
                        context["stuck_counter"] = 0
                if context["captcha_count"] > 3:
                    print("Stuck on CAPTCHA too many times, attempting direct navigation to content")
                    if "recipe" in initial_goal.lower():
                        page.goto("https://www.allrecipes.com/recipes/250/main-dish/pizza/")
                        context["actions_taken"].append("Navigated directly to recipe site due to persistent CAPTCHA")
                        context["stuck_counter"] = 0
                    elif "iphone" in initial_goal.lower():
                        page.goto("https://www.apple.com/iphone/")
                        context["actions_taken"].append("Navigated directly to Apple iPhone page due to persistent CAPTCHA")
                        context["stuck_counter"] = 0
            context["previous_actions"] = actions
            if actions:
                context["actions_taken"].extend(actions)
                print(f"Actions performed: {', '.join(actions)}")
            current_subtask = context["task"].get_current_subtask()
            if current_subtask:
                if response_json and "state" in response_json and "done" in response_json["state"].lower():
                    context["task"].mark_subtask_complete()
                    print(f"Marked subtask '{current_subtask.description}' as complete.")
                    new_subtask = context["task"].get_current_subtask()
                    if new_subtask:
                        print(f"Next subtask: {new_subtask.description}")
                    else:
                        print("No further subtasks left.")
            if context["task"].is_complete():
                print("\n=== ALL SUBTASKS COMPLETED! ===")
                break
            response_json = extract_json(ai_response)
            if response_json and "complete" in response_json and response_json["complete"] == True:
                print("\n=== TASK COMPLETED! ===")
                print(f"Final state: {response_json.get('state', 'Task successful')}")
                print(f"Analysis: {response_json.get('analysis', 'Goal accomplished')}")
                break
            if response_json and "state" in response_json:
                context["current_state"] = response_json["state"]
        except Exception as e:
            print(f"Error processing AI response: {e}")
        actual_interval = random.uniform(max(1, interval-1), interval+2)
        print(f"Waiting {actual_interval:.1f} seconds before next iteration...")
        time.sleep(actual_interval)
    print("\n=== Task Summary ===")
    print(f"Original goal: {initial_goal}")
    print(f"Final state: {context['current_state']}")
    print("Actions taken:")
    for i, action in enumerate(context["actions_taken"]):
        print(f"  {i+1}. {action}")
    return context

def extract_search_term_from_goal(goal):
    """Extract likely search term from user goal"""
    import re
    product_match = re.search(r'(?:find|search for|looking for|buy|purchase|get)?\s*([a-zA-Z0-9]+(?: [a-zA-Z0-9]+){1,5})\b', goal)
    if product_match:
        return product_match.group(1)
    if "recipe" in goal.lower():
        recipe_match = re.search(r'([a-zA-Z]+(?: [a-zA-Z]+){0,3})\s+recipe', goal)
        if recipe_match:
            return f"{recipe_match.group(1)} recipe"
    return goal

# Example usage if run directly
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    from dotenv import load_dotenv
    import os
    load_dotenv()
    user_goal = input("What would you like the browser agent to do? ")
    with sync_playwright() as p:
        from src.automation.playwright_controller import launch_browser_with_profile
        browser_context, temp_profile_path = launch_browser_with_profile()
        page = browser_context.new_page()
        try:
            feedback_loop(page, user_goal)
        except KeyboardInterrupt:
            print("Process terminated by user.")
        finally:
            input("Press Enter to close the browser...")
            browser_context.close()
            if temp_profile_path:
                import shutil
                shutil.rmtree(temp_profile_path, ignore_errors=True)
