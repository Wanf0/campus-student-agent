# 参考资料

本文件记录研究过程中实际阅读的源码位置与引用的架构点，作为上述文档的证据来源。

## 已 clone 并阅读的仓库

- `Campus-Asistant`（https://github.com/mahdisundarani/Campus-Asistant）— clone 于 `/tmp/opencode/research-src/Campus-Asistant`
- `LangGraph-Chatchat`（https://github.com/chatchat-space/LangGraph-Chatchat）— clone 于 `/tmp/opencode/research-src/LangGraph-Chatchat`
- `Langchain-Chatchat`（https://github.com/chatchat-space/Langchain-Chatchat）— clone 于 `/tmp/opencode/research-src/Langchain-Chatchat`

## 关键源码位置（引用依据）

### Campus-Asistant

| 文件 | 引用的架构点 |
| --- | --- |
| `backend/graph.py` | Supervisor → Specialist → Response Writer → END 的图结构 |
| `backend/agents/state.py` | GraphState（query/history/intent/context/sources/response）共享状态 |
| `backend/agents/supervisor.py` | LLM 意图分类 + 确定性预判 + 校验兜底 |
| `backend/agents/response_writer.py` | gather/write 分离；clarification_needed 快路径；引用拼接 |
| `backend/agents/timetable_agent.py` | LLM 抽参 + 澄清门（缺 section 就问用户） |
| `backend/agents/rag_agent.py` | metadata 过滤（department/year/course）+ 页级来源 |
| `backend/rag/pipeline.py` | 解析→切分→嵌入→上传 的 ingest/search 管线 |
| `backend/rag/chunker.py` | RecursiveCharacterTextSplitter + metadata tags |
| `backend/rag/FLOW_EXPLAINED.md` | 混合检索 + FlashRank 重排的架构说明 |
| `backend/mcp_client.py` | MCP 作为统一工具抽象（stdio 子进程） |
| `backend/eval/dataset.json` | 评测集结构（query/expected_intent/expected_keywords） |
| `backend/eval/runner.py` | 意图匹配率 + 关键词命中率 + 时延统计 |

### LangGraph-Chatchat

| 文件 | 引用的架构点 |
| --- | --- |
| `chatchat/server/agent/graphs_factory/base_rag.py` | agentic RAG：grade_documents（相关性分级）+ rewrite（改写重试）+ generate（grounding） |
| `chatchat/server/agent/graphs_factory/graphs_registry.py` | graph 注册表（插件化）；State/Graph 基类；checkpoint；break_point/human_feedback |
| `chatchat/server/agent/graphs_factory/plan_and_execute.py` | Plan-and-Execute 状态机 |
| `chatchat/server/file_rag/retrievers/ensemble.py` | EnsembleRetriever：BM25(jieba) + 向量，按权重融合 |
| `chatchat/server/reranker/reranker.py` | FlagReranker / API 重排 |
| `chatchat/server/knowledge_base/kb_service/*` | 可插拔向量库后端（faiss/milvus/chromadb/es/pg/zilliz） |
| `chatchat/server/file_rag/text_splitter/*` | 中文专用切分（zh_title_enhance / chinese_recursive） |

### Langchain-Chatchat

| 结构 | 引用的架构点 |
| --- | --- |
| `libs/chatchat-server` | 服务端与 WebUI 分离；knowledge_base/kb_service 抽象 |
| `markdown_docs/` | 文档级架构说明 |

### 通过 README/文档核实（未 clone）

| 项目 | 核实的架构点 |
| --- | --- |
| FastGPT | App/Workflow/Plugin 概念；知识库 chunk 记录可改删；混合检索+重排；完整调用链路日志；应用评测；双向 MCP |
| Dify | App（chatbot/agent/chatflow/workflow）；RAG pipeline；Agent sandbox + 工具 + MCP；LLMOps 可观测（Langfuse/Phoenix/Opik）；annotation；evaluation |
| RAGFlow | 深度文档理解（OCR/版面/表格）；模板化切分；Agentic RAG（多步检索+证据校验）；grounded citations；多路召回+融合重排；Go 服务架构（API/Admin/Ingestor/Syncer） |

## 方法说明

- 优先读"调用链"和"数据流"（图定义、状态定义、节点间如何传数据），而非技术栈清单。
- 对每个项目回答：核心抽象是什么、请求从入口到回答经过什么路径、哪些由 LLM 决定/哪些由确定性程序决定、如何失败/调试/评测。
- 结论不因星标多而默认最佳，均以"是否解决校园场景真实问题 + 是否可验证"为准。
