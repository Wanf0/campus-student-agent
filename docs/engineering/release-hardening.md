# Release Hardening

本阶段将系统从"核心功能实现"提升到"关键路径经过真实失败测试 + 完整状态闭环"。

## 1. 真实 Tool Failure

- 新增 `UpstreamError`（`tools/base.py`），`Tool.run()` 将上游异常映射为 `ToolResult(status="error", error_message=...)`。
- 新增失败工具 `query_transcript`（成绩单查询，关键词"成绩单/学籍"），func 抛 `UpstreamError("教务系统暂时不可用，请稍后重试")`。
- Agent 的 error 分支将 `result.error_message`（用户友好）以 `error` 事件发射，`retryable=true`。

**完整链路**（实测）：

```
查成绩单 → tool_call(query_transcript, start)
         → tool_call(query_transcript, error)
         → error{message="教务系统暂时不可用，请稍后重试", retryable=true}
         → done{citations=0}
         → 前端 error state + 重试按钮
```

## 2. Clarification Context（conversation-level pending state）

- 新增 `domain/clarification.py`：`ClarificationStore`（内存单例，按 conversation_id），`PendingClarification{intent, pending_tool, missing_params}`。
- `router.py` 拆分 `route_keyword(msg) -> str|None`（纯关键词，无 LLM）。
- Agent `run_stream/run` 支持 `clarification` 参数：存在时强制 `intent` + `force_tool`。
- `orchestrator.resolve_pending`：存在 pending 且用户输入命中其它确定意图关键词 → 取消澄清，走普通路由；否则返回 pending。
- `orchestrator.update_pending`：有澄清则存，无澄清则清。

**验证**：

- `查课表 → clarification → A班 → query_timetable(ok) → 清 pending`（实测，A班课表正确返回）。
- `查课表 → clarification → 图书馆借书能借几本 → 取消澄清走 RAG`（实测）。

## 3. SSE Contract（含 latency）

事件 schema（`run_id` 贯穿 start/status/evidence/tool_call/clarification/token/error/done）：

```
{event: start, intent, run_id, conversation_id}
{event: status, phase, run_id}
{event: evidence, items[], run_id}
{event: tool_call, tool, status: start|ok|error|missing_params, missing?, run_id}
{event: clarification, missing[], question, tool, intent, run_id}
{event: token, content, run_id}
{event: error, message, retryable, run_id}
{event: done, citations[], run_id, latency_ms}
```

- `done` 事件注入 `latency_ms`（总耗时）。
- 前端 `TracePanel` 展示 run_id / 意图 / 阶段 / 工具 / 证据数 / 耗时。
- 未伪造 token_usage / retrieval 统计（后端未度量则不展示）。

## 4. E2E 验证（六场景 SSE 事件序列）

| 场景 | 输入 | 事件序列（实测） | 结果 |
| --- | --- | --- | --- |
| A 知识问答 | 国家奖学金要什么条件 | start(qa) → retrieving → evidence(1) → generating → done(citations=1) | ✅ |
| B 库外问题 | 今天股市大盘怎么样 | start(qa) → retrieving → rewriting×2 → evidence(0) → generating → done(citations=0) | ✅ 正确拒答 |
| C 工具查询 | 我的成绩是多少 | start(academic) → tool_calling → query_score ok → generating → done | ✅ |
| D 澄清 | 查课表 → A班 | D1: missing_params → clarification；D2: query_timetable ok → generating | ✅ 真实续接 |
| E 工具失败 | 查成绩单 | query_transcript start→error → error(retryable) → done | ✅ |
| F 流中断 | —（前端） | 前端 catch → error state + 重试（store/SSE 单测覆盖） | ⚠️ 单元测试覆盖，未真实断网模拟 |

## 5. 测试与回归

- 后端：`test_system.py` 19/19，`test_hardening.py` 5/5（tool failure / store / 续接 / 放弃 / latency）。
- 前端：Vitest 23/23（新增 TracePanel 3 项 + latency 断言）；`vue-tsc --noEmit` 通过；`vite build` 成功。

## 6. 已知限制

1. `ClarificationStore` 为**内存单例**，进程重启后 pending 丢失（单进程演示足够；多进程需 DB 持久化）。
2. 澄清续接依赖 **LLM 从历史上下文提取参数**（强制工具 + history）；对"自由输入非 A/B 班"的通用参数填充未做确定性兜底。
3. 场景 F（流中断）仅由单元测试覆盖，未做真实断网的浏览器验证。
4. `query_transcript` 为纯演示失败工具，真实上游失败需接入真实教务接口。
5. 澄清"取消"依赖用户输入命中其它确定意图关键词；若用户输入非关键词的中性新话题，仍会被当作参数补充尝试。
