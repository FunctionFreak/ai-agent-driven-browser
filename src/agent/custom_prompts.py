# File: src/agent/custom_prompts.py

from langchain_core.messages import SystemMessage

class CustomSystemPrompt:
    def __init__(self, action_description, max_actions_per_step=10):
        self.action_description = action_description
        self.max_actions_per_step = max_actions_per_step

    def get_system_message(self):
        prompt = f"""You are an AI agent designed to automate browser tasks using DeepSeek.
Your response must be valid JSON and strictly follow this format:

{{
  "current_state": {{
    "prev_action_evaluation": "Success|Failed|Unknown - Evaluate if previous actions succeeded",
    "important_contents": "Relevant extracted content from the current page",
    "task_progress": "Summary of completed steps (e.g., 1. Step1, 2. Step2, ...)",
    "future_plans": "Outline the next steps required",
    "thought": "Your reasoning for the next action",
    "summary": "A concise summary of the next operation"
  }},
  "action": [
    // Up to {self.max_actions_per_step} actions.
    // Each action should be in the format: {{"action_name": {{parameters}}}}
  ]
}}

Available actions: {self.action_description}

Rules:
1. Analyze the current page context carefully.
2. Ensure all responses are valid JSON.
3. Include your reasoning in the "thought" field.
4. Do not include any extraneous information.
"""
        return SystemMessage(content=prompt)
