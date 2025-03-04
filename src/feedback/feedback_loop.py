import time
import json
import logging
from playwright.sync_api import Page
from src.capture.screen_capture import capture_screenshot
from src.vision.yolov8_detector import YOLOv8Detector
from src.vision.ocr_processor import OCRProcessor
from src.metadata.metadata_generator import MetadataGenerator
from src.reasoning.deepseek_reasoner import DeepSeekReasoner
from src.automation.action_executor import execute_actions
# Add this import at the top of src/feedback/feedback_loop.py
from src.automation.action_executor import extract_json

# In src/feedback/feedback_loop.py

def feedback_loop(page, initial_goal: str, max_iterations=20, interval: int = 3):
    """
    Enhanced feedback loop with progress tracking
    """
    # First, maximize the window
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
        "stuck_counter": 0      # To track if we're stuck
    }
    
    for iteration in range(1, max_iterations + 1):
        context["iteration"] = iteration
        print(f"\n--- Feedback Loop Iteration {iteration}/{max_iterations} ---")
        print(f"Current goal: {initial_goal}")
        print(f"Current state: {context['current_state']}")
        
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
        
        # Current URL info
        current_url = page.url
        context_message = f"GOAL: {initial_goal}\nCURRENT URL: {current_url}\nCURRENT STATE: {context['current_state']}\nITERATION: {iteration}/{max_iterations}"
        
        # If we're on Google and see a cookie notice, handle it directly
        if "google.com" in current_url and any("cookie" in r['text'].lower() for r in ocr_results):
            try:
                # Try direct JavaScript approach to accept cookies
                print("Detected Google cookie notice, attempting direct handling...")
                page.evaluate('''() => {
                    const buttons = Array.from(document.querySelectorAll('button'));
                    const acceptButton = buttons.find(button => 
                        button.textContent.toLowerCase().includes('accept all') || 
                        button.textContent.toLowerCase().includes('i agree')
                    );
                    if (acceptButton) acceptButton.click();
                }''')
                page.wait_for_timeout(2000)  # Wait for the banner to disappear
                # Skip to next iteration to check if it worked
                continue
            except:
                pass
            
        # Get AI decision with context
        ai_response = reasoner.get_response(context_message, metadata)
        print("AI Response:", ai_response)
        
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
                        # Try to input directly into the search box
                        search_query = "best pizza recipe"
                        page.fill("input[name='q']", search_query)
                        page.press("input[name='q']", "Enter")
                        print(f"Attempted direct search for '{search_query}'")
                        context["stuck_counter"] = 0
                    except:
                        # If that fails, reload the page and try again
                        page.reload()
                        print("Reloaded the page to try again")
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
        
        # Wait before next iteration
        print(f"Waiting {interval} seconds before next iteration...")
        time.sleep(interval)
    
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
        browser_context = launch_browser_with_profile()
        page = browser_context.new_page()
        
        try:
            feedback_loop(page, user_goal)
        except KeyboardInterrupt:
            print("Process terminated by user.")
        finally:
            input("Press Enter to close the browser...")
            browser_context.close()