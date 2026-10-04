"""工具模块：构建默认工具注册表。"""

from app.domain.tools.base import Tool
from app.domain.tools.knowledge_tool import build_knowledge_tool
from app.domain.tools.read_tools import build_read_tools
from app.domain.tools.registry import ToolRegistry


def build_registry() -> ToolRegistry:
    reg = ToolRegistry()
    for t in build_read_tools():
        reg.register(t)
    reg.register(build_knowledge_tool())
    return reg
