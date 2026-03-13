import logging

from modules.notification.notification_engine import NotificationEngine


logger = logging.getLogger(__name__)


def test_notification_cooldown_and_logging(monkeypatch):
    logger.info("TC06 Step 1: Prepare fake DB and popup trackers")
    calls = {"popup": 0, "logs": 0}

    class FakeDB:
        def log_alert(self, **kwargs):
            calls["logs"] += 1

    monkeypatch.setattr("modules.notification.notification_engine.DBManager", lambda: FakeDB())
    monkeypatch.setattr(
        "modules.notification.notification_engine.show_popup",
        lambda *args, **kwargs: calls.__setitem__("popup", calls["popup"] + 1),
    )

    fake_time = {"value": 1000.0}

    class FakeTimeModule:
        @staticmethod
        def time():
            return fake_time["value"]

    monkeypatch.setattr("modules.notification.notification_engine._time", FakeTimeModule)

    logger.info("TC06 Step 2: Initialize NotificationEngine with mocked dependencies")
    engine = NotificationEngine(user_id=1)

    logger.info("TC06 Step 3: Send first posture alert at t=1000 (popup expected)")
    engine.send_posture_alert(session_id=1, duration_seconds=12)
    assert calls["popup"] == 1
    assert calls["logs"] == 1
    logger.info("TC06 Counters after first alert: %s", calls)

    # Within cooldown: popup suppressed, DB log still happens.
    fake_time["value"] = 1005.0
    logger.info("TC06 Step 4: Send second alert within cooldown at t=1005 (popup suppressed)")
    engine.send_posture_alert(session_id=1, duration_seconds=14)
    assert calls["popup"] == 1
    assert calls["logs"] == 2
    logger.info("TC06 Counters after second alert: %s", calls)

    # After cooldown: popup allowed again.
    fake_time["value"] = 1035.0
    logger.info("TC06 Step 5: Send third alert after cooldown at t=1035 (popup expected)")
    engine.send_posture_alert(session_id=1, duration_seconds=20)
    assert calls["popup"] == 2
    assert calls["logs"] == 3
    logger.info("TC06 Final counters: %s", calls)
    logger.info("TC06 Result: PASS")
