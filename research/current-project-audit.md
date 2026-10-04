# 当前项目审计报告

对「校园学生智能体」当前实现的问题清单，按严重程度分级。每项给出：问题 → 根因 → 影响 → 推荐方案。

---

## Critical（必须解决）

### C1. "多智能体"是伪创新

- **问题**：`agents/` 下的 6 个领域智能体，本质是"keyword 路由 + 6 个不同 system prompt + 2 个特殊 agent（qa/RAG、academic/tool）"。LangGraph 状态图只是把 `if/else` 表达成图，节点间除了最终 `reply` 无信息流动。
- **根因**：把"Multi-Agent"当成创新卖点，而非为了解决真实问题。
- **影响**：答辩时经不起追问；文档中"多智能体协作"创新点被证伪；工作量看似多实则低价值。
- **推荐方案**：二选一——
  1. 诚实收敛为"意图路由 + 单次工作流"，删除 6 个伪 agent，用**配置驱动**（`intent → {system_prompt, needs_retrieval, needs_tool}`）表达；
  2. 参考 Campus-Asistant 做真正的 `supervisor → specialist（只取数）→ response_writer（统一成文）`，让"多智能体"有真实的职责分工与数据流。

### C2. RAG 是 naive RAG，无失败检测、无答案 grounding

- **问题**：`agents/qa.py` 的流程是"检索→重排→生成"，没有：
  - **检索相关性分级**（grade_documents）：不判断召回文档是否真相关；
  - **改写重试**（query rewrite）：检索无结果/不相关时不会改写问题重试；
  - **answer grounding**：没有强制"答案必须基于上下文，否则明说"的结构性约束。
- **根因**：把 RAG 当作"检索+拼接上下文"的线性管线。
- **影响**：检索不准时答案质量下降；检索空结果时 LLM 用空上下文作答，可能编造校园信息（与项目"不做编造"的立意直接冲突）。
- **推荐方案**：引入 LangGraph-Chatchat 的 agentic RAG 循环：`检索 → 相关性分级 → 相关则生成 / 不相关则改写重试 → 生成时强制 grounding`。

### C3. 无评测体系

- **问题**：`test_system.py` 只检查"意图标签 + HTTP 状态码 + 回复是否含某关键词"，是冒烟测试，不是质量评测。没有检索命中率、答案准确率、引用正确率、幻觉率等指标。
- **根因**：测试目标停留在"能不能跑通"，而非"答得好不好"。
- **影响**：无法回答项目立意的核心问题——"智能体是否真的降低了交互成本、比传统方案好"。
- **推荐方案**：建立校园问答评测集（query + 期望答案/关键词/引用）+ runner（意图匹配率 + 关键词命中率 + 时延），参考 Campus-Asistant 的 `eval/dataset.json` + `eval/runner.py`。

---

## Major（应当解决）

### M1. 无可观测性

- **问题**：无法 trace 一次完整 run（query → intent → retrieved docs → scores → tool calls → answer），无法定位 RAG 命中错误、tool 错误，无法统计 token/latency/tool_call/retrieval 指标。
- **影响**：出问题只能靠猜；无法在答辩中展示"检索到了什么、为什么这么答"。
- **推荐方案**：结构化运行日志（每次 run 记录关键中间态），或用 LangGraph 的 checkpoint/stream 输出节点级事件。

### M2. Tool 抽象弱

- **问题**：`services/tools.py` 是硬编码的 `TOOLS` 列表 + `call_tool` 里的 if/else 分发。没有统一 Tool 接口（name/description/schema/execute）、参数校验、权限边界、错误感知。
- **影响**：加一个工具要改多处；工具失败无法被 Agent 结构化感知。
- **推荐方案**：定义 `Tool` 抽象（Pydantic schema + execute），工具返回结构化结果（含 error 状态），Agent 能感知失败并降级或澄清。

### M3. RAG 与 Agent 强耦合

- **问题**：`agents/qa.py` 内嵌 embedding + 检索 + 重排 + 生成，检索管线无法独立评测与复用。
- **影响**：改检索策略要动 agent；评测检索质量很别扭。
- **推荐方案**：抽出独立的 `RetrievalService`（可独立喂评测集打分），agent 只做编排。

### M4. 无澄清机制

- **问题**：教务查询缺参数（如学号/班级）时直接返回 mock 数据，没有 ask-user 流程。
- **影响**：与"真实信息交互"的立意相悖；无法区分"数据可查"和"数据缺失需澄清"。
- **推荐方案**：tool 参数缺失时返回 `clarification_needed`，由响应层向用户澄清（参考 Campus-Asistant）。

### M5. 记忆薄弱

- **问题**：`study_plan`/`user_profile` 表已建但从未使用；实际只有近 10 条消息 + 标题生成。没有长期记忆、用户画像落地、对话摘要。
- **影响**：文档写了"记忆机制"创新点，但代码未落地。
- **推荐方案**：落地用户画像（专业/年级/偏好）与跨会话记忆，或明确从创新点中移除。

---

## Moderate（建议解决）

### Md1. 无 metadata 过滤

chunk 只有 `title`/`category`，无时间/来源/类别/版本等元数据，检索无法做过滤。

### Md2. 知识无时效/版本

校园通知有强时效性，但知识无 `publish_date`/`expire_date`/`version`，无法表达"这条已过时"。

### Md3. 引用粗粒度

只有【来源：title】，无页级/结构化 citation 返回给前端，无法验证"答案来自哪里"。

### Md4. query rewrite 缺失

多轮对话依赖原样历史，无语义改写；指代消解（"那周二呢"）能力弱。

### Md5. 错误处理基础

异常多数直接冒泡，无结构化 error context 让 agent 优雅降级或向用户解释。

---

## Minor（可暂缓）

- **Mi1.** 无 Docker 化部署（本地 venv 依赖较重）。
- **Mi2.** LangGraph 未使用 checkpointing（无断点/人工确认/人机协作）。
- **Mi3.** 前端为 CDN Vue，无构建、无 lint、无测试。
- **Mi4.** 配置无统一校验（settings 缺字段时不报错，运行时才炸）。

---

## 最终结论

> 如果这是我一个人、毕业设计周期有限的项目，我会不会推翻现在的架构？

**不会全盘推翻，但会做一次高杠杆的定向重构。**

| 动作 | 内容 |
| --- | --- |
| **保留** | FastAPI 分层骨架、LangGraph 编排（重做图内容）、混合检索+重排、SSE 流式、Vue3 前端、7 张表 DB 模型 |
| **删除** | 6 个"伪 agent"文件收敛为配置驱动的领域 prompt；删除"多智能体"作为创新点的表述 |
| **重构** | ① RAG → agentic RAG（分级+改写+grounding）；② Tool → 统一 schema + 错误/澄清；③ 检索与生成解耦；④ 加 metadata + 时效 |
| **新增** | ① 评测 harness + 校园问答数据集；② 可观测性（trace 一次 run）；③ 时效性 + 来源可信度；④ 澄清机制 |
| **暂缓** | MCP、插件 registry、checkpointing、Docker、多模型、GraphRAG、深度文档解析、plan-execute/reflexion 图 |

**核心理由**：项目缺的不是"技术堆料"，而是"证明它有效"和"结构可解释"。把 `agentic RAG 自校正 + 评测集 + 时效性 grounding` 做扎实，既直接服务"剩余交互成本"的立意，又能用指标证明"比 naive RAG 好"——这才是毕设真正的差异化。
