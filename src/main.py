# File: src/main.py

import os
import logging
import shutil
import random
import time
from dotenv import load_dotenv
from src.handlers.search_handler import SearchHandler
from src.utils.json_utils import extract_json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Project imports
from src.automation.playwright_controller import launch_browser_with_profile
from src.feedback.feedback_loop import feedback_loop

def main():
    # Load environment variables
    load_dotenv()
    
    print("===== AI-Driven Browser Automation =====")
    print("This agent will use AI to complete browsing tasks autonomously.")
    print("Examples of tasks you can request:")
    print("- 'Search for iPhone 16 Pro on Amazon'")
    print("- 'Find a good pizza recipe'")
    print("- 'Look up the weather forecast for New York'")
    print("- 'Check the top news headlines'")
    print()

    # Get high-level goal from the user
    user_goal = input("What would you like the browser agent to do? ")
    
    print("\nLaunching browser and starting autonomous agent...")
    print("(Press Ctrl+C at any time to stop the process)")
    
    # Show a more human-like startup message
    startup_messages = [
        "Initializing browser environment...",
        "Setting up AI-driven automation...",
        "Preparing to navigate the web...",
        "Starting autonomous browsing session..."
    ]
    
    for message in startup_messages:
        print(message)
        # Random delay between messages
        time.sleep(random.uniform(0.3, 1.0))
    
    # Launch browser with persistent profile
    try:
        browser_context, temp_profile_path = launch_browser_with_profile()
        page = browser_context.new_page()
        
        try:
            # Run the continuous feedback loop with the enhanced version
            feedback_loop(page, user_goal, max_iterations=20, interval=3)
        except KeyboardInterrupt:
            print("\nProcess interrupted by user.")
        except Exception as e:
            logging.error(f"Error during execution: {e}")
        finally:
            # Let the user see the final state before closing
            input("\nPress Enter to close the browser...")
            browser_context.close()
            
            # Only clean up temporary profile if one was created
            if temp_profile_path:
                print(f"Cleaning up temporary Chrome profile...")
                shutil.rmtree(temp_profile_path, ignore_errors=True)
    except Exception as e:
        logging.error(f"Failed to launch browser: {e}")
        print("\nError: Could not start the browser. Please check your Chrome installation and configuration.")

if __name__ == "__main__":
    main()