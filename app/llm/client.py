import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

class LMStudioClient:
    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = 0.4,
    ):
        load_dotenv()
        model = model or os.getenv("LM_STUDIO_MODEL", "qwen2.5-7b-instruct-1m")
        base_url = base_url or os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.llm = ChatOpenAI(
            model=model,
            base_url=base_url,
            api_key="lm-studio",
            temperature=temperature,
        )

    def run(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)
        return response.content.strip()
