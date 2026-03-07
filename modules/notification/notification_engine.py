from datetime import datetime
import threading
from utils.enums import AlertType
from database.db_manager import DBManager
from utils.logger import Logger

try:
    import win10toast
    HAS_WIN10TOAST = True
except ImportError:
    HAS_WIN10TOAST = False
    Logger.warning("win10toast not available. Desktop notifications disabled on Windows.")

try:
    import pynotify
    HAS_PYNOTIFY = True
except ImportError:
    HAS_PYNOTIFY = False


class NotificationEngine:
    """
    Handles:
    - Alert display (console + desktop notifications)
    - Logging alerts to database
    - Cross-platform notification support (Windows + Linux)
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.db = DBManager()

    # ======================================
    # SEND DESKTOP NOTIFICATION
    # ======================================

    def _show_desktop_notification(self, title, message, duration=10):
        """
        Show desktop notification via platform-specific method.
        Runs in background thread to avoid blocking.
        """
        def notify():
            try:
                if HAS_WIN10TOAST:
                    # Windows 10+ notification
                    win10toast.ToastNotifier().show_toast(
                        title=title,
                        msg=message,
                        duration=duration,
                        threaded=True
                    )
                elif HAS_PYNOTIFY:
                    # Linux notification
                    pynotify.init("DeskGuardian")
                    notification = pynotify.Notification(title, message)
                    notification.show()
                else:
                    Logger.warning("No notification library available.")
            except Exception as e:
                Logger.warning(f"Failed to show desktop notification: {e}")

        # Run notification in background thread to avoid blocking main loop
        thread = threading.Thread(target=notify, daemon=True)
        thread.start()

    # ======================================
    # POSTURE ALERT
    # ======================================

    def send_posture_alert(self, session_id, duration_seconds):
        """Send alert for bad posture maintained for a period of time."""
        message = f"⚠️ Bad posture detected for {duration_seconds} seconds. Please sit upright."

        Logger.info(f"[ALERT] POSTURE: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - Bad Posture Alert",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.POSTURE_ALERT.value,
            message=message
        )

    # ======================================
    # SCREEN TIME ALERT
    # ======================================

    def send_screen_time_alert(self, session_id, screen_time_minutes):
        message = f"⏰ You have been working for {screen_time_minutes} minutes. Consider taking a break."

        Logger.info(f"[ALERT] SCREEN TIME: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - Screen Time Alert",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.SCREEN_TIME_ALERT.value,
            message=message
        )

    # ======================================
    # BREAK REMINDER
    # ======================================

    def send_break_reminder(self, session_id):
        message = "🏃 Time for a break! Stretch, walk, and relax your eyes."

        Logger.info(f"[ALERT] BREAK REMINDER: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - Break Reminder",
            message=message,
            duration=8
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type=AlertType.BREAK_REMINDER.value,
            message=message
        )

    # ======================================
    # BURNOUT HIGH RISK ALERT
    # ======================================

    def send_burnout_alert(self, session_id, assessment_id, burnout_probability):
        message = f"🔥 High burnout risk detected (Probability: {burnout_probability:.1%}). Please take immediate rest."

        Logger.warning(f"[ALERT] BURNOUT HIGH RISK: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - Burnout Risk Alert",
            message=message,
            duration=10
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=assessment_id,
            alert_type=AlertType.BURNOUT_HIGH_RISK.value,
            message=message
        )

    # ======================================
    # NO USER DETECTED ALERT
    # ======================================

    def send_no_user_detected_alert(self, session_id, idle_seconds):
        message = f"👤 No user detected for {idle_seconds} seconds. Closing camera to save resources."

        Logger.warning(f"[ALERT] NO USER DETECTED: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - No User Detected",
            message=message,
            duration=5
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type="NO_USER_DETECTED",
            message=message
        )

    # ======================================
    # USER RE-DETECTED NOTIFICATION
    # ======================================

    def send_user_detected_notification(self, session_id):
        message = "✅ User detected. Resuming monitoring..."

        Logger.info(f"[INFO] USER DETECTED: {message}")

        self._show_desktop_notification(
            title="DeskGuardian - Monitoring Resumed",
            message=message,
            duration=3
        )

        self.db.log_alert(
            user_id=self.user_id,
            session_id=session_id,
            assessment_id=None,
            alert_type="USER_DETECTED",
            message=message
        )

