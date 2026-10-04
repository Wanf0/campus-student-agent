# 校园学生智能体 (Campus Student Agent)

面向校园学生群体的智能体系统。以 DeepSeek 大语言模型为推理底座，结合权威感知 RAG 检索增强与工具调用，探索以自然语言作为学生与校园复杂信息系统之间更自然的交互层，降低校园中仍然存在的"剩余交互成本"。

## 功能

- **校园智能问答**：基于 RAG，对校园制度、通知、办事流程等信息进行问答
- **学习辅导**：课程答疑、知识点讲解、学习资源推荐
- **教务信息查询**：通过工具调用（Function Calling）查询课表、成绩、考试安排
- **校园生活服务**：通知公告、报修、失物招领等信息查询
- **心理陪伴**：情绪疏导与日常陪伴式对话
- **个性化学习规划**：基于用户画像生成个性化学习建议

## 技术栈

| 组件 | 技术 |
| --- | --- |
| 大语言模型 | DeepSeek（API） |
| 后端 | Python + FastAPI |
| 智能体编排 | 单一 Agent + 确定性路由 + 工作流（权威感知 agentic RAG） |
| 向量数据库 | Chroma |
| 关系数据库 | SQLite（开发）/ MySQL（文档标准） |
| 嵌入模型 | BAAI/bge-small-zh-v1.5 |
| 重排模型 | BAAI/bge-reranker-base |
| 前端 | Vue3 + TypeScript + Vite |

## 项目结构

```
campus-agent/
├── backend/              # FastAPI 后端（分层架构）
│   ├── app/
│   │   ├── api/          # 路由与协议转换
│   │   ├── application/  # 编排器、run 生命周期、trace
│   │   ├── domain/       # 单一 Agent、router、RAG、Tool、knowledge
│   │   └── infrastructure/  # llm / embedding / reranker / vectorstore / db / observability
│   ├── requirements.txt
│   └── .env.example
├── frontend/             # Vite + Vue3 + TypeScript 前端
├── knowledge/            # 校园知识库文档
├── evaluation/           # 评测系统（覆盖率/citation/ablation）
├── docs/                 # 架构与评测文档
└── research/             # 开源调研与架构审计
```

## 快速开始

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # 填入你的 DeepSeek API Key
uvicorn app.main:app --reload
```

启动后：

- 访问 `http://127.0.0.1:8000/docs` 查看接口文档
- 前端：生产模式先 `cd frontend && npm install && npm run build`（FastAPI 自动服务 `dist/`）；开发模式 `npm run dev`（代理到后端）

```bash
# 前端开发模式
cd frontend
npm install
npm run dev        # 访问 http://localhost:5173，代理到后端 :8000
```

### 导入知识库

将校园文档（`.txt` 或 `.pdf`）放入 `knowledge/` 目录，然后：

```bash
cd backend
source .venv/bin/activate
python seed.py
```

> 注：`knowledge/` 下的真实校园 PDF（含个人信息）已被 `.gitignore` 排除，仅用于本地构建知识库，不会提交到仓库。

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（必填） |
| `DEEPSEEK_MODEL` | 模型名，默认 `deepseek-chat` |
| `DATABASE_URL` | 数据库连接串，默认 SQLite |
| `EMBEDDING_MODEL` | 嵌入模型，默认 `BAAI/bge-small-zh-v1.5` |
| `CHROMA_DIR` | 向量库持久化目录 |

> 注意：`.env` 含密钥，已被 `.gitignore` 排除，切勿提交。
