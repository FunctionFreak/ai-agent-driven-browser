# File: src/agent/custom_message_manager.py

class CustomMessageManager:
    def __init__(self, state, settings):
        """
        Initialize the custom message manager with current state and settings.
        'state' should provide access to the history of messages and current token count.
        'settings' must contain parameters such as max_input_tokens and image_tokens.
        """
        self.state = state
        self.settings = settings

    def cut_messages(self):
        """
        Trims the message history to ensure the total token count remains within the maximum limit.
        It removes or truncates content (e.g., image data, text) from the last message if necessary.
        """
        diff = self.state.history.current_tokens - self.settings.max_input_tokens
        if diff <= 0:
            return None

        # Attempt to remove image content first if present to free tokens
        last_message = self.state.history.messages[-1]
        if isinstance(last_message.content, list):
            for i, item in enumerate(last_message.content):
                if 'image_url' in item:
                    last_message.content.pop(i)
                    diff -= self.settings.image_tokens
                    self.state.history.current_tokens -= self.settings.image_tokens
                    if diff <= 0:
                        return None

        # If still over the token limit, trim the text content proportionally
        proportion_to_remove = diff / last_message.metadata.tokens
        if proportion_to_remove > 0.99:
            raise ValueError("Max token limit reached - history is too long")

        if isinstance(last_message.content, str):
            characters_to_remove = int(len(last_message.content) * proportion_to_remove)
            last_message.content = last_message.content[:-characters_to_remove]
        elif isinstance(last_message.content, list):
            for item in last_message.content:
                if isinstance(item, dict) and 'text' in item:
                    characters_to_remove = int(len(item['text']) * proportion_to_remove)
                    item['text'] = item['text'][:-characters_to_remove]

        # Remove the old message and add the trimmed version back to the history
        self.state.history.remove_last_state_message()
        self.state.history.add_message(last_message)
        return last_message
