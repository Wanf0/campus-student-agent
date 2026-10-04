# Tool Architecture

统一工具抽象，四类工具，权限策略，澄清机制。

## Tool 抽象

```python
class Tool(BaseModel):
    name: str
    description: str
    category: Literal["read", "write", "external", "knowledge"]
    input_schema: dict            # JSON Schema
    permission: Literal["read_only", "needs_confirm"]
    timeout: float                # 秒
    retry: int
    async def execute(self, args: dict) -> ToolResult: ...
    def map_error(self, e: Exception) -> ToolResult: ...
```

## ToolResult（统一结果）

```python
class ToolResult(BaseModel):
    status: Literal["ok", "error", "missing_params"]
    data: Any = None              # ok 时的结构化结果
    missing_params: list[str] = []  # missing_params 时列出缺失项
    error_message: str | None = None
    evidence: list[Evidence] = []  # knowledge 类工具携带证据
```

## 四类工具

| 类别 | 例子 | 权限 | 副作用 |
| --- | --- | --- | --- |
| Read | query_timetable/score/exam/notice/calendar | read_only | 无 |
| Write | 退选课、报名 | needs_confirm | 有 |
| External | 外部接口（如真实教务系统） | read_only/needs_confirm | 视情况 |
| Knowledge | search_knowledge | read_only | 无 |

**原则**：查询类与写操作类**绝不能**有相同信任级别；Write 类默认需用户确认。

## 注册表（Registry）

```python
class ToolRegistry:
    def register(self, tool: Tool) -> None: ...
    def get(self, name: str) -> Tool: ...
    def schemas(self, category=None) -> list[dict]:  # 给 LLM 的 tool schema
    def dispatch(self, name, args, *, confirmed=False) -> ToolResult: ...
```

## 澄清机制

1. `execute` 发现必需参数缺失 → 返回 `status=missing_params` + `missing_params`。
2. Application 层捕获 → 触发澄清流程（问用户补参数）。
3. 用户补充后重新调用（携带已确认参数）。

本阶段只实现 Read 与 Knowledge 类；Write 类定义抽象与权限策略，不实现具体工具。

## 与 Agent 的关系

Agent 不直接"知道"工具的副作用或权限。它只看到工具的 schema（name/description/input_schema/category 的 read/knowledge 部分）。权限校验、确认流程、参数校验全部由确定性程序（Tool 抽象 + Application）负责——LLM 决策始终在明确边界内。
