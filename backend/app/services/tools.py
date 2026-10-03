"""工具调用服务：为教务信息查询提供模拟数据与工具定义。"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "query_timetable",
            "description": "查询学生的课程表",
            "parameters": {
                "type": "object",
                "properties": {"semester": {"type": "string", "description": "学期，如 2026-2027-1"}},
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_score",
            "description": "查询学生的考试成绩",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_exam",
            "description": "查询考试安排（时间、地点）",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_notice",
            "description": "查询最新的校园通知公告",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "query_calendar",
            "description": "查询校历（开学、放假、考试周等时间安排）",
            "parameters": {"type": "object", "properties": {}},
        },
    },
]

# 模拟数据（开发阶段代替真实教务接口）
_MOCK_TIMETABLE = [
    {"时间": "周一 1-2 节", "课程": "软件工程", "地点": "教学楼A-101"},
    {"时间": "周二 3-4 节", "课程": "数据库系统", "地点": "教学楼B-203"},
    {"时间": "周三 5-6 节", "课程": "计算机网络", "地点": "实验楼C-305"},
    {"时间": "周四 1-2 节", "课程": "操作系统", "地点": "教学楼A-204"},
]

_MOCK_SCORE = [
    {"课程": "软件工程", "成绩": 92},
    {"课程": "数据库系统", "成绩": 88},
    {"课程": "计算机网络", "成绩": 85},
    {"课程": "操作系统", "成绩": 90},
]

_MOCK_EXAM = [
    {"课程": "软件工程", "时间": "2026-01-10 09:00", "地点": "教学楼A-101"},
    {"课程": "数据库系统", "时间": "2026-01-12 14:00", "地点": "教学楼B-203"},
]

_MOCK_NOTICE = [
    {"标题": "关于开展秋季开学初校园安全检查的通知", "时间": "2026-09-01"},
    {"标题": "2026年国庆假期安全提醒", "时间": "2026-09-28"},
    {"标题": "关于公布本科“优课优酬”奖励名单的通知", "时间": "2026-09-20"},
]

_MOCK_CALENDAR = [
    {"事项": "秋季学期开学", "时间": "2026-09-07"},
    {"事项": "国庆假期", "时间": "2026-10-01 至 10-07"},
    {"事项": "期末考试周", "时间": "2027-01-04 至 01-15"},
    {"事项": "寒假开始", "时间": "2027-01-16"},
]


def call_tool(name: str, args: dict) -> str:
    """调用工具并返回格式化后的字符串结果。"""
    if name == "query_timetable":
        return "课表如下：\n" + "\n".join(f"- {r['时间']}  {r['课程']}（{r['地点']}）" for r in _MOCK_TIMETABLE)
    if name == "query_score":
        return "成绩如下：\n" + "\n".join(f"- {r['课程']}：{r['成绩']}" for r in _MOCK_SCORE)
    if name == "query_exam":
        return "考试安排如下：\n" + "\n".join(f"- {r['课程']}：{r['时间']}（{r['地点']}）" for r in _MOCK_EXAM)
    if name == "query_notice":
        return "最新通知公告：\n" + "\n".join(f"- {r['时间']}  {r['标题']}" for r in _MOCK_NOTICE)
    if name == "query_calendar":
        return "校历安排：\n" + "\n".join(f"- {r['时间']}  {r['事项']}" for r in _MOCK_CALENDAR)
    return "未找到对应工具。"
