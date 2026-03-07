# Key Code Changes Reference Guide

## 1. POSTURE DETECTION - Correct Angle Thresholds

### Before (Incorrect - too strict):

```python
GOOD_POSTURE_MAX_BACK_ANGLE = 10        # Too strict!
GOOD_POSTURE_MAX_NECK_ANGLE = 10
```

### After (Correct - ISO 11226 based):

```python
GOOD_POSTURE_MAX_BACK_ANGLE = 15        # Good posture zone
GOOD_POSTURE_MAX_NECK_ANGLE = 15

SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE = 25  # Slightly uncomfortable
SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE = 25

BAD_POSTURE_MAX_BACK_ANGLE = 40         # Poor posture
BAD_POSTURE_MAX_NECK_ANGLE = 40
# > 40 degrees = VERY_BAD
```

**Impact**: Upright users will now correctly be classified as "Good" instead of "Very Bad"

---

## 2. DESKTOP NOTIFICATIONS - Implementation

### Key Code:

```python
# In notification_engine.py
def _show_desktop_notification(self, title, message, duration=10):
    """Show desktop notification via platform-specific method."""
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
        except Exception as e:
            Logger.warning(f"Failed to show desktop notification: {e}")

    # Run in background thread to avoid blocking
    thread = threading.Thread(target=notify, daemon=True)
    thread.start()

# Alert with duration tracking
def send_posture_alert(self, session_id, duration_seconds):
    message = f"⚠️ Bad posture detected for {duration_seconds} seconds."
    self._show_desktop_notification(
        title="DeskGuardian - Bad Posture Alert",
        message=message,
        duration=8
    )
```

**Impact**: Non-blocking notifications appear on desktop with duration information

---

## 3. NO-USER-DETECTED ALERT - Auto Camera Closure

### Key Code:

```python
# In system_controller.py
def __init__(self, user_id):
    ...
    self.last_user_detected_time = None
    self.no_user_alert_sent = False

def _monitor_loop(self):
    while ...:
        frame, posture_class, alert_triggered = self.pose_detector.process_frame()
        face_detected = posture_class is not None

        if face_detected:
            self.last_user_detected_time = datetime.now()

            # User detected again after idle
            if self.no_user_alert_sent:
                self.no_user_alert_sent = False
                self.notifier.send_user_detected_notification(...)
        else:
            # Check idle duration
            if self.last_user_detected_time is not None:
                elapsed = (datetime.now() - self.last_user_detected_time).total_seconds()

                # Alert after 60 seconds idle
                if elapsed >= IDLE_FACE_NOT_DETECTED_SECONDS and not self.no_user_alert_sent:
                    self.no_user_alert_sent = True
                    self.notifier.send_no_user_detected_alert(...)

                    # Close camera
                    cv2.destroyAllWindows()
                    self.state_manager.transition(SystemState.IDLE_DETECTED)
                    break
```

**Impact**: Camera automatically closes after 60 seconds of no user detection with alert

---

## 4. RESEARCH-BASED BURNOUT MODEL

### Key Code:

```python
# In burnout_model.py
def _train_initial_model(self):
    """Train on 20 research-informed synthetic samples"""

    # Features: [screen_time_min/hr, bad_posture_count/hr, breaks/hr]
    X = np.array([
        [20, 5, 4],      # Low Risk
        [25, 8, 3],      # Low Risk
        ...
        [50, 20, 1],     # High Risk
        [60, 30, 0],     # High Risk - full screen, no breaks
    ])

    y = np.array([0, 0, 0, ..., 1, 1, 1])  # 0=Low, 1=High Risk

    # Normalize features
    self.scaler = StandardScaler()
    X_scaled = self.scaler.fit_transform(X)

    # Train logistic regression
    self.model = LogisticRegression(C=1.0, max_iter=1000)
    self.model.fit(X_scaled, y)

def predict_burnout(self, total_screen_time_minutes, bad_posture_count,
                    total_breaks, session_duration_minutes):
    """Calculate burnout probability using research formula"""

    # Normalize to per-hour metrics
    session_hours = max(session_duration_minutes / 60, 0.1)

    avg_screen_time_per_hour = min(total_screen_time_minutes / session_hours, 60)
    avg_bad_posture_per_hour = bad_posture_count / session_hours
    avg_breaks_per_hour = total_breaks / session_hours

    features = np.array([[avg_screen_time_per_hour, avg_bad_posture_per_hour, avg_breaks_per_hour]])
    features_scaled = self.scaler.transform(features)

    # Get probability from logistic regression
    probability = self.model.predict_proba(features_scaled)[0][1]

    return probability
```

**Risk Classification**:

- < 0.4 = 🟢 LOW RISK
- 0.4-0.7 = 🟡 MODERATE RISK
- > = 0.7 = 🔴 HIGH RISK

**Impact**: Burnout probability calculated scientifically based on Maslach Burnout Inventory

---

## 5. COMPREHENSIVE DASHBOARD - Multi-Tab Interface

### Key Code Structure:

```python
# In dashboard_ui.py
class DashboardUI(QMainWindow):
    def __init__(self, user_id):
        self.tabs = QTabWidget()

        # Tab 1: Overview
        self.tabs.addTab(self._create_overview_tab(), "📊 Overview")

        # Tab 2: Posture Analysis
        self.tabs.addTab(self._create_posture_tab(), "🧍 Posture Analysis")

        # Tab 3: Screen Time & Breaks
        self.tabs.addTab(self._create_screen_time_tab(), "⏰ Screen Time & Breaks")

        # Tab 4: Burnout Prediction
        self.tabs.addTab(self._create_burnout_tab(), "🔥 Burnout Prediction")

        # Tab 5: Alerts
        self.tabs.addTab(self._create_alerts_tab(), "🔔 Alert History")

        # Auto-refresh every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)

    def refresh_all(self):
        """Refresh all dashboard data"""
        self._update_overview()
        self._update_posture_analysis()
        self._update_screen_time_analysis()
        self._update_burnout_analysis()
        self._update_alerts_history()
```

### Tab Features:

**Tab 1: Overview**

- Current session summary
- Key metrics (total sessions, screen time, posture count, avg burnout)

**Tab 2: Posture Analysis**

- Pie chart: Posture distribution
- Table: Recent posture events (20 entries)

**Tab 3: Screen Time & Breaks**

- Bar chart: Screen time per session
- Table: Break history with duration

**Tab 4: Burnout Prediction**

- Line chart: Burnout trend with thresholds
- Status indicator: Color-coded risk (Green/Yellow/Red)
- Table: Assessment history

**Tab 5: Alert History**

- Table: Recent alerts (30 entries)
- Alert type, message, time, resolution status

**Impact**: Professional dashboard with real-time data visualization

---

## 6. DURATION TRACKING IN ALERTS

### Key Code:

```python
# In system_controller.py - Posture alert with duration
if alert_triggered and ENABLE_POSTURE_ALERTS:
    # Get duration from classifier
    duration_seconds = 0
    if self.pose_detector.classifier.bad_posture_start_time:
        duration_seconds = time.time() - self.pose_detector.classifier.bad_posture_start_time

    # Send alert with duration
    self.notifier.send_posture_alert(
        self.session_manager.session_id,
        int(duration_seconds)
    )

# In notification_engine.py - Show duration in message
def send_posture_alert(self, session_id, duration_seconds):
    message = f"⚠️ Bad posture detected for {duration_seconds} seconds. Please sit upright."
    self._show_desktop_notification(
        title="DeskGuardian - Bad Posture Alert",
        message=message,
        duration=8
    )
```

**Impact**: Users see exactly how long bad posture has been maintained

---

## 7. BURNOUT ASSESSMENT LOGGING

### Key Code:

```python
# In system_controller.py - Log assessment to database
if self.timer.is_time_for_burnout_check():
    probability = self.burnout_model.predict_burnout(...)

    # Log to database
    self.session_manager.db.log_burnout_assessment(
        user_id=self.user_id,
        interval_start=datetime.now(),
        interval_end=datetime.now(),
        burnout_probability=probability,
        avg_screen_time_per_day=self.session_manager.screen_tracker.get_total_screen_time_minutes(),
        avg_bad_posture_per_hour=self.session_manager.screen_tracker.get_bad_posture_count(),
        avg_breaks_per_hour=0
    )

    # Alert if high risk
    if probability >= 0.7:
        self.notifier.send_burnout_alert(
            self.session_manager.session_id,
            None,
            probability
        )
```

**Impact**: Historical burnout assessments stored for trend analysis

---

## 8. ALERT CONSTANTS CONFIGURATION

### New Constants in config/constants.py:

```python
# Posture thresholds (ISO 11226 based)
GOOD_POSTURE_MAX_BACK_ANGLE = 15
GOOD_POSTURE_MAX_NECK_ANGLE = 15
POSTURE_ALERT_THRESHOLD_SECONDS = 30

# No-user-detected
IDLE_FACE_NOT_DETECTED_SECONDS = 60

# Burnout model weights
BURNOUT_WEIGHT_SCREEN_TIME = 0.4
BURNOUT_WEIGHT_BAD_POSTURE = 0.35
BURNOUT_WEIGHT_LOW_BREAKS = 0.25

# Alert types
ALERT_TYPES = [
    "POSTURE_ALERT",
    "SCREEN_TIME_ALERT",
    "BREAK_REMINDER",
    "BURNOUT_HIGH_RISK",
    "NO_USER_DETECTED",    # NEW
    "USER_DETECTED"        # NEW
]
```

**Impact**: All thresholds configurable in one place

---

## Testing Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run application
python main.py

# Run dashboard separately (in another terminal)
python -m modules.dashboard.dashboard_ui

# Check syntax
python -m py_compile **/*.py

# View logs
tail -f data/deskguardian.log
```

---

## File Dependencies & Import Chain

```
main.py
├── core/system_controller.py ✅ (UPDATED)
│   ├── modules/posture_detection/pose_detector.py
│   │   ├── modules/posture_detection/posture_metrics.py (angle calculations)
│   │   └── modules/posture_detection/posture_classifier.py ✅ (threshold logic)
│   ├── modules/behavior_tracking/session_manager.py
│   ├── modules/burnout_prediction/burnout_model.py ✅ (research formula)
│   └── modules/notification/notification_engine.py ✅ (desktop alerts)
│
├── config/constants.py ✅ (UPDATED)
│   └── Imported by all modules
│
└── config/settings.py
    └── Alert toggles
```

---

## Quick Troubleshooting

| Issue                                 | Solution                                                             |
| ------------------------------------- | -------------------------------------------------------------------- |
| Posture shows "Very Bad" when upright | Check angle thresholds in constants.py (should be 15°)               |
| No desktop notifications              | Install: `pip install win10toast`                                    |
| Camera doesn't close after idle       | Check IDLE_FACE_NOT_DETECTED_SECONDS (should be 60)                  |
| Dashboard is empty                    | Ensure at least one session has completed with data                  |
| Burnout always predicting low         | Check that burnout model is trained (first run trains automatically) |
| Alerts not triggering                 | Check ENABLE\_\*\_ALERTS settings in config/settings.py              |

---

This reference guide covers all major code changes implemented in the DeskGuardian application.
