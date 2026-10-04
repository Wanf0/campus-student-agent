# 工程实践对比

对比评测、可观测性、错误处理、配置、部署等工程能力，说明当前项目的短板。

## 对比表

| 能力 | 当前项目 | Campus-Asistant | LangGraph-Chatchat | FastGPT | Dify | RAGFlow |
| --- | --- | --- | --- | --- | --- | --- |
| **评测(Evaluation)** | 冒烟测试（意图+状态码+关键词） | dataset.json + runner（意图/关键词/时延） | 弱（靠 UI 测试） | 应用评测 + 知识库单点测试 | 标注 + evaluation | 弱 |
| **可观测性** | 无 trace | print 日志 | 日志 + checkpoint | 完整调用链路日志 | LLMOps（Langfuse/Phoenix/Opik） | 引用可追踪 |
| **错误处理** | 异常直接冒泡 | try/except → error context → 响应层优雅降级 | 重试(max_retries) + 结构化输出 | 节点日志 | 节点级错误 | 工程性 |
| **配置** | pydantic-settings（无校验） | dotenv | 多级配置 + registry | 环境变量 | 多级配置 | service_conf.yaml |
| **测试** | 1 个脚本 | 13+ 个 test_*.py | 脚本检查导入 | vitest | e2e + 单元 | Go tests |
| **部署** | 本地 venv | Procfile(Heroku) | Docker | Docker Compose | Docker Compose | Docker(Go) |

## 关键缺口与借鉴

### 1. 评测（最关键的缺口）

Campus-Asistant 的 `eval/dataset.json` 结构：

```json
{ "id": "q2", "query": "What is the attendance policy?",
  "expected_intent": "rag",
  "expected_keywords": ["75%", "shortage", "minimum"] }
```

`eval/runner.py` 的评测维度：**意图匹配率 + 关键词命中率 + 时延**，并统计成功/超时/出错。

**可迁移**：为校园场景建一个中文评测集，每条含 `query / expected_intent / expected_keywords / expected_sources`，用脚本跑分。这是把项目从"课程 demo"提升为"可验证工程"的最快方式。

### 2. 可观测性

Dify/FastGPT 都强调**完整调用链路日志**——一次回答里能看到：命中了哪些 chunk、调了哪些工具、每步耗时。当前项目完全没有。

**轻量替代**：不用上 Langfuse/Phoenix 全套，只需在每次 run 时记录结构化中间态（query、intent、retrieved docs + scores、tool calls、latency、token），输出到日志或一个 trace 表，即可在答辩中展示"检索到了什么、为什么这么答"。

### 3. 错误处理

Campus-Asistant 的 pattern：specialist 内部 try/except → 把错误写成 `context` 项 → response_writer 识别后向用户礼貌说明，而非崩溃或编造。

**可迁移**：当前项目的 agent 应把异常转成结构化错误上下文，让上层决定是降级、澄清还是重试。

### 4. 测试规模

当前只有 1 个测试脚本；成熟项目有分层测试（health/api/rag/agent/supervisor 各一）。

**可迁移**：至少把"检索质量"与"意图路由"拆成独立可测单元，配合评测集做回归。

## 结论

工程能力是当前项目与成熟项目差距最大、但**补齐成本最低**的一块。优先级：**评测集 > 可观测 trace > 结构化错误处理 > 分层测试**。这三样都不需要引入重型基础设施，却能让项目在答辩中"经得起看"。
