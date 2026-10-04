# 校园学生智能体 — 架构审计与开源调研

本目录是对「校园学生智能体」项目的一次完整架构审计与开源项目横向调研的产物。

## 背景

项目立意：

> 校园已经高度数字化，但"信息存在"并不等于"低成本可理解、可获取、可执行"。
> 智能体是否能够降低学生与校园复杂信息系统之间剩余的交互成本？

当前技术路线：DeepSeek + FastAPI + LangGraph + Chroma（混合检索 + 重排）+ SQLite/MySQL + Vue3，功能覆盖校园问答、学习辅导、教务查询、生活服务、心理陪伴、学习规划、知识库管理等。

## 研究范围

深度阅读（clone 源码）的项目：

- [Campus-Asistant](https://github.com/mahdisundarani/Campus-Asistant) — 直接可比的校园智能体
- [LangGraph-Chatchat](https://github.com/chatchat-space/LangGraph-Chatchat) — LangGraph 版 RAG/Agent 平台
- [Langchain-Chatchat](https://github.com/chatchat-space/Langchain-Chatchat) — 经典 RAG 问答平台

通过文档核实的项目：

- [FastGPT](https://github.com/labring/FastGPT) — 知识库问答产品
- [Dify](https://github.com/langgenius/dify) — LLM 应用平台
- [RAGFlow](https://github.com/infiniflow/ragflow) — 深度文档理解 RAG 引擎

## 文档索引

| 文件 | 内容 |
| --- | --- |
| [architecture-comparison.md](./architecture-comparison.md) | 6 项目横向架构对比表 |
| [current-project-audit.md](./current-project-audit.md) | 当前项目问题清单（Critical/Major/Moderate/Minor） |
| [rag-comparison.md](./rag-comparison.md) | naive / hybrid / agentic RAG 对比 |
| [agent-comparison.md](./agent-comparison.md) | 多智能体架构模式对比 |
| [workflow-comparison.md](./workflow-comparison.md) | 工作流编排模式对比 |
| [engineering-comparison.md](./engineering-comparison.md) | 工程实践（评测/可观测/错误处理/配置）对比 |
| [innovation-candidates.md](./innovation-candidates.md) | 候选创新方向 |
| [references.md](./references.md) | 参考源码位置与引用的架构点 |

## 核心结论（摘要）

1. **当前项目不缺技术堆料，缺的是"证明它有效"和"结构可解释"。**
2. 最该做的是：**Agentic RAG 自校正（检索相关性分级 + 改写重试 + 答案 grounding）+ 评测集 + 时效性 grounding**，而不是再加 Agent/向量库/模型。
3. "多智能体"目前是伪创新（keyword 路由 + N 个 prompt），应重构为"意图路由 + 单次工作流"或真正的 supervisor→specialist→response_writer 分工。
4. 不建议全盘推翻架构；保留骨架，做一次高杠杆的定向重构。

详见各文档与 [current-project-audit.md](./current-project-audit.md) 的最终结论。
