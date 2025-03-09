# File: src/utils/agent_state.py

import json
import os

class AgentState:
    def __init__(self, state_file="agent_state.json"):
        """
        Initialize the agent state with an optional file for persistence.
        - context: Holds persistent data across interactions.
        - history: Manages a list of messages and the current token count.
        """
        self.state_file = state_file
        self.context = {}
        self.history = {
            "messages": [],
            "current_tokens": 0
        }
        self.load_state()

    def load_state(self):
        """
        Load the agent state from the specified JSON file, if it exists.
        """
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                data = json.load(f)
                self.context = data.get("context", {})
                self.history = data.get("history", {"messages": [], "current_tokens": 0})

    def save_state(self):
        """
        Save the current state (context and history) to the JSON file.
        """
        data = {
            "context": self.context,
            "history": self.history
        }
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def add_message(self, message):
        """
        Add a new message to the history.
        The message is expected to be a dictionary with at least a 'content' key.
        Also updates the token count based on the message content.
        """
        self.history["messages"].append(message)
        # Simple token count estimation: one token per character (for demonstration)
        self.history["current_tokens"] += len(message.get("content", ""))

    def remove_last_state_message(self):
        """
        Remove the last message from the history and update the token count.
        Returns the removed message, or None if no messages exist.
        """
        if self.history["messages"]:
            removed = self.history["messages"].pop()
            self.history["current_tokens"] -= len(removed.get("content", ""))
            return removed
        return None
