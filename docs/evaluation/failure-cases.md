# Failure Cases

记录当前评测中发现的失败案例与局限。当前语料小、每问仅一个 gold 文档，失败案例较少，但仍需诚实记录。

## 已观察到的失败/局限

### 1. Rerank 带来的时延成本（非正确性失败，但值得记录）

- **现象**：配置 C（+Rerank）与 F（+Self-correction）时延约 39s，A/B 约 16s。
- **根因**：交叉编码器对每个候选片段做 query-doc 联合推理，且 offline 前需加载模型。
- **影响**：交互体验下降，但换来了引用精度（0.79 vs 4.0）。
- **结论**：属成本-收益权衡，非 bug。

### 2. Temporal 开关在无元数据语料上产生噪声（E 配置）

- **现象**：E 的 Answer Recall 降至 0.682。
- **根因**：语料无 `effective_*`/`version` 元数据，`_dedupe_latest` 按 title 归并后，部分问题可引用的 chunk 被减少；叠加 LLM 非确定性。
- **影响**：若误读会得出"temporal 有害"的错误结论。
- **结论**：已在 ablation.md 标记 Pending Corpus，不据此下结论。

### 3. 无法测出的失败类型（受语料限制）

| 失败类型 | 为何当前测不出 |
| --- | --- |
| retrieval_failure | 每问唯一 gold 文档，向量检索总能命中 top-4 |
| citation_incomplete | 每问 gold_evidence_count=1，无多证据漏引场景 |
| hallucination_risk | 知识库外问题正确拒答，未触发编造 |
| 权威排序错误 | 无语料分层 |
| 版本选择错误 | 无多版本文档 |
| 冲突未识别 | 无冲突来源 |

## 结论

当前语料下未发现"正确性"层面的失败案例；主要风险是**指标在简单语料上虚高**（precision/recall=1.0 建立在"每问单 gold 文档"的弱假设上）。补充多文档、多版本、权威分层、冲突语料后，上述失败类型才能真正被评测出来。
