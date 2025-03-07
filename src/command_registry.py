from pydantic import BaseModel, ValidationError, Field
from typing import Any, Callable, Dict, List
import logging

class CommandSchema(BaseModel):
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

class CommandRegistry:
    def __init__(self):
        # Registry to map command names to their handler functions
        self.registry: Dict[str, Callable[[CommandSchema], bool]] = {}
    
    def register(self, action: str, handler: Callable[[CommandSchema], bool]):
        """
        Register a command handler for a specific action.
        
        Args:
            action: The command action name.
            handler: A function that takes a CommandSchema and returns a boolean indicating success.
        """
        if action in self.registry:
            logging.warning(f"Handler for action '{action}' is already registered. Overwriting.")
        self.registry[action] = handler
    
    def execute(self, command_data: Dict[str, Any]) -> bool:
        """
        Validate and execute a command.
        
        Args:
            command_data: A dictionary representing the command.
            
        Returns:
            bool: True if command executed successfully, False otherwise.
        """
        try:
            command = CommandSchema(**command_data)
        except ValidationError as e:
            logging.error(f"Command validation error: {e}")
            return False
        
        handler = self.registry.get(command.action)
        if not handler:
            logging.error(f"No handler registered for action: {command.action}")
            return False
        
        return handler(command)

    def list_registered(self) -> List[str]:
        """
        Return a list of registered command actions.
        
        Returns:
            List[str]: A list of action names.
        """
        return list(self.registry.keys())
