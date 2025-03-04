import time
from playwright.sync_api import Page
from src.capture.screen_capture import capture_screenshot
from src.vision.yolov8_detector import YOLOv8Detector
from src.vision.ocr_processor import OCRProcessor
from src.metadata.metadata_generator import MetadataGenerator
from src.reasoning.deepseek_reasoner import DeepSeekReasoner
from src.automation.action_executor import execute_actions

def feedback_loop(page: Page, user_command: str, interval: int = 10):
    """
    Continuously loops to capture the screen, process vision data, 
    and execute actions based on AI reasoning.
    
    :param page: The active Playwright page instance.
    :param user_command: The initial user command that seeds the reasoning process.
    :param interval: Time in seconds between iterations of the loop.
    """
    # Initialize vision and reasoning modules
    detector = YOLOv8Detector(model_variant='yolov8l.pt')
    ocr_processor = OCRProcessor()
    metadata_gen = MetadataGenerator()
    reasoner = DeepSeekReasoner()
    
    iteration = 0
    while True:
        iteration += 1
        print(f"Feedback loop iteration {iteration} started.")
        
        # Capture current screen state
        screenshot_path = capture_screenshot(page)
        print(f"Screenshot captured: {screenshot_path}")
        
        # Run vision processing
        object_detections = detector.detect(screenshot_path)
        ocr_results = ocr_processor.process_image(screenshot_path)
        metadata = metadata_gen.generate_metadata(object_detections, ocr_results)
        metadata_gen.save_metadata(metadata, file_path=f"metadata_{iteration}.json")
        print("Metadata generated and saved.")
        
        # Get AI response based on current metadata and original command
        ai_response = reasoner.get_response(user_command, metadata)
        print("AI Response:", ai_response)
        
        # Execute actions based on AI response
        execute_actions(page, ai_response)
        
        print(f"Iteration {iteration} complete. Waiting {interval} seconds before next iteration...\n")
        time.sleep(interval)

# Example usage:
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright
    from dotenv import load_dotenv
    import os

    load_dotenv()
    
    user_command = input("Enter your command for the AI-driven browser automation: ")
    
    with sync_playwright() as p:
        # Assume you have set CHROME_PROFILE_PATH in your .env file and use the persistent context
        from src.automation.playwright_controller import launch_browser_with_profile
        browser_context = launch_browser_with_profile()
        page = browser_context.new_page()
        page.goto("https://example.com")
        
        try:
            feedback_loop(page, user_command, interval=10)
        except KeyboardInterrupt:
            print("Feedback loop terminated by user.")
        finally:
            browser_context.close()
