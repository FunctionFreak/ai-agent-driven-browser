def preprocess_command(user_command: str) -> dict:
    """
    Preprocess a high-level user command and break it down into actionable commands.
    
    For example, if the command contains the keyword "nowtv", it returns a command
    to navigate directly to the NOW TV homepage. Otherwise, it defaults to a search action.
    
    Args:
        user_command (str): The high-level instruction from the user.
        
    Returns:
        dict: A JSON-compatible command structure with keys "analysis", "state", 
              "commands", and "complete".
    """
    lower_cmd = user_command.lower().strip()
    
    if "nowtv" in lower_cmd:
        # Directly navigate to NOW TV's homepage if detected.
        return {
            "analysis": "Interpreted command to open NOW TV directly.",
            "state": "Navigating to NOW TV homepage.",
            "commands": [
                {"action": "navigate", "url": "https://www.nowtv.com/"}
            ],
            "complete": False
        }
    else:
        # Fallback: perform a search using the user's command.
        return {
            "analysis": f"Interpreted command: Searching for '{user_command}'.",
            "state": "Performing search.",
            "commands": [
                {"action": "input", "selector": "input[name='q']", "text": user_command, "submit": True}
            ],
            "complete": False
        }
