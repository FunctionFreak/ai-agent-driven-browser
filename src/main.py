# File: src/main.py

import os
from dotenv import load_dotenv

# Playwright imports
from playwright.sync_api import sync_playwright

# Project imports
from src.automation.playwright_controller import launch_browser_with_profile
from src.capture.screen_capture import capture_screenshot
from src.vision.yolov8_detector import YOLOv8Detector
from src.vision.ocr_processor import OCRProcessor
from src.metadata.metadata_generator import MetadataGenerator
from src.reasoning.deepseek_reasoner import DeepSeekReasoner
from src.automation.action_executor import execute_actions

def main():
    # 1. Load environment variables (.env must contain GROQ_API_KEY and CHROME_PROFILE_PATH)
    load_dotenv()

    # 2. Ask user for a command
    user_command = input("Enter your command for the AI-driven browser automation: ")

    # 3. Launch a persistent browser session (make sure headless=False if you want to see the browser)
    browser_context = launch_browser_with_profile()  # headless=False is set inside that function
    page = browser_context.new_page()
    
    # (No initial page.goto() call—so the AI alone decides where to navigate.)

    # 4. Capture a screenshot of the current page (likely blank or default)
    screenshot_path = capture_screenshot(page)
    print(f"Screenshot saved at: {screenshot_path}")

    # 5. Run YOLOv8 for object detection
    detector = YOLOv8Detector(model_variant='yolov8l.pt')
    object_detections = detector.detect(screenshot_path)

    # 6. Run OCR to extract text
    ocr = OCRProcessor()
    ocr_results = ocr.process_image(screenshot_path)

    # 7. Generate metadata from detections + OCR
    meta_gen = MetadataGenerator()
    metadata = meta_gen.generate_metadata(object_detections, ocr_results)
    # (Optional) save metadata to file
    meta_gen.save_metadata(metadata, file_path="metadata.json")

    # 8. Use DeepSeek reasoning to decide the next action
    reasoner = DeepSeekReasoner()
    ai_response = reasoner.get_response(user_command, metadata)
    print("AI Response:", ai_response)

    # 9. Execute the commands from the AI response (e.g., navigate to https://www.google.com)
    execute_actions(page, ai_response)

    # (Optional) Wait a bit so you can see the result before closing
    page.wait_for_timeout(5000)

    # 10. Close the browser context
    browser_context.close()

if __name__ == "__main__":
    main()
