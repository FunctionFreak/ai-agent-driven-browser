# File: src/feedback/chat_logger.py
import json
import os
from datetime import datetime

class ChatLogger:
    def __init__(self, log_file="chat_history.json"):
        self.log_file = log_file
        # Load existing conversation if available
        if os.path.exists(log_file):
            with open(log_file, "r") as f:
                try:
                    self.conversation = json.load(f)
                except json.JSONDecodeError:
                    self.conversation = []
        else:
            self.conversation = []
    
    def log_message(self, role: str, content: str):
        """
        Log a new message into the conversation.
        
        :param role: The role of the message sender ("system", "user", or "assistant")
        :param content: The content of the message
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "role": role,
            "content": content
        }
        self.conversation.append(entry)
        self._save()
    
    def _save(self):
        with open(self.log_file, "w") as f:
            json.dump(self.conversation, f, indent=2)
    
    def get_conversation(self):
        """
        Retrieve the complete conversation history.
        """
        return self.conversation

# Example usage:
if __name__ == "__main__":
    logger = ChatLogger()
    logger.log_message("user", "How should I click the button?")
    logger.log_message("assistant", "You should click the button located in the top-right corner.")
    conversation = logger.get_conversation()
    print(json.dumps(conversation, indent=2))
