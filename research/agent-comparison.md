# Agent 架构对比

对比三种多智能体组织方式，说明当前项目属于哪一种、真正该用哪一种。

## 三种模式

### 模式 1：伪多智能体 = 意图路由 + N 个 Prompt（当前项目）

```
route(keyword/LLM) → agent_i（每个 agent 就是一个 system prompt + 一次 LLM 调用）
```

- 6 个"agent"之间没有协作、没有对话、没有信息交换。
- "智能体"没有决策能力，只是"换了 prompt 的同一个 LLM 调用"。
- 特殊的两类（qa 走 RAG、academic 走 tool）只是多了预处理步骤。

**判定**：这是"为了 Agent 而 Agent"。工作量看似多，创新价值低。

### 模式 2：Supervisor → Specialist → Response Writer（Campus-Asistant）

```
supervisor(意图分类) → specialist(只取数，写 context/sources)
                      → response_writer(统一组织 Markdown + 引用)
```

- **gather 与 write 分离**：specialist 只负责"取到数据/检索到文档"，不写最终答案；response_writer 统一成文。
- **有真实数据流**：`context`/`sources` 作为共享状态在节点间流动。
- **澄清机制**：specialist 缺参数时写 `clarification_needed`，response_writer 直接问用户。

来源证据：Campus-Asistant `backend/graph.py`（Supervisor → RAG/Timetable/Planner/Notices → Response Writer → END）、`agents/response_writer.py`（读 context/sources 统一生成）。

### 模式 3：Graph Registry（LangGraph-Chatchat）

```
多种图（base_rag / plan_and_execute / reflexion / text_to_sql）以插件注册，按需加载
```

- 每种图是一套完整的 agent 工作流（而非一个"领域"）。
- 用注册表组织，扩展 = 新增一个 graph 类。
- 适合"多种不同任务形态"的场景（RAG、SQL、规划、反思）。

来源证据：`chatchat/server/agent/graphs_factory/graphs_registry.py` 的 `register_graph` 装饰器 + `rag_registry`/`agent_registry`。

## 对比表

| 维度 | 伪多智能体（当前） | Supervisor/Specialist（推荐） | Graph Registry |
| --- | --- | --- | --- |
| 是否有真实分工 | 否（同质 prompt） | 是（取数 vs 成文） | 是（不同工作流） |
| 节点间数据流 | 无（只有 reply） | 有（context/sources） | 有（state） |
| 澄清能力 | 无 | 有 | 有（可自定义） |
| 复杂度 | 低 | 中 | 中高 |
| 适配场景 | — | 校园多领域问答 | 多任务形态 |

## 结论

- 当前项目应**放弃"伪多智能体"表述**。
- 如果确实需要多智能体，采用 **Supervisor/Specialist/ResponseWriter** 模式（gather/write 分离 + 澄清），它给"多智能体"提供了**真实的分工与数据流**，也直接服务"事务闭环"的立意。
- Graph Registry 对个人毕设偏重，仅当需要"多种任务形态"时再考虑。
- 单智能体 + 工作流（当前 agentic RAG 即此形态）在很多场景已足够，**不要为了"多"而多**。
