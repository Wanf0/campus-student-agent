# Target Architecture

面向校园时效性知识的权威感知 Agentic RAG —— 目标架构。

## 核心贡献（一句话）

> 利用**来源权威性**、**时间有效性**与**证据一致性**约束智能体的检索与生成过程，并通过评测集验证其相较于传统 RAG 的 grounding 能力。

## 分层边界

```
┌─ Presentation ────────────────────────────────┐
│  Vue3：流式、引用展示、tool 状态、错误/重试     │
└──────────────────┬────────────────────────────┘
                   │ HTTP / SSE
┌─ API ─────────────────────────────────────────┐
│  FastAPI routers：只做协议转换、鉴权、参数解析  │
└──────────────────┬────────────────────────────┘
                   │
┌─ Application ─────────────────────────────────┐
│  编排器：run 生命周期、trace 组装、澄清流程     │
│  (Router → Agent/Workflow → Grounding → Trace) │
└──────────────────┬────────────────────────────┘
                   │
┌─ Domain ──────────────────────────────────────┐
│  Router 规则、Agent、Workflow、RAG 管线、      │
│  Tool 抽象/Registry、Grounding、Citation、     │
│  Knowledge(时效/权威)                          │
└──────────────────┬────────────────────────────┘
                   │
┌─ Infrastructure ──────────────────────────────┐
│  LLM client、Embedding、Reranker、VectorStore、 │
│  DB(SQLAlchemy)、Observability(trace/log)      │
└────────────────────────────────────────────────┘
```

## 组件边界归属

| 组件 | 边界 | 说明 |
| --- | --- | --- |
| LLM | Infrastructure | 只做模型适配，不掺杂业务 |
| Retriever | Domain + Infra | 编排在 Domain，向量/BM25 在 Infra |
| Agent | Domain | 单一 reasoning 循环，通过 tool 获得能力 |
| Workflow | Application | 编排 Agent/RAG/Tool 的组合 |
| Tool | Domain(定义/注册) + Infra(执行) | 统一抽象 |
| Memory | Domain + Infra(DB) | 画像/历史/摘要 |
| Knowledge | Domain(元数据) + Infra(存储) | 时效/权威/版本 |
| Database | Infrastructure | SQLAlchemy |
| Observability | Infrastructure（横切） | run_id/trace |
| Evaluation | 独立目录 `evaluation/` | 测试资产，非运行时 |

## 职责划分原则

**确定性程序负责**：权限、参数校验、状态机、数据一致性、tool schema、安全限制、业务规则、事务边界、时效过滤、权威加权、重试上限。

**LLM 负责**：语言理解、模糊意图识别、任务规划、信息整合、自然语言生成、在明确边界内进行决策。

## 核心设计（相对现状的变化）

| 现状 | 目标 |
| --- | --- |
| 6 个伪 Agent（keyword 路由 + prompt） | 单一 Agent + 确定性路由 + 工作流 |
| naive RAG（检索→生成） | Agentic RAG（检索→分级→改写→grounding→citation） |
| RAG 内嵌在 qa agent | RAG 作为 Knowledge Tool，可独立评测 |
| 硬编码 tool + if/else | 统一 Tool 抽象（4 类 + 权限 + 澄清） |
| answer 纯文本 | answer + evidence + citation + trace |
| 无观测 | run_id + 完整 trace |
| 冒烟测试 | 评测集 + Before/After 指标 |

## 目标目录结构（P1 之后）

```
backend/app/
├── api/            # FastAPI routers（协议转换）
├── application/    # 编排器、run 生命周期、trace
├── domain/         # router、agent、workflow、rag、tool、grounding、citation、knowledge
└── infrastructure/ # llm、embedding、reranker、vectorstore、db、observability
```
