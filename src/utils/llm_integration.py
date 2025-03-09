# File: src/utils/llm_integration.py

import asyncio
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

class DeepSeekLLMManager:
    def __init__(self, api_key, base_url=None, model="deepseek-reasoner"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.max_retries = 3

    async def agenerate_with_retry(self, messages, temperature=0.7):
        retries = 0
        while retries < self.max_retries:
            try:
                return await self._agenerate(messages, temperature)
            except Exception as e:
                retries += 1
                await asyncio.sleep(2 ** retries)  # Exponential backoff
        raise Exception("Max retries reached for DeepSeek LLM API call.")

    async def _agenerate(self, messages, temperature):
        formatted_messages = self._format_messages(messages)
        # TODO: Replace the following simulated response with an actual API call to DeepSeek.
        # Simulated response includes a thinking block as typically returned by DeepSeek.
        simulated_response = {
            "choices": [{
                "message": {
                    "content": (
                        "<think>\n"
                        "Okay, I need to help the user open Netflix and navigate to their account. "
                        "First, navigate to Netflix homepage...\n"
                        "</think>\n"
                        "Simulated AI response content after thinking block."
                    )
                }
            }]
        }
        raw_content = simulated_response["choices"][0]["message"]["content"]
        content, reasoning_content = self._strip_thinking_block(raw_content)
        return AIMessage(content=content, reasoning_content=reasoning_content)

    def _strip_thinking_block(self, content):
        """
        Checks for a <think>...</think> block in the content.
        If found, extracts its content as the reasoning block and removes it from the main content.
        """
        start_tag = "<think>"
        end_tag = "</think>"
        start = content.find(start_tag)
        end = content.find(end_tag)
        if start != -1 and end != -1:
            # Extract thinking block content
            thinking_block = content[start + len(start_tag):end].strip()
            # Remove the thinking block from the original content
            cleaned_content = (content[:start] + content[end + len(end_tag):]).strip()
            return cleaned_content, thinking_block
        else:
            # No thinking block found; return content as is and empty reasoning.
            return content, ""

    def _format_messages(self, messages):
        formatted = []
        for msg in messages:
            if isinstance(msg, SystemMessage):
                formatted.append({"role": "system", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted.append({"role": "assistant", "content": msg.content})
            elif isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
        return formatted
