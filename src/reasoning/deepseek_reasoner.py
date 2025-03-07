import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq  # Ensure groq is installed
from src.feedback.chat_logger import ChatLogger
from src.prompts.system_prompt import get_system_prompt

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

    def get_response(self, user_message: str, metadata: dict, dom_data=None, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Get a response from DeepSeek model by passing the current context and metadata.
        
        :param user_message: The current context message (containing goal and state).
        :param metadata: A dictionary containing vision output (detections and OCR results).
        :param dom_data: Optional DOM-based information about the page structure
        :param temperature: Sampling temperature for response generation.
        :param max_tokens: Maximum tokens to generate in the response.
        :return: The AI-generated response.
        """
        # Create a detailed summary of what's visible on the page
        ocr_texts = [item.get('text', '') for item in metadata.get('ocr_results', [])]
        ocr_summary = ", ".join(ocr_texts) if ocr_texts else "No text detected"
        # DOM information if available
        dom_info = ""
        if dom_data:
            interactive_counts = []
            if 'buttons' in dom_data:
                interactive_counts.append(f"{dom_data['buttons']} buttons")
            if 'links' in dom_data:
                interactive_counts.append(f"{dom_data['links']} links")
            if 'inputs' in dom_data:
                interactive_counts.append(f"{dom_data['inputs']} input fields")
            if 'selects' in dom_data:
                interactive_counts.append(f"{dom_data['selects']} dropdown menus")
            
            dom_info = f"DOM Analysis: Found {', '.join(interactive_counts)}. "
            
            # Optionally, add additional DOM details if available (like search boxes or headings)
            if 'search_boxes' in dom_data and dom_data['search_boxes']:
                dom_info += f"Detected search boxes. "
        
        # Number of objects detected
        num_objects = len(metadata.get('object_detections', []))
        
        # DOM information if available
        dom_info = ""
        if dom_data:
            interactive_counts = []
            if 'buttons' in dom_data:
                interactive_counts.append(f"{dom_data['buttons']} buttons")
            if 'links' in dom_data:
                interactive_counts.append(f"{dom_data['links']} links")
            if 'inputs' in dom_data:
                interactive_counts.append(f"{dom_data['inputs']} input fields")
            if 'selects' in dom_data:
                interactive_counts.append(f"{dom_data['selects']} dropdown menus")
                
            dom_info = f"DOM Analysis: Found {', '.join(interactive_counts)}. "
            
            # Add search box information if available
            if 'search_boxes' in dom_data and dom_data['search_boxes']:
                search_info = [f"Search box with placeholder: '{box.get('placeholder', 'None')}'" 
                            for box in dom_data['search_boxes'][:2]]
                dom_info += f"Detected search boxes: {', '.join(search_info)}. "

                # Add page content information if available
                if 'headings' in dom_data:
                    headings = []
                    for level, texts in dom_data.get('headings', {}).items():
                        if texts:
                            headings.extend(texts[:2])  # Include up to 2 headings per level
                    if headings:
                        dom_info += f"Top headings: {', '.join(headings[:3])}. "
        
        # Craft a detailed system prompt that helps the model understand its task
        # Update the system prompt to include DOM-based instructions and task decomposition
        system_prompt = get_system_prompt()

        # Create the prompt with context and metadata
        prompt_message = f"""
    CURRENT CONTEXT:
    {user_message}

    VISUAL INFORMATION:
    {json.dumps(metadata, indent=2)}
    """
        
        # Call the DeepSeek API with the system prompt
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }

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