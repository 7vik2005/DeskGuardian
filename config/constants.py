"""
DeskGuardian - Global System Constants
---------------------------------------
Central configuration file for thresholds, limits, timings, and enums.
All system modules import values from here.

Modifying values here updates system-wide behavior.

Research Papers Referenced:
- Postural Assessment: Based on ISO 11226 (Assessment of static working postures)
- Burnout Prediction: Based on Maslach Burnout Inventory (MBI) research
"""

# ===============================
# 🎥 WEBCAM & FRAME SETTINGS
# ===============================

FPS = 15  # Frames per second (SRS: 10–30 FPS requirement)
FRAME_WIDTH = 640
FRAME_HEIGHT = 480


# ===============================
# 🧍 POSTURE CLASSIFICATION
# ===============================
# Based on ISO 11226 and biomechanical research
# These thresholds define acceptable deviation angles from vertical posture

# Good Posture: Nearly perfect upright position (0-15 degrees deviation)
GOOD_POSTURE_MAX_BACK_ANGLE = 15
GOOD_POSTURE_MAX_NECK_ANGLE = 15

# Slightly Bad: Acceptable but not ideal (15-25 degrees deviation)
SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE = 25
SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE = 25

# Bad: Concerning levels of forward lean/head tilt (25-40 degrees deviation)
BAD_POSTURE_MAX_BACK_ANGLE = 40
BAD_POSTURE_MAX_NECK_ANGLE = 40

# Very Bad: Critical posture issues (>40 degrees deviation)
# Auto-classified as PostureClass.VERY_BAD if exceeds bad thresholds

# Posture class labels (Domain constraint - enum values)
POSTURE_CLASSES = [
    "Good",
    "Slightly Bad",
    "Bad",
    "Very Bad"
]

# Alert trigger threshold: Send alert after continuous bad/very bad posture
POSTURE_ALERT_THRESHOLD_SECONDS = 30  # 30 seconds of continuous bad posture


# ===============================
# ⏳ SCREEN TIME & BREAK DETECTION
# ===============================

# Continuous screen usage alert threshold
CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES = 45

# Break detection threshold (SRS FR-3: 2 minutes)
BREAK_THRESHOLD_SECONDS = 120

# No user detected timeout: Alert after user not detected for 60 seconds
IDLE_FACE_NOT_DETECTED_SECONDS = 60


# ===============================
# 🔥 BURNOUT PREDICTION
# ===============================
# Based on Maslach Burnout Inventory (MBI) research
# Features: Screen Time, Posture Quality, Break Frequency

# Burnout risk classification thresholds
LOW_RISK_THRESHOLD = 0.4
HIGH_RISK_THRESHOLD = 0.7

# Burnout evaluation interval (in minutes)
BURNOUT_EVALUATION_INTERVAL_MINUTES = 30

# Domain constraint (SRS)
BURNOUT_PROBABILITY_MIN = 0.0
BURNOUT_PROBABILITY_MAX = 1.0

# Burnout feature weights (research-based)
BURNOUT_WEIGHT_SCREEN_TIME = 0.4  # Higher screen time = higher burnout
BURNOUT_WEIGHT_BAD_POSTURE = 0.35  # Poor posture correlation with fatigue
BURNOUT_WEIGHT_LOW_BREAKS = 0.25  # Lack of breaks increases burnout


# ===============================
# 🔔 ALERT TYPES (Enum Constraint)
# ===============================

ALERT_TYPES = [
    "POSTURE_ALERT",
    "SCREEN_TIME_ALERT",
    "BREAK_REMINDER",
    "BURNOUT_HIGH_RISK",
    "NO_USER_DETECTED",
    "USER_DETECTED"
]


# ===============================
# 🗄 DATABASE CONFIG
# ===============================

DATABASE_NAME = "data/deskguardian.db"


# ===============================
# 🖥 DASHBOARD CONFIG
# ===============================

DASHBOARD_REFRESH_INTERVAL_MS = 3000


# ===============================
# 🧠 SYSTEM STATES (State Diagram)
# ===============================

SYSTEM_STATES = [
    "IDLE",
    "INITIALIZING",
    "MONITORING",
    "WEBCAM_ERROR",
    "GOOD_POSTURE",
    "BAD_POSTURE",
    "IDLE_DETECTED",
    "BREAK_DETECTED",
    "BURNOUT_CHECK",
    "LOW_RISK",
    "HIGH_RISK",
    "STOPPED"
]
