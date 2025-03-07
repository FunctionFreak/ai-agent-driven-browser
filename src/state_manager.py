import logging

class StateManager:
    def __init__(self):
        # Initialize the state dictionary with default values.
        self.state = {
            "goal": None,
            "current_subtask": None,
            "progress": 0,    # Percentage of completion
            "history": []     # List of completed subtasks
        }
        logging.info("StateManager initialized.")

    def initialize_state(self, goal: str, current_subtask: str = None):
        """Initialize the agent state with a goal and an optional subtask."""
        self.state["goal"] = goal
        self.state["current_subtask"] = current_subtask
        self.state["progress"] = 0
        self.state["history"] = []
        logging.info("State initialized with goal: '%s' and subtask: '%s'", goal, current_subtask)

    def update_subtask(self, subtask: str):
        """Update the current subtask and add it to the history."""
        self.state["current_subtask"] = subtask
        self.state["history"].append(subtask)
        logging.info("Updated current subtask to: '%s'", subtask)

    def update_progress(self, progress: int):
        """
        Update the progress percentage.
        
        Args:
            progress: An integer representing the current completion percentage.
        """
        self.state["progress"] = progress
        logging.info("Updated progress to: %d%%", progress)

    def get_state(self):
        """Retrieve the current state."""
        return self.state

    def reset_state(self):
        """Reset the state to its initial default values."""
        self.state = {
            "goal": None,
            "current_subtask": None,
            "progress": 0,
            "history": []
        }
        logging.info("State reset to initial state.")
