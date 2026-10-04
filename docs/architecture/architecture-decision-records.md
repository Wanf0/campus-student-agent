# Architecture Decision Records

## ADR-1：单一 Agent + 确定性路由 + 工作流，删除伪多智能体

- **状态**：Accepted
- **背景**：现状 6 个领域 agent 本质是 keyword 路由 + 6 个不同 system prompt，节点间无数据流，是伪多智能体。
- **决策**：收敛为单一 Agent，通过工具调用获得能力；路由由确定性规则 + LLM 兜底完成；复杂流程用工作流编排。
- **影响**：删除 `agents/` 下 6 个伪 agent；文档中"多智能体协作"创新点表述需同步修改。

## ADR-2：RAG 作为 Knowledge Tool，而非内嵌在 Agent 里

- **状态**：Accepted
- **背景**：现状 `qa.py` 内嵌 embedding + 检索 + 重排 + 生成，检索管线无法独立评测。
- **决策**：检索管线抽为独立服务，以 Tool 形式暴露给 Agent 调用。
- **影响**：检索可独立评测（recall/precision）；Agent 通过统一工具接口获得检索能力。

## ADR-3：Agentic RAG 自校正（检索→分级→改写重试→grounding）

- **状态**：Accepted
- **背景**：naive RAG 检索不准时答案质量差甚至编造。
- **决策**：检索后做相关性分级；不相关则改写问题重试（有上限）；生成阶段强制 evidence grounding。
- **影响**：LangGraph 循环图真正产生收益；需设重试上限与预算防死循环。

## ADR-4：Tool 四类 + 权限策略，副作用默认需确认

- **状态**：Accepted
- **背景**：查询与退选课等副作用操作不能有相同信任级别。
- **决策**：Tool 分为 Read / Write / External / Knowledge 四类；Write 类默认需用户确认。
- **影响**：本阶段只实现 Read 与 Knowledge 类；Write 类定义抽象与权限策略，不实现具体工具。

## ADR-5：Knowledge 引入时间/来源/版本/院系/类型/权威/生效/适用范围元数据

- **状态**：Accepted
- **背景**：校园知识强时效、强权威，"2026 选课规定"不能被当作"2024 选课规定"的相似文本。
- **决策**：chunk 继承文档元数据：source_authority、publish_date、effective_from/to、version、department、doc_type、scope。
- **影响**：检索支持时效过滤与权威加权；这是核心创新（时间有效性 + 来源权威性）的落地基础。

## ADR-6：answer + evidence + citation + trace 结构化返回

- **状态**：Accepted
- **背景**：现状只有纯文本 answer，无法回答"为什么这么答"。
- **决策**：返回结构化结果，含 evidence（来源/权威/时间/得分）与 citation，前端可展示依据。
- **影响**：实现证据一致性（核心创新第三支柱）与可观测。

## ADR-7：每次 run 生成 run_id + 完整 trace

- **状态**：Accepted
- **背景**：现状无观测，出问题无法反推是 Router/Retrieval/Tool/LLM 哪一环错。
- **决策**：每次请求生成 run_id，记录 request/route/model/prompt/retrieval/docs/tool_calls/latency/token/errors/final_answer。
- **影响**：trace 落 SQLite 表，提供结构化观测。

## ADR-8：Evaluation-first，先打 Before 基线再重构

- **状态**：Accepted
- **背景**：无评测则无法证明重构有效。
- **决策**：先建评测集并给现状打 Before 基线，重构后打 After，用指标对比。
- **影响**：这是验证体系，不作为创新点本身。

## ADR-9：SQLite + SQLAlchemy 抽象不变，trace/evidence 落 SQLite

- **状态**：Accepted
- **背景**：保持零配置可跑。
- **决策**：沿用 SQLAlchemy，trace/evidence 新增表落 SQLite，MySQL 可无缝切换。

## ADR-10：前端只展示真实运行状态，禁止伪造思考过程

- **状态**：Accepted
- **背景**：前端应工程化，但不能为"展示 Agent 很厉害"而造假。
- **决策**：只展示真实 tool 执行状态、真实引用、真实错误/重试。（P6 阶段实施）
