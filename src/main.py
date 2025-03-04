# File: src/main.py

import os
import logging
import shutil
from dotenv import load_dotenv

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
    
    # Launch browser with persistent profile (using temporary copy)
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
        
        # Clean up the temporary profile
        print(f"Cleaning up temporary Chrome profile...")
        shutil.rmtree(temp_profile_path, ignore_errors=True)

if __name__ == "__main__":
    main()