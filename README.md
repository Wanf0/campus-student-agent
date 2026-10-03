# 校园学生智能体 (Campus Student Agent)

面向校园学生群体的智能体系统。以 DeepSeek 大语言模型为推理底座，结合 RAG 检索增强与多智能体协作，探索以自然语言作为学生与校园复杂信息系统之间更自然的交互层，降低校园中仍然存在的"剩余交互成本"。

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
| 智能体框架 | LangGraph（规划中） |
| 向量数据库 | Chroma |
| 关系数据库 | SQLite（开发）/ MySQL（文档标准） |
| 嵌入模型 | BAAI/bge-small-zh-v1.5 |
| 前端 | Vue3 |

## 项目结构

```
campus-agent/
├── backend/          # FastAPI 后端
│   ├── app/
│   │   ├── main.py           # 入口
│   │   ├── config.py         # 配置
│   │   ├── db.py             # 数据库会话
│   │   ├── models.py         # SQLAlchemy 模型（7 张表）
│   │   ├── schemas.py        # Pydantic 模型
│   │   ├── routers/          # 路由
│   │   ├── agents/           # 智能体
│   │   └── services/         # llm / rag / tools / memory
│   ├── requirements.txt
│   └── .env.example
├── frontend/         # Vue3 前端
├── knowledge/        # 校园知识库文档
└── README.md
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

启动后访问 `http://127.0.0.1:8000/docs` 查看接口文档。

## 环境变量

| 变量 | 说明 |
| --- | --- |
| `DEEPSEEK_API_KEY` | DeepSeek API Key（必填） |
| `DEEPSEEK_MODEL` | 模型名，默认 `deepseek-chat` |
| `DATABASE_URL` | 数据库连接串，默认 SQLite |
| `EMBEDDING_MODEL` | 嵌入模型，默认 `BAAI/bge-small-zh-v1.5` |
| `CHROMA_DIR` | 向量库持久化目录 |

> 注意：`.env` 含密钥，已被 `.gitignore` 排除，切勿提交。
