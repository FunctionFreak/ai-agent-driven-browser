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
        Get a response from DeepSeek model by passing the current conversation and metadata as context.
        
        :param user_message: The current user message.
        :param metadata: A dictionary containing vision output (detections and OCR results).
        :param temperature: Sampling temperature for response generation.
        :param max_tokens: Maximum tokens to generate in the response.
        :return: The AI-generated response.
        """
        # Prepare a summary context from the metadata.
        metadata_summary = f"Metadata summary: {metadata}\n"
        # Optionally, include recent conversation history (for brevity, you could limit this)
        conversation_history = self.chat_logger.get_conversation()
        conversation_summary = ""
        for entry in conversation_history[-5:]:
            conversation_summary += f"{entry['role'].capitalize()}: {entry['content']}\n"
        
        # Combine the metadata summary, conversation history, and the current user message
        prompt_message = metadata_summary + conversation_summary + f"User: {user_message}"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are an AI automation assistant. When given metadata and a user command, output only a valid JSON object with a 'commands' array. Each command should be formatted as: { 'action': 'navigate', 'url': 'https://example.com' } (or similar for 'click' or 'input'). Do not include any additional text or explanations."},
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