# File: src/history/recorder.py

import json
import os
from datetime import datetime

class HistoryRecorder:
    def __init__(self, history_file="chat_history.json"):
        """
        Initialize the HistoryRecorder with the specified file.
        If the file exists, load its content; otherwise, start with an empty history.
        """
        self.history_file = history_file
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                self.history = json.load(f)
        else:
            self.history = []

    def record_interaction(self, interaction):
        """
        Record a new interaction to the history.
        'interaction' should be a dictionary containing details such as:
          - user_message
          - agent_response
          - additional metadata as needed
        A timestamp is automatically added.
        """
        interaction['timestamp'] = datetime.utcnow().isoformat()
        self.history.append(interaction)
        self._save_history()

    def _save_history(self):
        """
        Save the current history list to the JSON file.
        """
        with open(self.history_file, "w") as f:
            json.dump(self.history, f, indent=2)

    def get_history(self):
        """
        Retrieve the entire interaction history.
        """
        return self.history

    def replay_history(self):
        """
        Replay the interaction history by printing each entry.
        Useful for debugging or reviewing past sessions.
        """
        for entry in self.history:
            print(f"Timestamp: {entry.get('timestamp')}")
            print(f"User: {entry.get('user_message')}")
            print(f"Agent: {entry.get('agent_response')}")
            print("-" * 40)
