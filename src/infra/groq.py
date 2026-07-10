import os
from dataclasses import dataclass

from groq import Groq

from src.core.llm import AgentMessage, llmProvider, GroqResponse


class GroqProvider(llmProvider):
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        self.client = Groq(api_key=api_key)
        self.model = model
        self.call_count = 0

    def generate(self, messages: list) -> GroqResponse:
        self.call_count += 1
        formatted = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=formatted,
            temperature=0.7,
        )
        content = response.choices[0].message.content
        return GroqResponse(content=content)






