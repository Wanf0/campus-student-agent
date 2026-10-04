# Release Evaluation（P5.5 最终报告）

本报告基于当前 12 篇可入库语料，诚实区分"已实现 / 已验证 / 暂无法验证"。

## 一、11 项指标总览

| # | 指标 | 值 | 状态 |
| --- | --- | --- | --- |
| 1 | Knowledge Corpus Coverage | A 7 / B 3 / C 2（12 非工具题） | ✅ 可报告 |
| 2 | Retrieval Quality (Recall) | 1.0（每问单 gold，检索必中 top-4） | ✅ 可报告（但弱假设） |
| 3 | Citation Precision | 1.0（文档级） | ✅ 可报告 |
| 4 | Citation Recall | 1.0（文档级） | ✅ 可报告（但弱假设） |
| 5 | Grounding Accuracy | 1.0（C 类正确拒答） | ✅ 可报告 |
| 6 | Temporal Accuracy | — | ⛔ Pending Corpus |
| 7 | Authority Accuracy | — | ⛔ Pending Corpus |
| 8 | Abstention Accuracy | 1.0 | ✅ 可报告 |
| 9 | Agentic Recovery Success | 未触发（简单语料无需改写） | ⚠️ 未覆盖 |
| 10 | Latency | A/B≈16s，C/F≈39s | ✅ 可报告 |
| 11 | Token Usage | 未度量 | ⚠️ 待实现 |

## 二、已实现的机制

| 机制 | 代码位置 |
| --- | --- |
| 权威感知检索加权 | `domain/rag/retrieval.py::_authority_weight` |
| 时效过滤 + 版本归并 | `domain/rag/retrieval.py::_is_expired/_dedupe_latest` |
| 证据一致性（相关性分级 + 改写重试 + 证据过滤 + grounding） | `domain/agent.py`、`domain/rag/grounding.py` |
| Agentic Retrieval 循环 | `domain/agent.py::_prepare_rag` |
| 元数据字段（时间/权威/版本） | `domain/models.py`、`domain/knowledge.py` |
| run_id + trace 可观测 | `infrastructure/observability.py` |
| 评测框架（覆盖率 / citation 四指标 / A-F 消融） | `evaluation/` |

## 三、当前语料能验证的能力

1. **证据一致性（Evidence Grounding）有效**：agentic RAG 把答案召回从 0.773 提升到 0.864（+9pp），引用数从 4.0 压缩到 0.79（只保留相关证据），且 Citation Precision/Recall 均为 1.0。
2. **拒答（Abstention）正确**：知识库外与歧义问题正确回答"无法回答"，未编造。
3. **Self-correction 是唯一显著提升组件**：A/B/C 消融等价，F（+自校正）才有提升，说明当前提升来自相关性分级与证据过滤。

## 四、因 corpus 不足暂无法验证的能力

1. **来源权威性排序（Authority）**：语料全部 `source_authority=1`，无校级/处级/院级/学生整理分层。
2. **时间版本优先级（Temporal）**：无同主题多版本文档，无 `publish_date/effective_*` 元数据。
3. **冲突识别与消解（Conflict）**：无冲突来源样本。
4. **Agentic Recovery**：改写重试在简单语料上未触发。

> 上述四项标记 **Deferred / Pending Corpus**，机制已实现、评测框架已就绪，待补充权威分层 + 版本差异 + 冲突样本后重新评测。

## 五、对核心问题的回答

> 当前评测结果是否足以证明"Authority + Temporal + Evidence Grounding"有效？

**部分足以，部分不足：**

- ✅ **Evidence Grounding 已被证明有效**：相关性过滤 + grounding 带来可测量的答案质量提升与引用精度提升。
- ⛔ **Authority 与 Temporal 尚未被证明有效**：不是因为机制缺失，而是因为语料没有权威/时间维度，评测无法进行。当前 ablation 中 D/E 与 A/B/C 相同属于"无数据可作用"的必然结果，不能解读为机制无效。

**结论**：核心贡献的三支柱中，机制已全部实现，但仅有证据一致性支柱获得了实验验证。要完整验证，必须补充 temporal（多版本）、authority（分层）、conflict（冲突）三类语料——这是当前评测的根本缺口，而非评测方法或实现的问题。
