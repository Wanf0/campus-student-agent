"""单一 Campus Agent：确定性路由 + 工具调用 + agentic RAG 自校正。"""

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
    "你是教务信息查询助手。当用户查询课表、成绩、考试、通知或校历时，"
    "请调用相应工具获取数据，再整理为自然语言回答。"
)


class CampusAgent:
    def __init__(self):
        self.registry = build_registry()

    # ---- 入口 ----

    def run(self, query: str, history: list[dict] | None = None) -> AgentOutput:
        intent = router.route(query)
        messages, evidence, citations = self._prepare(intent, query, history)
        answer = llm.chat(messages)
        return AgentOutput(answer=answer, evidence=evidence, citations=citations, intent=intent)

    def run_stream(self, query: str, history: list[dict] | None = None):
        intent = router.route(query)
        messages, evidence, citations = self._prepare(intent, query, history)
        return intent, evidence, citations, llm.chat_stream(messages)

    # ---- 准备最终生成 ----

    def _prepare(self, intent: str, query: str, history: list[dict] | None):
        history = history or []
        if intent == "qa":
            return self._prepare_rag(query, history)
        if intent == "academic":
            return self._prepare_tool(query, history), [], []
        return self._prepare_generic(intent, query, history), [], []

    # ---- agentic RAG（检索 → 分级 → 改写 → 生成） ----

    def _prepare_rag(self, query: str, history: list[dict]) -> tuple[list[dict], list[Evidence], list[Citation]]:
        evidence = search_knowledge(query)

        for _ in range(settings.agent_max_rewrite_retries):
            if self._relevant(evidence):
                break
            query = self._rewrite(query, history)
            evidence = search_knowledge(query)

        # 只保留超过相关性阈值的证据，保证答案 grounded
        evidence = [e for e in evidence if (e.rerank_score or 0) >= settings.rerank_score_threshold]
        citations = grounding.to_citations(evidence)
        context = grounding.build_grounded_context(evidence)

        system = GROUNDED_PROMPT + ("\n\n可用资料：\n" + context if evidence else "\n\n（无相关检索结果）")
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        return messages, evidence, citations

    def _relevant(self, evidence: list[Evidence]) -> bool:
        if not evidence:
            return False
        best = max((e.rerank_score or 0) for e in evidence)
        return best >= settings.rerank_score_threshold

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

    def _prepare_tool(self, query: str, history: list[dict]) -> list[dict]:
        client = llm.get_client()
        messages = [{"role": "system", "content": TOOL_PROMPT}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})

        resp = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=messages,
            tools=self.registry.schemas(),
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            messages.append(msg)
            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = self.registry.call(tc.function.name, args)
                content = self._format_tool_result(result)
                messages.append({"role": "tool", "tool_call_id": tc.id, "content": content})
        return messages

    def _format_tool_result(self, result) -> str:
        if result.status == "missing_params":
            return "缺少参数：" + "、".join(result.missing_params) + "，请向用户询问这些信息。"
        if result.status == "error":
            return "查询失败：" + (result.error_message or "未知错误")
        return str(result.data)

    # ---- 开放对话 ----

    def _prepare_generic(self, intent: str, query: str, history: list[dict]) -> list[dict]:
        system = GENERIC_PROMPTS.get(intent, GENERIC_PROMPTS["study"])
        messages = [{"role": "system", "content": system}]
        messages.extend(history)
        messages.append({"role": "user", "content": query})
        return messages
