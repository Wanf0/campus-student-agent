# 核心贡献 → 机制 → 指标 → 证据状态 映射

将毕设核心贡献（Authority-aware + Temporal-aware + Evidence-grounded + Agentic Retrieval）映射到具体机制、代码位置、评测指标与当前验证状态。

## 映射表

| 贡献支柱 | 机制 | 代码位置 | 评测指标 | 当前状态 |
| --- | --- | --- | --- | --- |
| **来源权威性** | 检索融合按 authority 加权 | `domain/rag/retrieval.py::_authority_weight` | authority ranking 正确率 | ⛔ Pending Corpus（无权威元数据） |
| **时间有效性** | 时效过滤 + 版本归并 | `domain/rag/retrieval.py::_is_expired/_dedupe_latest` | temporal accuracy（选对当前有效版本） | ⛔ Pending Corpus（无时间/版本元数据） |
| **证据一致性** | 相关性分级 + 改写重试 + 证据过滤 + grounding | `domain/agent.py::_prepare_rag/_relevant/_rewrite`、`domain/rag/grounding.py` | Citation Precision/Recall、Answer Recall、Abstention | ✅ 已验证（当前语料） |
| **Agentic Retrieval** | 检索→分级→改写→生成循环 | `domain/agent.py` | Agentic Recovery、Answer Recall | ✅ 部分验证（改写重试在简单语料上未触发） |
| **元数据基础设施** | Document/Chunk 时间/权威/版本字段 | `domain/models.py`、`domain/knowledge.py` | —（基础设施） | ✅ 已实现（待数据填充） |
| **可观测** | run_id + trace | `infrastructure/observability.py`、`domain/models.py::Run/TraceEvent/ToolCall` | 归因能力 | ✅ 已实现（待前端展示） |

## 状态汇总

| 状态 | 支柱 | 说明 |
| --- | --- | --- |
| ✅ 已验证 | 证据一致性、Agentic 检索（分级+过滤） | 用当前 12 篇语料评测，Answer Recall +9pp、引用精度 0.79 vs 4.0 |
| ⛔ Pending Corpus | 来源权威性、时间有效性 | 机制与元数据字段已实现，但语料无权威分层/版本/时效信息，无法评测 |
| ⚠️ 未覆盖 | 冲突识别与消解 | 语料无冲突来源 |

## 诚实声明

1. 核心贡献的四支柱中，**机制全部已实现**，但**只有证据一致性得到实验验证**。
2. 权威性与时效性"实现 ≠ 验证"：代码已具备加权/过滤能力，但语料没有对应维度，故无法声称已验证。
3. 要完成完整验证，需补充：同主题多版本（temporal）、权威分层样本（authority）、冲突来源样本（conflict）。
