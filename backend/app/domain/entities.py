"""领域对象（Pydantic）：Evidence、ToolResult 等。"""

from typing import Any, Literal

from pydantic import BaseModel


class Evidence(BaseModel):
    """支撑回答的证据片段。"""
    text: str
    source_title: str
    source_authority: int
    publish_date: str | None = None
    effective_from: str | None = None
    effective_to: str | None = None
    version: str | None = None
    department: str | None = None
    doc_type: str = "其他"
    retrieval_score: float | None = None
    rerank_score: float | None = None

    @property
    def authority_label(self) -> str:
        return {4: "校级", 3: "院级", 2: "部门", 1: "未知"}.get(self.source_authority, "未知")


class Citation(BaseModel):
    """返回前端的引用。"""
    title: str
    authority: str
    publish_date: str | None = None


class ToolResult(BaseModel):
    """统一工具执行结果。"""
    status: Literal["ok", "error", "missing_params"]
    data: Any = None
    missing_params: list[str] = []
    error_message: str | None = None
    evidence: list[Evidence] = []


class AgentOutput(BaseModel):
    """单一 Agent 的最终输出。"""
    answer: str
    evidence: list[Evidence] = []
    citations: list[Citation] = []
    intent: str = "general"
    clarification: dict | None = None
    error: str | None = None
    retryable: bool = False
