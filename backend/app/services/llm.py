from openai import OpenAI

from ..config import settings

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
        )
    return _client


def chat(messages: list[dict], temperature: float = 0.7) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content or ""
