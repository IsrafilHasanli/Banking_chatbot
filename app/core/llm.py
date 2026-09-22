from app.core.config import settings
from langchain_anthropic import ChatAnthropic


def get_llm():
    return ChatAnthropic(
        api_key=settings.CLAUDE_API_KEY,
        model=settings.CLAUDE_MODEL,
        temperature=0,
    )
