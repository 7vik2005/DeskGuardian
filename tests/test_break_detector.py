from datetime import datetime, timedelta
import logging

from modules.behavior_tracking.break_detector import BreakDetector


logger = logging.getLogger(__name__)


def test_break_detector_start_and_end(monkeypatch):
    logger.info("TC04 Step 1: Initialize BreakDetector and fake datetime")
    detector = BreakDetector()
    base = datetime(2026, 1, 1, 9, 0, 0)

    class FakeDatetime:
        current = base

        @classmethod
        def now(cls):
            return cls.current

    monkeypatch.setattr("modules.behavior_tracking.break_detector.datetime", FakeDatetime)

    # User present.
    logger.info("TC04 Step 2: Face detected at base time, expect no break event")
    assert detector.update_face_status(True) is None

    # No break yet (below threshold).
    FakeDatetime.current = base + timedelta(seconds=5)
    logger.info("TC04 Step 3: Face absent for 5s (< threshold), expect no break")
    assert detector.update_face_status(False) is None

    # Break starts after threshold.
    FakeDatetime.current = base + timedelta(seconds=12)
    logger.info("TC04 Step 4: Face absent beyond threshold, expect BREAK_STARTED")
    started = detector.update_face_status(False)
    assert started is not None
    assert started["event"] == "BREAK_STARTED"
    logger.info("TC04 BREAK_STARTED payload: %s", started)

    # User returns and break ends.
    FakeDatetime.current = base + timedelta(seconds=25)
    logger.info("TC04 Step 5: Face detected again, expect BREAK_ENDED")
    ended = detector.update_face_status(True)
    assert ended is not None
    assert ended["event"] == "BREAK_ENDED"
    assert ended["duration_minutes"] > 0
    logger.info("TC04 BREAK_ENDED payload: %s", ended)
    logger.info("TC04 Result: PASS")
