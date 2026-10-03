"""教务信息查询智能体：通过工具调用（Function Calling）查询课表、成绩、考试。"""

import json

from ..config import settings
from ..services import llm, tools

SYSTEM_PROMPT = "你是教务信息查询助手。当用户查询课表、成绩或考试安排时，请调用相应工具获取数据，再整理为自然语言回答。"


def prepare(message: str, history: list[dict] | None = None) -> list[dict]:
    """执行工具调用流程，返回用于最终生成的 messages。"""
    client = llm.get_client()
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    resp = client.chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
        tools=tools.TOOLS,
        tool_choice="auto",
    )
    msg = resp.choices[0].message

    if msg.tool_calls:
        messages.append(msg)
        for tc in msg.tool_calls:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = tools.call_tool(tc.function.name, args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": result})
    return messages


def handle(message: str, history: list[dict] | None = None) -> str:
    messages = prepare(message, history)
    final = llm.get_client().chat.completions.create(
        model=settings.deepseek_model,
        messages=messages,
    )
    return final.choices[0].message.content or ""


def handle_stream(message: str, history: list[dict] | None = None):
    messages = prepare(message, history)
    yield from llm.chat_stream(messages)
