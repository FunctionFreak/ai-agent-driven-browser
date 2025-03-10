# File: src/task/task_manager.py

class Subtask:
    """
    Represents a single actionable subtask with a clear objective.
    """
    def __init__(self, description, preconditions=None, completion_check=None):
        self.description = description
        self.preconditions = preconditions or []
        self.completion_check = completion_check
        self.is_complete = False

    def mark_complete(self):
        self.is_complete = True

    def can_start(self, context):
        """Check if all preconditions are met based on the provided context."""
        return all(context.get(cond, False) for cond in self.preconditions)

    def check_if_complete(self, page, context):
        """
        Check if the subtask is complete based on the current page or state.
        Returns a boolean indicating completion status.
        """
        if self.completion_check and not self.is_complete:
            return self.completion_check(page, context)
        return False


class Task:
    """
    Represents a higher-level goal broken down into manageable subtasks.
    """
    def __init__(self, name, subtasks=None):
        self.name = name
        self.subtasks = subtasks or []
        self.current_index = 0

    def add_subtask(self, subtask):
        """Add a new subtask to the task."""
        self.subtasks.append(subtask)

    def get_current_subtask(self):
        """Return the current subtask to be executed, or None if all are complete."""
        if self.current_index < len(self.subtasks):
            return self.subtasks[self.current_index]
        return None

    def mark_subtask_complete(self):
        """Mark the current subtask as complete and move to the next."""
        if self.current_index < len(self.subtasks):
            self.subtasks[self.current_index].mark_complete()
            self.current_index += 1

    def is_complete(self):
        """Return True if all subtasks have been completed."""
        return self.current_index >= len(self.subtasks)
