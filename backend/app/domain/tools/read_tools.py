"""只读工具：教务查询（课表/成绩/考试/通知/校历，mock 数据）。"""

from app.domain.tools.base import Tool, MissingParamsError

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
]

_MOCK_CALENDAR = [
    {"事项": "秋季学期开学", "时间": "2026-09-07"},
    {"事项": "国庆假期", "时间": "2026-10-01 至 10-07"},
    {"事项": "期末考试周", "时间": "2027-01-04 至 01-15"},
]


def _timetable(args: dict):
    return _MOCK_TIMETABLE


def _score(args: dict):
    return _MOCK_SCORE


def _exam(args: dict):
    return _MOCK_EXAM


def _notice(args: dict):
    return _MOCK_NOTICE


def _calendar(args: dict):
    return _MOCK_CALENDAR


def build_read_tools() -> list[Tool]:
    return [
        Tool("query_timetable", "查询学生的课程表", "read", "read_only",
             {"type": "object", "properties": {}, "required": []}, _timetable),
        Tool("query_score", "查询学生的考试成绩", "read", "read_only",
             {"type": "object", "properties": {}, "required": []}, _score),
        Tool("query_exam", "查询考试安排", "read", "read_only",
             {"type": "object", "properties": {}, "required": []}, _exam),
        Tool("query_notice", "查询最新校园通知公告", "read", "read_only",
             {"type": "object", "properties": {}, "required": []}, _notice),
        Tool("query_calendar", "查询校历", "read", "read_only",
             {"type": "object", "properties": {}, "required": []}, _calendar),
    ]
