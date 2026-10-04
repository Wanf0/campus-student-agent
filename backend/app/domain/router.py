"""确定性路由 + LLM 兜底。"""

from app.infrastructure import llm

# 关键词规则（快速、确定性）。字典顺序即匹配优先级。
KEYWORDS = {
    "academic": ["课表", "成绩", "考试", "学分", "选课", "绩点", "查分", "通知", "校历"],
    "planning": ["计划", "规划", "安排学习", "目标", "制定"],
    "study": ["学习", "作业", "知识点", "讲解", "复习", "辅导", "资料", "推荐", "怎么学"],
    "life": ["食堂", "报修", "失物", "宿舍", "图书馆", "水电", "门禁", "快递", "校车"],
    "psychology": ["难过", "焦虑", "压力", "心情", "孤独", "失眠", "崩溃", "安慰", "烦", "累"],
}

VALID_INTENTS = ["qa", "study", "academic", "life", "psychology", "planning"]


def _llm_classify(message: str) -> str:
    prompt = (
        "请判断下面这条校园学生请求属于哪一类，只输出类别名，不要输出其他内容。\n"
        "类别：qa（校园信息/制度/办事流程问答）、study（学习辅导）、"
        "academic（教务信息查询）、life（校园生活服务）、"
        "psychology（心理陪伴/情绪疏导）、planning（个性化学习规划）。\n"
        f"请求：{message}"
    )
    try:
        resp = llm.chat([{"role": "user", "content": prompt}], temperature=0)
        intent = resp.strip().lower()
        for v in VALID_INTENTS:
            if v in intent:
                return v
    except Exception:
        pass
    return "qa"


def route(message: str) -> str:
    """返回意图类别。确定性关键词优先，LLM 兜底。"""
    for intent, kws in KEYWORDS.items():
        if any(k in message for k in kws):
            return intent
    return _llm_classify(message)
