"""P6.5 强化测试：tool failure、clarification 续接/放弃、store、latency。"""

from fastapi.testclient import TestClient

from app.application import orchestrator
from app.domain.agent import CampusAgent
from app.domain.clarification import ClarificationStore, PendingClarification, clarification_store
from app.infrastructure.db import Base, engine, SessionLocal
from app.main import app


def test_tool_failure():
    agent = CampusAgent()
    out = agent.run("查一下我的成绩单")
    assert out.error == "教务系统暂时不可用，请稍后重试", f"error={out.error}"
    assert out.retryable is True


def test_clarification_store():
    s = ClarificationStore()
    s.set(1, PendingClarification(intent="academic", pending_tool="query_timetable", missing_params=["student_group"]))
    assert s.get(1).pending_tool == "query_timetable"
    s.clear(1)
    assert s.get(1) is None


def test_clarification_continuation():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        out1, conv_id, _ = orchestrator.run(db, "查一下我的课表", 1, None)
        assert out1.clarification is not None
        assert out1.clarification["tool"] == "query_timetable"
        assert clarification_store.get(conv_id) is not None

        out2, _, _ = orchestrator.run(db, "A班", 1, conv_id)
        assert out2.clarification is None
        assert out2.error is None
        assert "软件工程" in out2.answer, f"answer={out2.answer[:80]}"
        assert clarification_store.get(conv_id) is None
    finally:
        db.close()


def test_clarification_abandoned():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        out1, conv_id, _ = orchestrator.run(db, "查一下我的课表", 1, None)
        assert out1.clarification is not None

        out2, _, _ = orchestrator.run(db, "图书馆借书能借几本", 1, conv_id)
        assert out2.clarification is None
        assert clarification_store.get(conv_id) is None
    finally:
        db.close()


def test_latency_in_done():
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    resp = client.post("/chat/stream", json={"message": "查A班的课表", "user_id": 1})
    assert resp.status_code == 200
    assert '"latency_ms"' in resp.text
    assert '"run_id"' in resp.text


def main():
    tests = [test_tool_failure, test_clarification_store, test_clarification_continuation,
             test_clarification_abandoned, test_latency_in_done]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n结果：{passed}/{len(tests)} 通过")


if __name__ == "__main__":
    main()
