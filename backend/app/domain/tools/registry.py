"""Tool 注册表。"""

from app.domain.entities import ToolResult
from app.domain.tools.base import Tool


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def all(self) -> list[Tool]:
        return list(self._tools.values())

    def schemas(self, category: str | None = None) -> list[dict]:
        """返回给 LLM 的工具 schema（默认只暴露 read/knowledge 类）。"""
        out = []
        for t in self._tools.values():
            if category is not None and t.category != category:
                continue
            if t.category in ("read", "knowledge"):
                out.append(t.to_openai_schema())
        return out

    def call(self, name: str, args: dict | None = None, *, confirmed: bool = False) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(status="error", error_message=f"未知工具: {name}")
        if tool.permission == "needs_confirm" and not confirmed:
            return ToolResult(status="error", error_message="该操作需要用户确认")
        return tool.run(args)
