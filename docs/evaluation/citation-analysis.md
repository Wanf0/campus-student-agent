# Citation 评测分析

对评测集逐题分析引用行为，区分"good compression / citation incomplete / correct abstention / retrieval failure"四种情况。

## 逐题分析结果

| id | 类别 | A/B/C | gold | retrieved | cited | relevant | missed | 判定 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| simple_01 | 简单知识 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| simple_02 | 简单知识 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| simple_03 | 简单知识 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| complex_01 | 复杂检索 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| complex_02 | 复杂检索 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| complex_03 | 复杂检索 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| struct_01/02 | 结构化查询 | tool | 0 | 4 | 0 | 0 | 0 | n/a（工具，非语料） |
| multitool_01 | 多工具 | B | 0 | 4 | 0 | 0 | 0 | n/a |
| multitool_02 | 多工具 | B | 0 | 4 | 3 | 0 | 0 | n/a |
| ambiguous_01 | 歧义 | C | 0 | 4 | 0 | 0 | 0 | correct_abstention |
| temporal_01 | 时效性 | B | 1 | 4 | 1 | 1 | 0 | good_compression |
| temporal_02 | 时效性 | A | 1 | 4 | 1 | 1 | 0 | good_compression |
| oov_01 | 知识库外 | C | 0 | 4 | 0 | 0 | 0 | correct_abstention |

## 四指标（文档级）

| 指标 | 值 | 说明 |
| --- | --- | --- |
| Citation Precision | **1.0** | 被引用的证据中，全部是 gold（无无关引用） |
| Citation Recall | **1.0** | 所有 gold 文档都被引用（无漏引） |
| Citation Completeness | **0.812** | key_claims 在答案中的命中率 |
| Citation Correctness | doc-level | 与 precision 同源；claim 级需人工标注 → Deferred |

## 分类统计

- good_compression：8（所有 A/B 有 gold 题）
- correct_abstention：2（歧义 + 库外）
- n/a：4（工具类 + B 无 gold 类）

## 关键观察

1. **"低引用"（avg 0.79）是 good compression，不是过度压缩**：所有 A 类题 retrieved=4 → cited=1，且 relevant=1、missed=0，说明 agent 删掉了 3 条无关证据、保留了唯一相关证据，precision/recall 均为 1.0。
2. **没有出现 citation_incomplete 或 retrieval_failure**：当前语料规模小、每个问题只有一个 gold 文档，检索总能命中。
3. **C 类正确拒答**：补考、股市两题均 cited=0，未编造。

## 局限（必须诚实声明）

- 当前每个问题 gold_evidence_count=1，无法测出"多证据问题是否漏引"（Citation Recall 上限被压低）。
- Citation Correctness 目前只有文档级近似，claim 级对齐需人工标注。
- 上述 Precision/Recall 的 1.0 是在"每问仅 1 个 gold 文档"的简单场景下取得的，不代表复杂多文档场景下仍成立。
