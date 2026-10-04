"""记忆服务：对话标题生成、长对话摘要。"""

from app.infrastructure import llm


def generate_title(message: str) -> str:
    prompt = (
        "请为下面这条用户消息生成一个不超过 12 个字的简短标题，"
        "直接输出标题本身，不要加引号或其他说明：\n" + message
    )
    try:
        title = llm.chat([{"role": "user", "content": prompt}], temperature=0).strip()
        return title[:20] if title else message[:20]
    except Exception:
        return message[:20]


def summarize(history: list[dict]) -> str:
    if not history:
        return ""
    prompt = "请用一两句话概括下面这段对话的主要内容：\n" + "\n".join(
        f"{m['role']}: {m['content']}" for m in history
    )
    try:
        return llm.chat([{"role": "user", "content": prompt}], temperature=0).strip()
    except Exception:
        return ""
