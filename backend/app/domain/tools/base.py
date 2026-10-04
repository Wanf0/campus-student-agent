"""Tool 统一抽象。"""

from typing import Any, Callable, Literal

from app.domain.entities import ToolResult


class MissingParamsError(Exception):
    def __init__(self, params: list[str]):
        self.params = params
        super().__init__(f"缺少参数: {params}")


class Tool:
    """统一工具抽象。"""

    def __init__(
        self,
        name: str,
        description: str,
        category: Literal["read", "write", "external", "knowledge"],
        permission: Literal["read_only", "needs_confirm"],
        input_schema: dict,
        func: Callable[[dict], Any],
    ):
        self.name = name
        self.description = description
        self.category = category
        self.permission = permission
        self.input_schema = input_schema
        self._func = func

    def run(self, args: dict | None = None) -> ToolResult:
        args = args or {}
        try:
            data = self._func(args)
            return ToolResult(status="ok", data=data)
        except MissingParamsError as e:
            return ToolResult(status="missing_params", missing_params=e.params)
        except Exception as e:
            return ToolResult(status="error", error_message=str(e))

    def to_openai_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema,
            },
        }
