# File: src/telemetry/metrics.py

import time

class MetricsTracker:
    def __init__(self):
        self.start_time = time.time()
        self.actions = []

    def log_action(self, action_name, status, details=None):
        """
        Log an action's execution status with a timestamp.
        Parameters:
          - action_name: Name of the executed action.
          - status: Outcome of the action (e.g., "Success", "Failed").
          - details: Optional additional details or error messages.
        """
        timestamp = time.time() - self.start_time
        self.actions.append({
            "action": action_name,
            "status": status,
            "details": details,
            "timestamp": timestamp
        })

    def get_metrics(self):
        """
        Return the list of logged actions with their metrics.
        """
        return self.actions

    def print_metrics(self):
        """
        Print all logged actions in a human-readable format.
        """
        for entry in self.actions:
            print(f"[{entry['timestamp']:.2f}s] {entry['action']}: {entry['status']} - {entry['details']}")
