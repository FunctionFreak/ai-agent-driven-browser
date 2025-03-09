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
        # TODO: Replace the following simulated response with an actual API call to DeepSeek
        response = {
            "choices": [{
                "message": {
                    "content": "Simulated AI response content",
                    "reasoning_content": "Simulated reasoning details"
                }
            }]
        }
        content = response["choices"][0]["message"]["content"]
        reasoning_content = response["choices"][0]["message"]["reasoning_content"]
        return AIMessage(content=content, reasoning_content=reasoning_content)

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
