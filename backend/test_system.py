"""系统测试脚本：运行 TC-01~TC-14 测试用例并输出结果。

用法：在 backend 目录下执行
    .venv/bin/python test_system.py
"""

import json
import sys

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

RESULTS = []


def check(tc_id, name, method, path, payload=None, expects=None, contains=None, status=None):
    """执行一个测试用例并记录结果。"""
    try:
        if method == "POST":
            resp = client.post(path, json=payload)
        else:
            resp = client.get(path)
        body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        ok_status = (status is None) or (resp.status_code == status)
        ok_contains = True
        if contains:
            ok_contains = all(c in (body.get("reply", "") if isinstance(body, dict) else str(body)) for c in contains)
        passed = ok_status and ok_contains
        # 提取关键信息用于展示
        if isinstance(body, dict) and "reply" in body:
            actual = f"[{resp.status_code}] intent={body.get('intent')} reply={body['reply'][:80]}..."
        else:
            actual = f"[{resp.status_code}] {json.dumps(body, ensure_ascii=False)[:120]}"
        RESULTS.append((tc_id, name, passed, actual))
        print(f"{'PASS' if passed else 'FAIL'}  {tc_id} {name}: {actual}")
    except Exception as e:
        RESULTS.append((tc_id, name, False, f"异常: {e}"))
        print(f"FAIL  {tc_id} {name}: 异常 {e}")


def main():
    print("=" * 70)
    print("校园学生智能体 系统测试")
    print("=" * 70)

    # ---- 用户管理 ----
    check("TC-03", "注册新用户", "POST", "/auth/register",
          {"username": "tester", "password": "123456", "name": "测试员"}, status=200)
    check("TC-01", "正确登录", "POST", "/auth/login",
          {"username": "tester", "password": "123456"}, status=200)
    check("TC-02", "错误登录", "POST", "/auth/login",
          {"username": "tester", "password": "wrongpass"}, status=401)

    # ---- 校园智能问答（RAG）----
    check("TC-04", "奖学金问答(RAG)", "POST", "/chat",
          {"message": "国家奖学金要什么条件？", "user_id": 1}, contains=["奖学金"])
    check("TC-05", "知识库无结果", "POST", "/chat",
          {"message": "今天股市大盘怎么样？", "user_id": 1})

    # ---- 学习辅导 ----
    check("TC-06", "课程答疑", "POST", "/chat",
          {"message": "请解释数据库事务", "user_id": 1})
    check("TC-07", "资源推荐", "POST", "/chat",
          {"message": "推荐一些数据结构学习资料", "user_id": 1})

    # ---- 教务信息查询（工具调用）----
    check("TC-08", "课表查询", "POST", "/chat",
          {"message": "查一下我的课表", "user_id": 1}, contains=["软件工程"])
    check("TC-09", "成绩查询", "POST", "/chat",
          {"message": "我的成绩是多少？", "user_id": 1}, contains=["软件工程"])

    # ---- 校园生活服务 ----
    check("TC-10", "通知公告查询", "POST", "/chat",
          {"message": "食堂几点开门？", "user_id": 1})

    # ---- 心理陪伴 ----
    check("TC-11", "情绪疏导", "POST", "/chat",
          {"message": "最近压力好大，心情很糟", "user_id": 1})

    # ---- 个性化学习规划 ----
    check("TC-12", "学习计划", "POST", "/chat",
          {"message": "帮我制定一个学习计划", "user_id": 1})

    # ---- 知识库管理 ----
    check("TC-13", "文档录入", "POST", "/admin/documents",
          {"title": "测试文档", "category": "测试", "content": "这是用于测试的知识库文档内容。"}, status=200)
    check("TC-13b", "文档列表", "GET", "/admin/documents", status=200)
    # 删除刚创建的文档（验证 Chroma 清理），动态获取 id
    try:
        created = client.post("/admin/documents", json={
            "title": "待删除文档", "category": "测试", "content": "用于删除测试的内容。"}).json()
        did = created.get("id")
        resp = client.delete(f"/admin/documents/{did}")
        ok = resp.status_code == 200 and resp.json().get("chunks_removed", -1) >= 0
        RESULTS.append(("TC-15", "文档删除(清理Chroma)", ok, f"[{resp.status_code}] {resp.text[:80]}"))
        print(f"{'PASS' if ok else 'FAIL'}  TC-15 文档删除: [{resp.status_code}] {resp.text[:80]}")
    except Exception as e:
        RESULTS.append(("TC-15", "文档删除", False, f"异常: {e}"))
        print(f"FAIL  TC-15 文档删除: 异常 {e}")

    # ---- 意图识别 ----
    r = client.post("/chat", json={"message": "食堂几点开门？", "user_id": 1}).json()
    intent = r.get("intent")
    passed = intent == "qa"
    RESULTS.append(("TC-14", "意图识别(知识问答)", passed, f"intent={intent}"))
    print(f"{'PASS' if passed else 'FAIL'}  TC-14 意图识别: intent={intent}")

    # ---- 规划意图（验证路由修复）----
    r = client.post("/chat", json={"message": "帮我制定一个学习计划", "user_id": 1}).json()
    intent = r.get("intent")
    passed = intent == "planning"
    RESULTS.append(("TC-16", "意图识别(学习规划)", passed, f"intent={intent}"))
    print(f"{'PASS' if passed else 'FAIL'}  TC-16 意图识别(学习规划): intent={intent}")

    # ---- 流式接口 ----
    try:
        resp = client.post("/chat/stream", json={"message": "国家奖学金要什么条件？", "user_id": 1})
        body = resp.text
        ok = resp.status_code == 200 and '"intent"' in body and '"token"' in body
        RESULTS.append(("TC-17", "流式接口(SSE)", ok, f"[{resp.status_code}] 含intent/token事件={ok}"))
        print(f"{'PASS' if ok else 'FAIL'}  TC-17 流式接口: [{resp.status_code}]")
    except Exception as e:
        RESULTS.append(("TC-17", "流式接口", False, f"异常: {e}"))
        print(f"FAIL  TC-17 流式接口: {e}")

    # ---- 文件上传 ----
    try:
        resp = client.post("/admin/upload",
                           files={"file": ("上传测试.txt", "这是上传测试的文档内容。".encode("utf-8"), "text/plain")})
        body = resp.json()
        ok = resp.status_code == 200 and body.get("id")
        RESULTS.append(("TC-18", "文件上传", ok, f"[{resp.status_code}] {body}"))
        print(f"{'PASS' if ok else 'FAIL'}  TC-18 文件上传: [{resp.status_code}] {body}")
    except Exception as e:
        RESULTS.append(("TC-18", "文件上传", False, f"异常: {e}"))
        print(f"FAIL  TC-18 文件上传: {e}")

    # ---- 汇总 ----
    print("=" * 70)
    passed = sum(1 for _, _, p, _ in RESULTS if p)
    total = len(RESULTS)
    print(f"结果：{passed}/{total} 通过")
    for tid, name, p, _ in RESULTS:
        if not p:
            print(f"  未通过: {tid} {name}")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
