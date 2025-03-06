import os
import requests
from dotenv import load_dotenv
from groq import Groq  # Ensure groq is installed
from src.feedback.chat_logger import ChatLogger

# Load environment variables from .env
load_dotenv()

class DeepSeekReasoner:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not set in environment variables.")
        
        self.groq_api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_name = "deepseek-r1-distill-llama-70b"
        # Initialize the Groq instance (if needed)
        self.groq_instance = Groq(api_key=self.api_key)
        # Initialize the conversation logger to maintain context
        self.chat_logger = ChatLogger()

    def get_response(self, user_message: str, metadata: dict, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Get a response from DeepSeek model by passing the current context and metadata.
        
        :param user_message: The current context message (containing goal and state).
        :param metadata: A dictionary containing vision output (detections and OCR results).
        :param temperature: Sampling temperature for response generation.
        :param max_tokens: Maximum tokens to generate in the response.
        :return: The AI-generated response.
        """
        # Create a detailed summary of what's visible on the page
        ocr_texts = [item.get('text', '') for item in metadata.get('ocr_results', [])]
        ocr_summary = ", ".join(ocr_texts) if ocr_texts else "No text detected"
        
        # Number of objects detected
        num_objects = len(metadata.get('object_detections', []))
        
        # Craft a detailed system prompt that helps the model understand its task
        system_prompt = """You are an autonomous browser agent that can see and interact with web pages. Your goal is to accomplish the user's task by breaking it down into smaller steps and reasoning about the current state.

# WORKFLOW:
1. ANALYZE THE CURRENT STATE:
   - Analyze what page you're on and what elements are visible
   - Check if there are any blocking elements (cookie banners, login prompts, popups)
   - Identify the interactive elements needed to progress toward the goal
   
2. NAVIGATION PATH:
   - If you need to visit a specific website, navigate there directly if URL is known
   - Otherwise, use Google search to find relevant pages
   - When using search engines, use specific, well-formed queries related to the task
   - IMPORTANT: Avoid sponsored links and ads, prioritize organic search results

3. ELEMENT INTERACTION:
   - For cookie banners, PREFER to click "Reject" or "Reject all" buttons when available
   - Only use "Accept all" as a fallback when rejection is not possible
   - For Amazon, use selector "input[id='twotabsearchtextbox']" for the search box
   - For Google search, use selector "textarea[name='q']" instead of "input[name='q']"
   - For navigation, find and click on the most relevant links
   - For forms, fill in required fields and submit

4. PROGRESS TRACKING:
   - Keep track of what has been done and what remains
   - Handle any unexpected situations that arise
   - Signal when the task is complete

# OUTPUT FORMAT:
ALWAYS respond with a valid JSON object in the following format - this is critically important:
{
  "analysis": "Detailed description of what you observe on the screen",
  "state": "Current progress toward the goal",
  "commands": [
    {"action": "navigate", "url": "https://example.com"},
    {"action": "click", "text": "Accept all"},
    {"action": "input", "selector": "input[name='q']", "text": "query", "submit": true},
    {"action": "scroll", "direction": "down", "amount": 300}
  ],
  "complete": false
}

Make sure your response contains ONLY this JSON object with no additional text, markdown, or explanation before or after.

Make decisions based on the OCR text you can see on the page. Focus on moving towards the goal step by step.
"""

        # Construct a detailed prompt with context and visuals
        prompt_message = f"""
    CURRENT GOAL AND STATE:
    {user_message}

    VISUAL INFORMATION:
    - OCR detected text: {ocr_summary}
    - Number of UI elements detected: {num_objects}

    Based on what you can see and where you are, what's the next best action to take to achieve the goal?
    """

        # Call the DeepSeek API
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.groq_api_url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            
            # Log both the user message and the assistant response for future context
            self.chat_logger.log_message("user", user_message)
            self.chat_logger.log_message("assistant", answer)
            
            return answer
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

# Example usage:
if __name__ == "__main__":
    # Test 1: Using dummy metadata with an empty detection list
    dummy_metadata = {"object_detections": [], "ocr_results": []}
    reasoner = DeepSeekReasoner()
    response = reasoner.get_response("Go to https://www.google.com", dummy_metadata)
    print("DeepSeek response (empty metadata):", response)
    
    # Test 2: Using dummy metadata with sample detections
    dummy_metadata_with_data = {
        "timestamp": "2023-03-04T00:00:00",
        "object_detections": [
            {"bbox": [100, 100, 200, 200], "confidence": 0.95, "class": 0}
        ],
        "ocr_results": [
            {"bbox": [[10, 10], [10, 50], [50, 50], [50, 10]], "text": "Hello", "confidence": 0.85}
        ]
    }
    response_with_data = reasoner.get_response("What action should I perform next?", dummy_metadata_with_data)
    print("DeepSeek response (with data):", response_with_data)