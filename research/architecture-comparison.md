# 架构横向对比

对 6 个参考项目与当前项目做架构级横向对比。重点看"调用链"与"数据流"，而非技术栈罗列。

## 总体对比表

| 项目 | 语言/栈 | 核心抽象 | Agent 编排 | Workflow | RAG 检索 | Tool | Memory | Evaluation | Observability | 最值得借鉴的设计 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **当前项目** | Python/FastAPI | 意图路由 + 领域智能体 | LangGraph（单层路由） | 无（单次工作流） | 向量+BM25+重排（naive） | 硬编码 dict + if/else | 近10条消息 + 标题生成 | 冒烟测试（意图+状态码） | 无 | — |
| **Campus-Asistant** | Python/LangGraph | Supervisor→Specialist→ResponseWriter | LangGraph 状态图 | 单次，但有澄清分支 | FAISS+BM25+FlashRank，页级引用+metadata过滤 | MCP servers（统一抽象） | 会话历史 | dataset.json + runner（意图+关键词+时延） | print 日志 | 澄清机制、gather/write 分离、评测 harness |
| **LangGraph-Chatchat** | Python/LangGraph | Graph 注册表（插件化） | 多图（base_rag/plan_execute/reflexion） | agentic RAG 自校正循环 | Ensemble(BM25+向量)+rerank，可插拔向量库 | tools_factory 注册表 | history_manager（过滤+限长） | 无独立 eval（靠 UI 测试） | 日志 + checkpoint | agentic RAG（grade→rewrite）、graph registry |
| **Langchain-Chatchat** | Python/FastAPI | 服务端 + WebUI 分离 | ReAct agent | 基础 RAG | 多向量库后端 + 多 loader + 中文切分 | tools_factory | 对话记忆 | 无 | 日志 | 知识库服务抽象（kb_service）、中文切分 |
| **FastGPT** | Node/Next.js | App/Workflow/Plugin | Agent + 工作流 | 可视化 Flow | 混合检索+重排，chunk 可改删 | 插件 + 双向 MCP | 会话 | 应用评测 + 知识库单点测试 | 完整调用链路日志 | chunk 记录管理、调用链路日志、评测 |
| **Dify** | Python/Flask + Next.js | App（chatbot/agent/workflow） | Agent sandbox + 工具 | 可视化 workflow | RAG pipeline | 工具 + MCP + marketplace | 会话变量 | 标注 + evaluation | LLMOps（Langfuse/Phoenix/Opik） | LLMOps 可观测、annotation、评测 |
| **RAGFlow** | Go + Python | 文档理解 + Agent | Agentic RAG（多步检索+证据校验） | 深度文档解析管线 | 多路召回 + 融合重排 | Agent + MCP + Sandbox | — | 无（工程性） | 引用可追踪 | agentic retrieval、grounded citations、模板化切分 |

## 关键差异（调用链层面）

### 当前项目：单次、无自校正、无评测

```
User Input → API → 意图路由(keyword/LLM) → 领域智能体
   ├─ qa: 检索→重排→生成（无相关性校验、无改写）
   ├─ academic: LLM 抽参→工具→生成（无澄清、无校验）
   └─ 其余: 直接 LLM（不同 prompt）
→ 返回 answer（无结构化 citation、无 trace）
```

特点：**一次向前，永不回头**。检索不准就直接生成；工具缺参就用 mock；没有"这次结果好不好"的判断。

### 成熟项目：有校验、有回溯、有评测

LangGraph-Chatchat 的 base_rag 是一个**带回路的图**：

```
history_manager → chatbot(agent 决定是否检索) → retrieve → grade_documents
   ├─ relevant → generate → END
   └─ not relevant → rewrite(query) → 回到 chatbot 重试
```

Campus-Asistant 是**gather/write 分离 + 澄清**：

```
supervisor(意图) → specialist(只取数，写 context/sources)
   └─ 缺参 → clarification_needed（response_writer 直接问用户）
→ response_writer(统一组织 Markdown + 引用) → END
```

## 可迁移到校园场景的设计（按性价比）

| 设计 | 来源 | 迁移价值 | 成本 |
| --- | --- | --- | --- |
| agentic RAG（grade→rewrite→grounding） | LangGraph-Chatchat | 直接降低幻觉、提高答案质量 | 中 |
| gather/write 分离 + 澄清机制 | Campus-Asistant | 结构清晰 + 事务闭环 | 中 |
| 评测数据集 + runner | Campus-Asistant | 证明"比 naive RAG 好"的关键 | 低 |
| chunk metadata + 过滤 + 页级引用 | Campus-Asistant/RAGFlow | 时效性 + 可信度 | 低 |
| 调用链日志 | FastGPT/Dify | 可定位问题 | 中 |
| 知识库服务抽象（可插拔） | Langchain-Chatchat | 便于替换后端 | 中 |

## 明显过度复杂、不建议迁移（对个人毕设）

| 设计 | 来源 | 为何过度 |
| --- | --- | --- |
| GraphRAG / 知识图谱 | RAGFlow | 工程量大，校园知识量级用不上 |
| 可视化 workflow 引擎 | FastGPT/Dify | 需要前端编排器，远超毕设范围 |
| MCP 全量接入 | Campus-Asistant/Dify | 一套 stdio 子进程管理，复杂度高，收益有限 |
| LLMOps 平台（Langfuse/Phoenix） | Dify | 需额外部署，可用轻量日志替代 |
| 深度文档解析（OCR/版面/表格） | RAGFlow | 校园文档多为可提取 PDF，OCR 是边际需求 |
| plugin registry 热更新 | FastGPT/LangGraph-Chatchat | 动态插件系统，个人项目无需 |

## 甚至可能比当前项目更差的地方

| 项目 | 潜在问题 |
| --- | --- |
| Campus-Asistant | 每个 specialist 内部硬编码 LLM 抽参（无统一 tool schema），抽参失败静默降级；print 日志无结构化 |
| LangGraph-Chatchat | 历史管理依赖 ToolMessage 手动追加，注释里自己承认"需要再研究"，存在 fragile 点 |
| Langchain-Chatchat | 老代码库，服务端与 WebUI 耦合历史包袱较重 |

结论：**不要因为星标多就默认最佳**；对个人毕设，最值得抄的是"agentic RAG 自校正 + 评测 + 澄清"，而非大平台的工程底座。
