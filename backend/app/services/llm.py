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


def chat_stream(messages: list[dict], temperature: float = 0.7):
    """流式返回生成内容（逐段 yield）。"""
    client = get_client()
    stream = client.chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
        temperature=temperature,
        stream=True,
    )
    for chunk in stream:
        if chunk.choices:
            delta = chunk.choices[0].delta
            if delta and delta.content:
                yield delta.content
