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
from src.automation.action_executor import extract_json
from src.automation.playwright_controller import apply_stealth_mode

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
        context_message = f"GOAL: {initial_goal}\nCURRENT URL: {current_url}\nCURRENT STATE: {context['current_state']}\nITERATION: {iteration}/{max_iterations}"
        
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
                    # For non-recipe goals, try a different approach
                    print("Trying alternative approach due to CAPTCHA...")
                    # Reset the page
                    page.goto("about:blank")
                    context["actions_taken"].append("Reset page due to CAPTCHA")
                
                # Add longer delay to appear more human-like
                wait_time = random.uniform(3.0, 7.0)
                print(f"Waiting {wait_time:.1f} seconds...")
                time.sleep(wait_time)
                
                # Skip to next iteration
                continue
        
        # If we're on Google and see a cookie notice, handle it directly
        if "google.com" in current_url and any("cookie" in r['text'].lower() for r in ocr_results):
            try:
                # Try direct JavaScript approach to accept cookies
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
                    page.wait_for_timeout(2000)  # Wait for the banner to disappear
                    
                    # Add a human-like pause
                    time.sleep(random.uniform(1.0, 3.0))
                    
                    # Skip to next iteration to check if it worked
                    continue
            except:
                pass
        
        # If we're on Google and already passed cookie notice, try direct search
        if "google.com" in current_url and not any("cookie" in r['text'].lower() for r in ocr_results):
            try:
                # Try multiple selectors for Google's search box
                search_selectors = [
                    "textarea[name='q']",  # Google now often uses textarea instead of input
                    "input[name='q']",
                    "[aria-label='Search']",
                    ".gLFyf"  # Google's search class
                ]
                
                for search_selector in search_selectors:
                    try:
                        if page.is_visible(search_selector, timeout=1000):
                            # If we're here for the first time, search for the goal
                            if iteration <= 2 and not any(a.startswith("Typed") for a in context["actions_taken"]):
                                # Determine search query based on the goal
                                if "recipe" in initial_goal.lower():
                                    search_query = "best pizza recipe"
                                elif "iphone" in initial_goal.lower():
                                    search_query = "iphone 16 pro buy"
                                else:
                                    search_query = initial_goal
                                
                                # Human-like interaction with search
                                # First, move mouse to the search box
                                element_position = page.evaluate(f"""() => {{
                                    const element = document.querySelector('{search_selector}');
                                    if (!element) return null;
                                    const rect = element.getBoundingClientRect();
                                    return {{ x: rect.x + rect.width/2, y: rect.y + rect.height/2 }};
                                }}""")
                                
                                if element_position:
                                    # Move mouse naturally to search box
                                    from src.automation.action_executor import move_mouse_naturally
                                    move_mouse_naturally(page, element_position['x'], element_position['y'])
                                
                                # Click and clear the search box
                                page.click(search_selector)
                                page.fill(search_selector, "")
                                
                                # Type with human-like delays
                                for char in search_query:
                                    page.type(search_selector, char, delay=random.randint(50, 200))
                                    time.sleep(random.uniform(0.01, 0.05))
                                
                                # Pause briefly before pressing enter
                                time.sleep(random.uniform(0.5, 1.5))
                                page.press(search_selector, "Enter")
                                
                                print(f"Performed direct search with selector: {search_selector}")
                                # Wait for results page to load
                                page.wait_for_timeout(3000)
                                
                                # Record actions
                                context["actions_taken"].append(f"Typed '{search_query}' into search box")
                                context["actions_taken"].append("Pressed Enter to search")
                                break
                    except Exception as e:
                        continue
            except Exception as e:
                print(f"Direct search attempt failed: {e}")
            
        # Get AI decision with context
        try:
            ai_response = reasoner.get_response(context_message, metadata)
            print("AI Response:", ai_response)
        except Exception as e:
            print(f"AI API error: {e}")
            # Create a fallback response when API fails
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
                # If we're already on a recipe site, mark task as complete
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
                # Generic fallback for other pages
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
            actions = execute_actions(page, ai_response)
            
            # Check if we're stuck in a loop
            if actions == context["previous_actions"]:
                context["stuck_counter"] += 1
            else:
                context["stuck_counter"] = 0
                
            # If we're stuck for 3 iterations, try a different approach
            if context["stuck_counter"] >= 3:
                print("Detected loop, trying alternative approach...")
                
                # If we're stuck on Google with a cookie banner
                if "google.com" in current_url:
                    # Try direct search without handling cookies
                    try:
                        # Try multiple selectors for Google's search box
                        search_selectors = [
                            "textarea[name='q']",  # Google now often uses textarea instead of input
                            "input[name='q']",
                            "[aria-label='Search']",
                            ".gLFyf"  # Google's search class
                        ]
                        
                        for search_selector in search_selectors:
                            try:
                                if page.is_visible(search_selector, timeout=1000):
                                    # Determine search query based on goal
                                    if "recipe" in initial_goal.lower():
                                        search_query = "best pizza recipe"
                                    else:
                                        search_query = initial_goal
                                        
                                    # Human-like typing
                                    page.click(search_selector)
                                    page.fill(search_selector, "")
                                    for char in search_query:
                                        page.type(search_selector, char, delay=random.randint(50, 150))
                                    
                                    time.sleep(random.uniform(0.5, 1.0))
                                    page.press(search_selector, "Enter")
                                    print(f"Attempted direct search for '{search_query}' with selector {search_selector}")
                                    context["stuck_counter"] = 0
                                    page.wait_for_timeout(3000)
                                    break
                            except Exception as e:
                                continue
                        
                        if context["stuck_counter"] > 0:  # If all selectors failed
                            # If Google is persistently problematic, try going to a recipe site directly
                            if "recipe" in initial_goal.lower():
                                print("Bypassing Google search and going directly to recipe site")
                                direct_success = attempt_direct_recipe_search(page, context)
                                if direct_success:
                                    context["stuck_counter"] = 0
                            else:
                                # If that fails, reload the page and try again
                                page.reload()
                                print("Reloaded the page to try again")
                                context["stuck_counter"] = 0
                    except Exception as e:
                        print(f"Alternative approach failed: {e}")
                        page.reload()
                        print("Reloaded the page to try again")
                        context["stuck_counter"] = 0
                
                # If we're stuck on a CAPTCHA page too many times
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
                
            # Store the current actions for next comparison
            context["previous_actions"] = actions
            
            if actions:
                context["actions_taken"].extend(actions)
                print(f"Actions performed: {', '.join(actions)}")
            
            # Check if task is complete
            response_json = extract_json(ai_response)
            if response_json and "complete" in response_json and response_json["complete"] == True:
                print("\n=== TASK COMPLETED! ===")
                print(f"Final state: {response_json.get('state', 'Task successful')}")
                print(f"Analysis: {response_json.get('analysis', 'Goal accomplished')}")
                break
                
            # Update context state if available
            if response_json and "state" in response_json:
                context["current_state"] = response_json["state"]
        except Exception as e:
            print(f"Error processing AI response: {e}")
        
        # Wait before next iteration with variable interval
        actual_interval = random.uniform(max(1, interval-1), interval+2)
        print(f"Waiting {actual_interval:.1f} seconds before next iteration...")
        time.sleep(actual_interval)
    
    # Final summary
    print("\n=== Task Summary ===")
    print(f"Original goal: {initial_goal}")
    print(f"Final state: {context['current_state']}")
    print("Actions taken:")
    for i, action in enumerate(context["actions_taken"]):
        print(f"  {i+1}. {action}")
    
    return context


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
            # Clean up temporary profile if needed
            if temp_profile_path:
                import shutil
                shutil.rmtree(temp_profile_path, ignore_errors=True)