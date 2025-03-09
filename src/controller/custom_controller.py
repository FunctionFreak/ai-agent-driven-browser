# File: src/controller/custom_controller.py

class CustomController:
    def __init__(self):
        """
        Initialize the custom controller with a dictionary of available actions.
        Extend this dictionary with additional specialized actions as needed.
        """
        self.actions = {
            "click": self.click,
            "fill": self.fill,
            "scroll": self.scroll,
            # Add further actions here.
        }

    def execute_action(self, action_name, **parameters):
        """
        Execute the specified action by name with the provided parameters.
        
        Parameters:
          - action_name (str): The name of the action to execute.
          - parameters: Keyword arguments specific to the action.
        
        Returns:
          - The result of the action, if applicable.
        """
        if action_name in self.actions:
            return self.actions[action_name](**parameters)
        else:
            raise ValueError(f"Action '{action_name}' is not supported.")

    def click(self, selector):
        """
        Simulate a click on a given element.
        
        Parameters:
          - selector (str): The CSS selector for the target element.
        """
        print(f"[Controller] Clicking on element with selector: {selector}")
        # Implementation goes here (e.g., integrate with browser automation).

    def fill(self, selector, text):
        """
        Fill an input field with the specified text.
        
        Parameters:
          - selector (str): The CSS selector for the input element.
          - text (str): The text to enter into the input.
        """
        print(f"[Controller] Filling element {selector} with text: '{text}'")
        # Implementation goes here.

    def scroll(self, distance):
        """
        Scroll the page by a given distance.
        
        Parameters:
          - distance (int): The number of pixels to scroll.
        """
        print(f"[Controller] Scrolling by {distance} pixels")
        # Implementation goes here.

# Example usage:
if __name__ == "__main__":
    controller = CustomController()
    controller.execute_action("click", selector="#submit-button")
    controller.execute_action("fill", selector="#username", text="example_user")
    controller.execute_action("scroll", distance=300)
