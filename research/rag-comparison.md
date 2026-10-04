# RAG 对比：naive / hybrid / agentic

对比三种 RAG 形态，说明当前项目处于哪一层、缺什么。

## 三种形态

### 1. Naive RAG（当前项目所在层）

```
query → embed → 向量检索 → 拼接 top-k 上下文 → LLM 生成
```

- 一次性检索，无反馈。
- 检索空结果时仍让 LLM 作答（可能编造）。
- 没有相关性判断、没有改写、没有 grounding 校验。

### 2. Hybrid RAG（当前项目已做到的一部分）

```
query → 向量检索 + BM25 → RRF 融合 → 重排 → top-k → LLM 生成
```

- 多路召回 + 融合 + 重排，提升召回质量。
- **但仍是"一次向前"**：召回质量没有显式校验，也没有回溯。
- 当前项目的 `retrieval.py`（向量+BM25+RRF）+ `rerank.py`（bge-reranker）即处于这一层。

### 3. Agentic RAG（成熟项目采用，当前项目缺失）

```
query → (agent 决定是否检索) → 检索 → 相关性分级(grade)
        ├─ 相关 → 生成（强制 grounding + 引用）
        └─ 不相关 → 改写 query → 回到检索（重试，有上限）
```

- **检索失败检测**：LLM 对召回文档做二元相关性分级（yes/no）。
- **改写重试**：不相关则改写问题重试，形成闭环。
- **answer grounding**：生成阶段显式要求"基于上下文、无依据则明说、禁止编造"。

来源证据：

- LangGraph-Chatchat `chatchat/server/agent/graphs_factory/base_rag.py`：
  - `grade_documents` 用 `with_structured_output(Grade)` 输出 `binary_score: yes/no`；
  - `rewrite` 节点改写问题后回到 `chatbot`；
  - `generate` 的 prompt 明确"根据已知信息回答，无法回答请说'根据已知信息无法回答该问题'，不允许编造"。
- RAGFlow 的 **Agentic Retrieval**：多步检索、拆解问题、验证证据、多轮检索推理以生成有根据的答案。

## 对比表

| 维度 | Naive | Hybrid（当前） | Agentic（目标） |
| --- | --- | --- | --- |
| 召回路数 | 1 | 2（向量+BM25）+重排 | 2+ 且可多轮 |
| 相关性校验 | 无 | 无 | 有（grade） |
| 失败处理 | 无 | 无 | 改写重试 |
| answer grounding | 弱（仅 prompt 建议） | 弱 | 强（结构化约束） |
| 引用粒度 | 粗 | 粗（title） | 可到 chunk/页级 |
| 可评测 | 难 | 难 | 可（有明确的中间态） |

## 结论

当前项目的"混合检索 + 重排"方向正确，但停在 Hybrid 层，**缺"相关性分级 + 改写重试 + grounding"的闭环**。这是最值得补的一块，因为它：

1. 直接降低幻觉（服务"不做编造"的立意）；
2. 有明确的中间态（grade 结果、改写记录），可观测、可评测；
3. 与 LangGraph 天然契合（循环图），当前已有 LangGraph 骨架，改造成本低。
