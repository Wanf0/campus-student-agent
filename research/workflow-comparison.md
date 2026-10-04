# Workflow 编排对比

对比工作流编排的几种形态，说明当前项目用的是哪种、何时该升级。

## 形态对比

### 1. 线性路由（当前项目）

```
if/else 路由 → 单次执行 → 返回
```

- 用 LangGraph 表达，但本质是 `route → 一个领域节点 → END`。
- 无循环、无重试、无分支合并、无状态回溯。
- 优点：简单、可预测；缺点：无法处理"结果不好重来"的场景。

### 2. 带回路的图（LangGraph-Chatchat 的 agentic RAG）

```
chatbot → retrieve → grade → {generate | rewrite → 回到 chatbot}
```

- **有循环**：检索不相关则改写重试（需设上限防死循环）。
- 状态在节点间累积（messages/history）。
- 这本质上是"条件回边"，是 RAG 质量自校正的基础。

### 3. Plan-and-Execute（LangGraph-Chatchat）

```
planner(生成 step 列表) → 逐个 execute → 汇总 response
```

- 把复杂任务拆成有序步骤，逐步执行。
- 适合"多步、需要规划"的任务（如"帮我规划这周复习"）。

来源证据：`chatchat/server/agent/graphs_factory/plan_and_execute.py`（`Plan{steps[]}` / `Act{Response|Plan}` / `past_steps` 状态）。

### 4. Reflexion（LangGraph-Chatchat）

- 生成 → 自我反思评价 → 不满意则修正重试。
- 适合"答案质量要求高、可自我评判"的任务。

### 5. 可视化 Flow（FastGPT / Dify）

- 用户在前端画节点图，后端按图执行。
- 工程量大（需编排器 + 节点引擎），对个人毕设过度。

## 对比表

| 形态 | 是否循环 | 复杂度 | 适配场景 | 当前是否需要 |
| --- | --- | --- | --- | --- |
| 线性路由 | 否 | 低 | 简单问答/查询 | 现状（可保留用于工具类） |
| 带回路的图（agentic RAG） | 是 | 中 | RAG 问答质量自校正 | **需要** |
| Plan-and-Execute | 是 | 中高 | 学习规划等多步任务 | 可选 |
| Reflexion | 是 | 中高 | 答案可自评的任务 | 暂缓 |
| 可视化 Flow | 是 | 高 | 产品化 | 不需要 |

## 结论

- 当前项目的 LangGraph 是"空转"——用了图但没有利用图的价值（循环、回边、状态累积）。
- **最低成本的升级**：给 RAG 图加一条"grade → rewrite → 重试"的回边，让它成为真正的 agentic RAG 循环。这一步就把"用了 LangGraph"变成"用对了 LangGraph"。
- Plan-and-Execute 可作为"学习规划"模块的进阶方向，但不是优先级最高的。
