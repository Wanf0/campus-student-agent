"""单一 Campus Agent：确定性路由 + 工具调用 + agentic RAG 自校正。

流式入口 run_stream 以事件 dict 生成器形式暴露完整执行轨迹
（start/status/evidence/tool_call/clarification/token/error/done），
run_id 由上层 chat.py 注入并贯穿整个请求。
"""

import json

from app.config import settings
from app.domain import router
from app.domain.entities import AgentOutput, Citation, Evidence
from app.domain.rag import grounding
from app.domain.tools import build_registry
from app.domain.tools.knowledge_tool import search_knowledge
from app.infrastructure import llm

GROUNDED_PROMPT = (
    "你是校园学生智能体。请【仅根据】下方提供的校园资料回答用户问题，"
    "并在回答末尾列出依据来源。\n"
    "规则：\n"
    "1. 若资料足以回答，请引用资料中的信息，不得编造。\n"
    "2. 若资料不足以回答或与问题无关，请明确说'根据现有资料无法回答'，"
    "并建议用户咨询相应部门或补充信息。\n"
    "3. 涉及时效信息时，请说明信息的发布时间或有效期。"
)

GENERIC_PROMPTS = {
    "study": "你是校园学生智能体中的学习辅导助手，负责课程答疑、知识点讲解与学习资源推荐。",
    "psychology": "你是校园学生智能体中的心理陪伴助手，以温暖、共情的语气进行情绪疏导与日常陪伴。",
    "planning": "你是校园学生智能体中的学习规划助手，基于用户情况制定个性化的学习计划与建议。",
}

TOOL_PROMPT = (
    "你是教务信息查询助手。当用户查询课表、成绩或考试安排时，"
    "请调用相应工具获取数据，再整理为自然语言回答。"
)

# 确定性工具选择：根据关键词强制指定工具，避免 LLM 自行判断导致澄清路径不稳定
ACADEMIC_TOOL_KEYWORDS = {
    "query_timetable": ["课表", "课程", "上课"],
    "query_score": ["成绩", "绩点", "查分"],
    "query_exam": ["考试", "考场"],
}


def _select_academic_tool(query: str) -> str | None:
    for tool, kws in ACADEMIC_TOOL_KEYWORDS.items():
        if any(k in query for k in kws):
            return tool
    return None


class CampusAgent:
    def __init__(self):
        self.registry = build_registry()

    # ---- 同步入口（供 /chat 与评测） ----

    def run(self, query: str, history: list[dict] | None = None) -> AgentOutput:
        intent = router.route(query)
        answer = ""
        evidence: list[Evidence] = []
        citations: list[Citation] = []
        for ev in self.run_stream(query, history):
            e = ev["event"]
            if e == "token":
                answer += ev.get("content", "")
            elif e == "evidence":
                evidence = [Evidence(**it) for it in ev.get("items", [])]
            elif e == "done":
                citations = [Citation(**c) for c in ev.get("citations", [])]
        return AgentOutput(answer=answer, evidence=evidence, citations=citations, intent=intent)

    # ---- 流式入口：yield 事件 dict ----

    def run_stream(self, query: str, history: list[dict] | None = None):
        intent = router.route(query)
        yield {"event": "start", "intent": intent}
        history = history or []
        if intent == "qa":
            yield from self._stream_rag(query, history)
        elif intent == "academic":
            yield from self._stream_tool(query, history)
        else:
            yield from self._stream_generic(intent, query, history)

    # ---- agentic RAG ----

    def _stream_rag(self, query: str, history: list[dict]):
        yield {"event": "status", "phase": "retrieving"}
        evidence = search_knowledge(query)
        for _ in range(settings.agent_max_rewrite_retries):
            if self._relevant(evidence):
                break
            yield {"event": "status", "phase": "rewriting"}
            query = self._rewrite(query, history)
            evidence = search_knowledge(query)

        evidence = [e for e in evidence if (e.rerank_score or 0) >= settings.rerank_score_threshold]
        yield {"event": "evidence", "items": [e.model_dump() for e in evidence]}
        citations = grounding.to_citations(evidence)
        yield {"event": "status", "phase": "generating"}

        messages = self._rag_messages(evidence, query, history)
        for token in llm.chat_stream(messages):
            yield {"event": "token", "content": token}
        yield {"event": "done", "citations": [c.model_dump() for c in citations]}

    def _rag_messages(self, evidence: list[Evidence], query: str, history: list[dict]) -> list[dict]:
        context = grounding.build_grounded_context(evidence)
        system = GROUNDED_PROMPT + ("\n\n可用资料：\n" + context if evidence else "\n\n（无相关检索结果）")
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        return messages

    def _relevant(self, evidence: list[Evidence]) -> bool:
        if not evidence:
            return False
        best = max((e.rerank_score or 0) for e in evidence)
        return best >= settings.rerank_score_threshold

    def _tool_choice(self, query: str):
        tool = _select_academic_tool(query)
        if tool:
            return {"type": "function", "function": {"name": tool}}
        return "auto"

    def _rewrite(self, query: str, history: list[dict]) -> str:
        prompt = (
            "请理解下面的问题并结合历史对话改写为一个更适合检索的明确问题，"
            "只输出改写后的问题：\n历史："
            + "\n".join(f"{m['role']}: {m['content']}" for m in history[-4:])
            + f"\n问题：{query}"
        )
        try:
            rewritten = llm.chat([{"role": "user", "content": prompt}], temperature=0).strip()
            return rewritten or query
        except Exception:
            return query

    # ---- 工具调用 ----

    def _stream_tool(self, query: str, history: list[dict]):
        yield {"event": "status", "phase": "tool_calling"}
        client = llm.get_client()
        messages = [{"role": "system", "content": TOOL_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        resp = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            tools=self.registry.schemas(),
            tool_choice=self._tool_choice(query),
        )
        msg = resp.choices[0].message

        if not msg.tool_calls:
            yield {"event": "status", "phase": "generating"}
            messages.append(msg)
            for token in llm.chat_stream(messages):
                yield {"event": "token", "content": token}
            yield {"event": "done", "citations": []}
            return

        messages.append(msg)
        for tc in msg.tool_calls:
            yield {"event": "tool_call", "tool": tc.function.name, "status": "start"}
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            result = self.registry.call(tc.function.name, args)

            if result.status == "missing_params":
                yield {"event": "tool_call", "tool": tc.function.name, "status": "missing_params",
                       "missing": result.missing_params}
                question = "需要补充参数：" + "、".join(result.missing_params) + "（例如 A班 或 B班）"
                yield {"event": "clarification", "missing": result.missing_params, "question": question}
                yield {"event": "token", "content": question}
                yield {"event": "done", "citations": []}
                return

            if result.status == "error":
                yield {"event": "tool_call", "tool": tc.function.name, "status": "error"}
                yield {"event": "error", "message": "查询失败，请稍后重试", "retryable": True}
                yield {"event": "done", "citations": []}
                return

            yield {"event": "tool_call", "tool": tc.function.name, "status": "ok"}
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": str(result.data)})

        yield {"event": "status", "phase": "generating"}
        for token in llm.chat_stream(messages):
            yield {"event": "token", "content": token}
        yield {"event": "done", "citations": []}

    # ---- 开放对话 ----

    def _stream_generic(self, intent: str, query: str, history: list[dict]):
        yield {"event": "status", "phase": "generating"}
        system = GENERIC_PROMPTS.get(intent, GENERIC_PROMPTS["study"])
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        for token in llm.chat_stream(messages):
            yield {"event": "token", "content": token}
        yield {"event": "done", "citations": []}
