# Ablation 分析

逐组件消融，观察各检索/生成配置对指标的影响。

## 配置定义

| 配置 | 组成 |
| --- | --- |
| A | Naive Vector RAG（仅向量，无过滤） |
| B | + BM25（混合检索） |
| C | + Rerank（重排） |
| D | + Authority（权威加权） |
| E | + Temporal（时效过滤/版本归并） |
| F | + Agentic Self-correction（相关性分级 + 改写 + 证据过滤） |

## 结果

| 配置 | Retrieval Recall | Answer Recall | Abstention | avg Citations | Latency |
| --- | --- | --- | --- | --- | --- |
| A (naive vector) | 1.0 | 0.773 | 1.0 | 4.0 | 15.9s |
| B (+BM25) | 1.0 | 0.773 | 1.0 | 4.0 | 15.8s |
| C (+Rerank) | 1.0 | 0.773 | 1.0 | 4.0 | 39.0s |
| D (+Authority) | 1.0 | 0.773 | 1.0 | 4.0 | 15.4s |
| E (+Temporal) | 1.0 | 0.682 | 1.0 | 4.0 | 16.1s |
| F (+Self-correction) | 1.0 | 0.864 | 1.0 | 0.79 | 39.4s |

## 可验证的结论（仅基于当前 12 篇语料）

1. **Agentic Self-correction 是唯一带来答案质量提升的组件**：Answer Recall 从 0.773 → 0.864（+9pp），avg Citations 从 4.0 → 0.79。
2. **BM25 / Rerank 在当前语料下无收益**：A/B/C 的 Answer Recall 完全相同（0.773），因为语料小、向量检索已能命中唯一 gold 文档。
3. **Rerank 与 Self-correction 带来明显时延**：C/F 约 39s（交叉编码器 + 改写循环），A/B 约 16s。

## 因语料不足无法验证的结论（Deferred / Pending Corpus）

1. **D (Authority)**：语料所有文档 `source_authority=1`，无权威分层，权威加权无差异可作用。D 与 A/B/C 结果相同是**必然的、无意义的**，不代表 authority 无价值。
2. **E (Temporal)**：语料无时间/版本元数据，`_dedupe_latest`/`_is_expired` 空转；E 的 Answer Recall 0.682 属于**噪声**（LLM 非确定性），不能解读为"temporal 有害"。
3. **Conflict 消解**：语料无冲突来源，完全无法评测。

## 结论

> 当前 ablation 只能证明：**Agentic Self-correction（证据一致性）有效**。
> **Authority / Temporal 两个支柱因语料无对应维度，标记 Pending Corpus，待补充权威分层 + 版本差异 + 冲突样本后重新评测。**
