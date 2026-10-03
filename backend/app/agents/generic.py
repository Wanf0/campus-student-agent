"""通用领域智能体：学习辅导、校园生活服务、心理陪伴、个性化学习规划。"""

from ..services import llm

SYSTEM_PROMPTS = {
    "study": "你是校园学生智能体中的学习辅导助手，负责课程答疑、知识点讲解与学习资源推荐。回答清晰、有条理。",
    "life": "你是校园学生智能体中的校园生活服务助手，负责通知公告、报修、失物招领、食堂等校园生活信息咨询。",
    "psychology": "你是校园学生智能体中的心理陪伴助手，以温暖、共情的语气进行情绪疏导与日常陪伴。",
    "planning": "你是校园学生智能体中的学习规划助手，基于用户情况制定个性化的学习计划与建议。",
}


def handle(intent: str, message: str, history: list[dict] | None = None) -> str:
    system = SYSTEM_PROMPTS.get(intent, SYSTEM_PROMPTS["study"])
    messages = [{"role": "system", "content": system}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})
    return llm.chat(messages)
