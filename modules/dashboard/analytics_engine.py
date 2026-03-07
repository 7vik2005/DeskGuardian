from datetime import datetime, timedelta
from database.db_manager import DBManager
from utils.logger import Logger


class AnalyticsEngine:
    """
    Analytics Engine for DeskGuardian Dashboard

    Provides data aggregation and analysis for:
    - Session summaries
    - Posture distribution
    - Screen time analysis
    - Break frequency
    - Burnout trends
    - Alert history
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DBManager()

    # ======================================
    # SESSION SUMMARY
    # ======================================

    def get_session_summary(self):
        """Get aggregated summary of all sessions."""
        try:
            self.db.cursor.execute("""
                SELECT
                    COUNT(*) as total_sessions,
                    SUM(total_screen_time_minutes) as total_screen_time_minutes,
                    SUM(bad_posture_count) as total_bad_posture_count,
                    MAX(end_time) as last_session_end
                FROM Session
                WHERE user_id = ?
            """, (self.user_id,))

            result = self.db.cursor.fetchone()

            if result:
                return {
                    "total_sessions": result[0] or 0,
                    "total_screen_time_minutes": result[1] or 0,
                    "total_bad_posture_count": result[2] or 0,
                    "last_session_end": result[3],
                    "session_active": self._is_session_active(),
                    "session_duration_minutes": self._get_current_session_duration(),
                    "current_screen_time_minutes": self._get_current_screen_time(),
                    "avg_burnout_probability": self._get_avg_burnout_probability(),
                }
            else:
                return {
                    "total_sessions": 0,
                    "total_screen_time_minutes": 0,
                    "total_bad_posture_count": 0,
                    "session_active": False,
                    "session_duration_minutes": 0,
                    "current_screen_time_minutes": 0,
                    "avg_burnout_probability": 0,
                }
        except Exception as e:
            Logger.error(f"Error getting session summary: {e}")
            return {}

    def _is_session_active(self):
        """Check if there's an active session."""
        try:
            self.db.cursor.execute("""
                SELECT 1 FROM Session
                WHERE user_id = ? AND end_time IS NULL
                LIMIT 1
            """, (self.user_id,))
            return self.db.cursor.fetchone() is not None
        except:
            return False

    def _get_current_session_duration(self):
        """Get current active session duration in minutes."""
        try:
            self.db.cursor.execute("""
                SELECT start_time FROM Session
                WHERE user_id = ? AND end_time IS NULL
                ORDER BY session_id DESC
                LIMIT 1
            """, (self.user_id,))

            result = self.db.cursor.fetchone()
            if result:
                start_time = datetime.fromisoformat(result[0])
                return (datetime.now() - start_time).total_seconds() / 60
            return 0
        except:
            return 0

    def _get_current_screen_time(self):
        """Get current active session screen time."""
        try:
            self.db.cursor.execute("""
                SELECT total_screen_time_minutes FROM Session
                WHERE user_id = ? AND end_time IS NULL
                ORDER BY session_id DESC
                LIMIT 1
            """, (self.user_id,))

            result = self.db.cursor.fetchone()
            return result[0] if result else 0
        except:
            return 0

    def _get_avg_burnout_probability(self):
        """Get average burnout probability across all assessments."""
        try:
            self.db.cursor.execute("""
                SELECT AVG(burnout_probability) FROM BurnoutAssessment
                WHERE user_id = ?
            """, (self.user_id,))

            result = self.db.cursor.fetchone()
            return result[0] if result and result[0] else 0
        except:
            return 0

    # ======================================
    # POSTURE ANALYSIS
    # ======================================

    def get_posture_distribution(self):
        """Get distribution of posture classifications."""
        try:
            self.db.cursor.execute("""
                SELECT posture_class, COUNT(*) as count
                FROM PostureEvent
                WHERE session_id IN (
                    SELECT session_id FROM Session WHERE user_id = ?
                )
                GROUP BY posture_class
                ORDER BY count DESC
            """, (self.user_id,))

            results = self.db.cursor.fetchall()
            return [{"posture_class": row[0], "count": row[1]} for row in results]
        except Exception as e:
            Logger.error(f"Error getting posture distribution: {e}")
            return []

    def get_recent_posture_events(self, limit=20):
        """Get recent posture events."""
        try:
            self.db.cursor.execute("""
                SELECT
                    timestamp,
                    posture_class,
                    0 as duration,
                    is_alert_triggered
                FROM PostureEvent
                WHERE session_id IN (
                    SELECT session_id FROM Session WHERE user_id = ?
                )
                ORDER BY timestamp DESC
                LIMIT ?
            """, (self.user_id, limit))

            results = self.db.cursor.fetchall()
            return [
                {
                    "timestamp": row[0],
                    "posture_class": row[1],
                    "duration": row[2],
                    "is_alert_triggered": bool(row[3])
                }
                for row in results
            ]
        except Exception as e:
            Logger.error(f"Error getting posture events: {e}")
            return []

    # ======================================
    # SCREEN TIME & BREAK ANALYSIS
    # ======================================

    def get_screen_time_by_session(self):
        """Get screen time aggregated by session."""
        try:
            self.db.cursor.execute("""
                SELECT
                    session_id,
                    total_screen_time_minutes
                FROM Session
                WHERE user_id = ?
                ORDER BY session_id DESC
                LIMIT 30
            """, (self.user_id,))

            results = self.db.cursor.fetchall()
            return [
                {
                    "session_id": row[0],
                    "total_screen_time_minutes": row[1] or 0
                }
                for row in results
            ]
        except Exception as e:
            Logger.error(f"Error getting screen time by session: {e}")
            return []

    def get_break_events(self, limit=20):
        """Get recent break events."""
        try:
            self.db.cursor.execute("""
                SELECT
                    start_time,
                    end_time,
                    duration_minutes,
                    break_type
                FROM BreakEvent
                WHERE session_id IN (
                    SELECT session_id FROM Session WHERE user_id = ?
                )
                ORDER BY start_time DESC
                LIMIT ?
            """, (self.user_id, limit))

            results = self.db.cursor.fetchall()
            return [
                {
                    "start_time": row[0],
                    "end_time": row[1],
                    "duration_minutes": row[2],
                    "break_type": row[3]
                }
                for row in results
            ]
        except Exception as e:
            Logger.error(f"Error getting break events: {e}")
            return []

    # ======================================
    # BURNOUT ANALYSIS
    # ======================================

    def get_burnout_trend(self):
        """Get burnout probability trend over time."""
        try:
            self.db.cursor.execute("""
                SELECT
                    interval_end,
                    burnout_probability,
                    avg_screen_time_per_day,
                    avg_bad_posture_per_hour,
                    avg_breaks_per_hour
                FROM BurnoutAssessment
                WHERE user_id = ?
                ORDER BY interval_end DESC
                LIMIT 30
            """, (self.user_id,))

            results = self.db.cursor.fetchall()
            return [
                {
                    "assessment_date": row[0],
                    "burnout_probability": row[1],
                    "avg_screen_time_per_day": row[2] or 0,
                    "avg_bad_posture_per_hour": row[3] or 0,
                    "avg_breaks_per_hour": row[4] or 0,
                }
                for row in results
            ]
        except Exception as e:
            Logger.error(f"Error getting burnout trend: {e}")
            return []

    def get_current_burnout_risk(self):
        """Get the most recent burnout assessment."""
        try:
            self.db.cursor.execute("""
                SELECT
                    interval_end,
                    burnout_probability,
                    avg_screen_time_per_day,
                    avg_bad_posture_per_hour
                FROM BurnoutAssessment
                WHERE user_id = ?
                ORDER BY interval_end DESC
                LIMIT 1
            """, (self.user_id,))

            result = self.db.cursor.fetchone()
            if result:
                return {
                    "assessment_date": result[0],
                    "burnout_probability": result[1],
                    "avg_screen_time_per_day": result[2] or 0,
                    "avg_bad_posture_per_hour": result[3] or 0,
                }
            return None
        except Exception as e:
            Logger.error(f"Error getting current burnout risk: {e}")
            return None

    # ======================================
    # ALERT HISTORY
    # ======================================

    def get_recent_alerts(self, limit=30):
        """Get recent alerts."""
        try:
            self.db.cursor.execute("""
                SELECT
                    alert_time,
                    alert_type,
                    message,
                    resolved
                FROM Alert
                WHERE user_id = ?
                ORDER BY alert_time DESC
                LIMIT ?
            """, (self.user_id, limit))

            results = self.db.cursor.fetchall()
            return [
                {
                    "alert_time": row[0],
                    "alert_type": row[1],
                    "message": row[2],
                    "resolved": bool(row[3])
                }
                for row in results
            ]
        except Exception as e:
            Logger.error(f"Error getting recent alerts: {e}")
            return []

    # ======================================
    # STATISTICS
    # ======================================

    def get_statistics_summary(self):
        """Get comprehensive statistics summary."""
        try:
            return {
                "sessions": self.get_session_summary(),
                "posture": self.get_posture_distribution(),
                "burnout_current": self.get_current_burnout_risk(),
            }
        except Exception as e:
            Logger.error(f"Error getting statistics summary: {e}")
            return {}
