# src/tasks/task_manager.py

class Subtask:
    """
    Represents a single actionable subtask with a clear objective,
    optional preconditions, and a completion state.
    
    Args:
        description (str): A short human-readable description of the subtask.
        preconditions (list): A list of context keys or conditions that must be True
                              for this subtask to start.
        completion_check (callable): A function or lambda that returns True if the
                                     subtask is already satisfied. For example,
                                     it might check the current URL or a flag in the context.
    """
    def __init__(self, description, preconditions=None, completion_check=None):
        self.description = description
        self.preconditions = preconditions if preconditions else []
        self.is_complete = False
        self.completion_check = completion_check  # Optional callable to auto-check completion

    def mark_complete(self):
        """Mark this subtask as complete."""
        self.is_complete = True

    def can_start(self, context):
        """
        Check if all preconditions are met based on the current context.
        Return True if the subtask can begin, False otherwise.
        """
        return all(context.get(cond, False) for cond in self.preconditions)

    def check_if_complete(self, page, context):
        """
        If a completion_check function is provided, call it to see if the subtask
        is already satisfied (e.g., we are on the correct URL or a certain flag is set).

        Args:
            page: The current Playwright page object (if needed).
            context: The agent's context dictionary.

        Returns:
            bool: True if the subtask is already complete, False otherwise.
        """
        if self.completion_check and not self.is_complete:
            return self.completion_check(page, context)
        return False


class Task:
    """
    Represents a higher-level goal that is broken down into multiple Subtasks.
    Tracks overall progress, context, and can determine the next subtask.
    """
    def __init__(self, name, subtasks=None):
        self.name = name
        self.subtasks = subtasks if subtasks else []
        self.current_index = 0

    def add_subtask(self, subtask):
        """Add a new Subtask to this Task."""
        self.subtasks.append(subtask)

    def get_current_subtask(self):
        """
        Return the current Subtask based on current_index, or None if
        all subtasks are completed.
        """
        if self.current_index < len(self.subtasks):
            return self.subtasks[self.current_index]
        return None

    def mark_subtask_complete(self):
        """
        Mark the current subtask as complete and move on to the next one.
        """
        if self.current_index < len(self.subtasks):
            self.subtasks[self.current_index].mark_complete()
            self.current_index += 1

    def is_complete(self):
        """
        Check if all subtasks have been completed.

        Returns:
            bool: True if current_index >= len(self.subtasks), False otherwise.
        """
        return self.current_index >= len(self.subtasks)

    def reset(self):
        """
        Reset the task to its initial state, marking all subtasks as incomplete
        and resetting current_index to 0.
        """
        self.current_index = 0
        for sub in self.subtasks:
            sub.is_complete = False
