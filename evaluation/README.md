# Evaluation 系统

验证核心创新「面向校园时效性知识的权威感知 Agentic RAG」的 grounding 能力。

## 运行

```bash
cd backend
source .venv/bin/activate
python ../evaluation/runner.py
```

## 数据集

`datasets/campus_qa.json` 含 6 类校园问题：

| 类别 | 示例 |
| --- | --- |
| 简单知识 | 图书馆一次能借几本书？ |
| 复杂检索 | 国家奖学金和校级一等奖学金哪个要求更高？ |
| 结构化查询 | 查一下我的课表 |
| 多工具 | 最近有什么校园通知？ |
| 歧义 | 补考什么时候？ |
| 时效性 | 今年奖学金申请条件是什么？ |
| 知识库外 | 今天股市大盘怎么样？ |

每条含 `query / expected_intent / expected_keywords / expected_sources`。

## 指标

| 指标 | 含义 |
| --- | --- |
| routing_accuracy | 意图路由准确率 |
| answer_keyword_recall | 答案中命中期望关键词的比例（答案质量） |
| citation_hit | 引用中命中期望来源的比例 |
| grounding_ok | 知识库外/歧义问题时是否正确表达"无法回答"（不编造） |
| avg_citations | 每条回答平均引用数（越低越精确，衡量引用精度） |

## 结果（本次运行示例）

| 指标 | Before(naive RAG) | After(agentic RAG) |
| --- | --- | --- |
| answer_keyword_recall | 0.773 | 0.864 |
| citation_hit | 1.0 | 1.0 |
| grounding_ok | 1.0 | 1.0 |
| avg_citations | 4.0 | 0.79 |

**结论**：权威感知 agentic RAG 在答案质量上优于 naive RAG（+9pp），且引用精度大幅提升（0.79 vs 4.0），证明相关性分级与证据过滤有效。

## 设计说明

- `naive_rag` 基线与 agentic RAG 使用相同的 grounded prompt，唯一区别是 agentic RAG 多了「重排 + 相关性分级 + 改写重试 + 证据过滤」，因此对比公平。
- `avg_citations` 是核心差异化指标：naive 固定返回 top-4（含无关），agentic 只返回超过相关性阈值的证据。
