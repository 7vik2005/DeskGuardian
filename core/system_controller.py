import cv2
from datetime import datetime
import time

from core.state_manager import StateManager
from core.background_timer import BackgroundTimer
from modules.posture_detection.pose_detector import PoseDetector
from modules.behavior_tracking.session_manager import SessionManager
from modules.burnout_prediction.burnout_model import BurnoutModel
from modules.notification.notification_engine import NotificationEngine
from utils.enums import SystemState
from utils.logger import Logger
from config.settings import (
    ENABLE_POSTURE_ALERTS,
    ENABLE_SCREEN_TIME_ALERTS,
    ENABLE_BURNOUT_ALERTS
)
from config.constants import IDLE_FACE_NOT_DETECTED_SECONDS, POSTURE_ALERT_THRESHOLD_SECONDS


class SystemController:
    """
    Central orchestrator of DeskGuardian.
    Integrates all modules and manages runtime flow.

    Features:
    - Real-time posture detection and alerting
    - Screen time tracking with alerts
    - Break detection
    - No-user-detected timeout with alerts
    - Burnout risk prediction and alerts
    - Desktop notifications
    """

    def __init__(self, user_id):
        self.user_id = user_id

        self.state_manager = StateManager()
        self.timer = BackgroundTimer()
        self.pose_detector = PoseDetector()
        self.session_manager = SessionManager(user_id)
        self.burnout_model = BurnoutModel()
        self.notifier = NotificationEngine(user_id)

        # No-user-detected tracking
        self.last_user_detected_time = None
        self.no_user_alert_sent = False

    # ======================================
    # START SYSTEM
    # ======================================

    def start(self):
        try:
            Logger.info("System Initializing...")
            self.state_manager.transition(SystemState.INITIALIZING)

            if not self.pose_detector.is_camera_available():
                self.state_manager.transition(SystemState.WEBCAM_ERROR)
                Logger.error("Webcam not available.")
                return

            self.session_manager.start_session()
            self.timer.start_monitoring()
            self.last_user_detected_time = datetime.now()

            self.state_manager.transition(SystemState.MONITORING)
            Logger.info("Monitoring Started.")

            self._monitor_loop()

        except Exception as e:
            Logger.error(f"System Error: {e}")

        finally:
            self.shutdown()

    # ======================================
    # MAIN MONITORING LOOP
    # ======================================

    def _monitor_loop(self):

        while self.state_manager.get_state() == SystemState.MONITORING:

            frame, posture_class, alert_triggered = \
                self.pose_detector.process_frame()

            if frame is None:
                Logger.warning("Frame capture failed.")
                break

            face_detected = posture_class is not None

            # ==========================================
            # NO-USER-DETECTED HANDLING
            # ==========================================

            if face_detected:
                self.last_user_detected_time = datetime.now()

                # User detected again after no-user alert
                if self.no_user_alert_sent:
                    self.no_user_alert_sent = False
                    Logger.info("User detected. Resuming monitoring...")
                    if ENABLE_POSTURE_ALERTS:
                        self.notifier.send_user_detected_notification(
                            self.session_manager.session_id
                        )
            else:
                # Check if user has been absent for the threshold time
                if self.last_user_detected_time is not None:
                    elapsed = (datetime.now() - self.last_user_detected_time).total_seconds()

                    if elapsed >= IDLE_FACE_NOT_DETECTED_SECONDS and not self.no_user_alert_sent:
                        Logger.warning(f"No user detected for {elapsed:.0f} seconds.")
                        self.no_user_alert_sent = True

                        if ENABLE_POSTURE_ALERTS:
                            self.notifier.send_no_user_detected_alert(
                                self.session_manager.session_id,
                                int(elapsed)
                            )

                        # Close camera window automatically after alert
                        Logger.info("Closing camera window...")
                        cv2.destroyAllWindows()
                        self.state_manager.transition(SystemState.IDLE_DETECTED)
                        break

            # Update behavior/session with face detection
            break_event = self.session_manager.update(
                posture_class,
                alert_triggered,
                face_detected
            )

            # ==========================================
            # POSTURE ALERT (with duration tracking)
            # ==========================================

            if alert_triggered and ENABLE_POSTURE_ALERTS:
                # Get duration of bad posture from classifier
                duration_seconds = 0
                if self.pose_detector.classifier.bad_posture_start_time:
                    duration_seconds = time.time() - self.pose_detector.classifier.bad_posture_start_time

                Logger.warning(f"Bad posture alert triggered! Duration: {duration_seconds:.0f}s")
                self.notifier.send_posture_alert(
                    self.session_manager.session_id,
                    int(duration_seconds)
                )

            # ==========================================
            # SCREEN TIME ALERT
            # ==========================================

            if self.timer.is_screen_time_exceeded() and ENABLE_SCREEN_TIME_ALERTS:
                screen_time = self.session_manager.screen_tracker.get_total_screen_time_minutes()
                Logger.warning(f"Screen time alert triggered! Duration: {screen_time:.0f} minutes")
                self.notifier.send_screen_time_alert(
                    self.session_manager.session_id,
                    screen_time
                )

            # ==========================================
            # BREAK DETECTION
            # ==========================================

            if break_event:
                if break_event["event"] == "BREAK_STARTED":
                    Logger.info("Break detected - User away from desk")
                elif break_event["event"] == "BREAK_ENDED":
                    duration = break_event.get("duration_minutes", 0)
                    Logger.info(f"Break ended. Duration: {duration:.1f} minutes")

            # ==========================================
            # BURNOUT CHECK (Time-driven)
            # ==========================================

            if self.timer.is_time_for_burnout_check():
                self.state_manager.transition(SystemState.BURNOUT_CHECK)
                Logger.info("Running burnout evaluation...")

                probability = self.burnout_model.predict_burnout(
                    total_screen_time_minutes=
                        self.session_manager.screen_tracker.get_total_screen_time_minutes(),
                    bad_posture_count=
                        self.session_manager.screen_tracker.get_bad_posture_count(),
                    total_breaks=0,
                    session_duration_minutes=
                        self.session_manager.screen_tracker.get_session_duration_minutes()
                )

                Logger.info(f"Burnout Probability: {probability:.1%}")

                # Log burnout assessment to database
                self.session_manager.db.log_burnout_assessment(
                    user_id=self.user_id,
                    interval_start=datetime.now(),
                    interval_end=datetime.now(),
                    burnout_probability=probability,
                    avg_screen_time_per_day=
                        self.session_manager.screen_tracker.get_total_screen_time_minutes(),
                    avg_bad_posture_per_hour=
                        self.session_manager.screen_tracker.get_bad_posture_count(),
                    avg_breaks_per_hour=0
                )

                if probability >= 0.7:
                    self.state_manager.transition(SystemState.HIGH_RISK)
                    if ENABLE_BURNOUT_ALERTS:
                        Logger.warning(f"High burnout risk detected! Probability: {probability:.1%}")
                        self.notifier.send_burnout_alert(
                            self.session_manager.session_id,
                            None,
                            probability
                        )
                else:
                    self.state_manager.transition(SystemState.LOW_RISK)

                self.state_manager.transition(SystemState.MONITORING)

            # Display frame with posture information
            if frame is not None:
                cv2.imshow("DeskGuardian - Monitoring", frame)

            # Handle window close and quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                Logger.info("User requested shutdown.")
                self.state_manager.transition(SystemState.STOPPED)
                break

        self.session_manager.end_session()

    # ======================================
    # SHUTDOWN
    # ======================================

    def shutdown(self):
        try:
            self.pose_detector.release()
            cv2.destroyAllWindows()
            Logger.info("System Shutdown Complete.")
        except Exception as e:
            Logger.error(f"Error during shutdown: {e}")
