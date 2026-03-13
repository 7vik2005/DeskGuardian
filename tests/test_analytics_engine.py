from datetime import datetime, timedelta
from pathlib import Path
import logging

from database.db_manager import DBManager
from modules.dashboard.analytics_engine import AnalyticsEngine


logger = logging.getLogger(__name__)


def test_analytics_summary_and_trends(monkeypatch, tmp_path: Path):
    logger.info("TC07 Step 1: Configure temporary database for analytics integration")
    temp_db = tmp_path / "analytics_test.db"
    monkeypatch.setattr("database.db_manager.DATABASE_NAME", str(temp_db))

    db = DBManager()
    logger.info("TC07 Temp DB Path: %s", temp_db)

    logger.info("TC07 Step 2: Seed user, session, posture events, burnout assessment")
    user_id = db.create_user("bob", "fakehash", 30, "Analyst")
    session_id = db.start_session(user_id)

    db.log_posture_event(session_id, "Good", 5.0, 6.0, 0.2, False)
    db.log_posture_event(session_id, "Bad", 28.0, 31.0, 1.1, True)
    db.log_burnout_assessment(
        user_id=user_id,
        interval_start=datetime.now() - timedelta(minutes=10),
        interval_end=datetime.now(),
        burnout_probability=0.63,
        avg_screen_time_per_day=42.0,
        avg_bad_posture_per_hour=5.0,
        avg_breaks_per_hour=1.0,
    )
    db.end_session(session_id)
    db.close()

    logger.info("TC07 Step 3: Query analytics outputs")
    analytics = AnalyticsEngine(user_id)

    summary = analytics.get_session_summary()
    logger.info("TC07 Summary Output: %s", summary)
    assert summary["total_sessions"] >= 1

    distribution = analytics.get_posture_distribution()
    logger.info("TC07 Distribution Output: %s", distribution)
    classes = {row["posture_class"] for row in distribution}
    assert "Good" in classes
    assert "Bad" in classes

    current = analytics.get_current_burnout_risk()
    logger.info("TC07 Current Burnout Output: %s", current)
    assert current is not None
    assert 0.0 <= current["burnout_probability"] <= 1.0

    analytics.db.close()
    logger.info("TC07 Result: PASS")
