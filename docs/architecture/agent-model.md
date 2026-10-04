# Agent Model

## 定位

单一 Agent + 确定性路由 + 工作流。Agent 通过工具调用获得能力，不做"万能的巨型决策者"。

## Agent 的 8 问

1. **负责什么**：在给定工具集与上下文中，理解用户意图、规划步骤、调用工具、整合证据、生成有依据的回答。
2. **输入**：query + history + 可用工具 schema + 用户画像。
3. **输出**：`answer + evidence[] + citations[]`（结构化）。
4. **可调用工具**：
   - `search_knowledge`（Knowledge，走权威感知 RAG 管线）
   - `query_timetable / query_score / query_exam / query_notice / query_calendar`（Read）
5. **启动条件**：任意用户请求进入对话。
6. **结束条件**：产出最终回答 / 触发澄清 / 达步数或 token 上限。
7. **失败处理**：
   - 工具失败 → 结构化错误 → 降级说明"无法获取"
   - 检索失败 → 改写重试(≤N) → 仍失败则明说"不确定，建议人工确认"
   - LLM 输出非法 → 校验后重试/兜底
8. **测试方式**：routing / tool-calling / answer / citation / hallucination 五类评测。

## 职责边界

| 责任 | Agent(LLM) | 确定性程序 |
| --- | --- | --- |
| 意图理解 | ✅ | 规则兜底 |
| 参数校验 | ❌ | ✅ |
| 工具选择 | ✅（schema 内） | ❌ |
| 权限控制 | ❌ | ✅ |
| 时效过滤/权威加权 | ❌ | ✅（检索层） |
| 证据整合 | ✅ | ❌ |
| grounding 约束 | 生成时遵守 | 结构性校验 |
| 事务/安全 | ❌ | ✅ |

## 与"多智能体"的关系

本设计**不是**多智能体。它是：

- 单一 reasoning Agent，通过**工具**扩展能力（RAG 是工具、教务查询是工具）；
- 用**工作流**表达复杂流程（agentic RAG 的"检索→分级→改写→生成"循环）；
- 用**确定性路由**替代 LLM 分类做意图分发。

这样避免"为了 Agent 而 Agent"，同时保留 Agent 真正的价值：在明确边界内做规划与工具调用。
