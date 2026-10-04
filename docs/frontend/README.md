# 前端工程说明

校园学生智能体前端，基于 Vite + Vue3 + TypeScript，测试用 Vitest + @vue/test-utils。

## 架构

遵循「UI → State → API Client → SSE Parser」职责分离：

```
src/
├── types/          # 前后端事件契约与领域类型（无 any）
├── services/
│   ├── api.ts      # HTTP API client（认证/会话/聊天/知识库）
│   └── sse.ts      # SSE 解析器（ReadableStream → 类型化事件）
├── stores/
│   └── chat.ts     # 会话/消息/流状态（composable）
├── utils/
│   └── markdown.ts # markdown 渲染 + 转义 + 摘录
├── components/     # EvidenceList / ToolStatus / ClarificationCard / TracePanel / ErrorState / MessageBubble
└── features/
    ├── chat/ChatView.vue
    └── auth/LoginView.vue
```

## 事件契约

后端 `/chat/stream` 通过 SSE 发射类型化事件（`run_id` 贯穿全程）：

```
start → status → evidence → tool_call → clarification → token → error → done
```

前端只渲染真实事件，不伪造思考/工具/检索过程。

## 开发

```bash
cd frontend
npm install
npm run dev          # Vite dev server（已配置代理到 http://127.0.0.1:8000）
```

## 构建（生产）

```bash
npm run build        # 产物输出到 dist/，由 FastAPI 挂载 /assets 与 / 服务
```

## 测试

```bash
npm test             # Vitest
npm run typecheck    # vue-tsc 类型检查
```

覆盖：SSE 解析、citation 渲染、tool 状态、澄清流程、错误状态、空证据、store 事件处理。

## 关键设计

- **Evidence / Citation 展示**：回答与证据分离，EvidenceCard 展示来源/权威/时间/版本/摘录，字段缺失优雅降级。
- **Tool 状态**：基于真实 `tool_call` 事件显示"查询课表/成绩 + 成功/失败/缺参"，不暴露内部异常与路径。
- **澄清**：`clarification` 事件触发，提供班级快捷选项（A/B）+ 自然语言输入。
- **Trace/Debug**：每条助手消息可展开查看 run_id/意图/阶段/工具/证据数。
- **错误**：区分可重试/不可重试，重试按钮重发最后一条用户消息。
