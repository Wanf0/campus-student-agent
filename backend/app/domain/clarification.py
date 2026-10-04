"""澄清状态：conversation-level pending task / clarification state。

用于让澄清后的短回复（如"A班"）被解析为对 pending 工具的参数补充，
而不是重新进入普通路由。当前为内存单例（单进程演示），可替换为 DB 持久化。
"""

from dataclasses import dataclass, field


@dataclass
class PendingClarification:
    intent: str
    pending_tool: str
    missing_params: list[str] = field(default_factory=list)


class ClarificationStore:
    def __init__(self):
        self._pending: dict[int, PendingClarification] = {}

    def set(self, conversation_id: int, pending: PendingClarification) -> None:
        self._pending[conversation_id] = pending

    def get(self, conversation_id: int) -> PendingClarification | None:
        return self._pending.get(conversation_id)

    def clear(self, conversation_id: int) -> None:
        self._pending.pop(conversation_id, None)


clarification_store = ClarificationStore()
