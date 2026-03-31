# 🧍 DeskGuardian - Posture & Burnout Detection System

A real-time AI-powered desktop application that monitors user posture, detects prolonged screen time, and predicts burnout risk using computer vision and machine learning — all wrapped in a modern PyQt5 graphical interface.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Building a Standalone Executable](#building-a-standalone-executable)
- [Configuration](#configuration)
- [Usage](#usage)
- [Core Modules](#core-modules)
- [Database Schema](#database-schema)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)

---

## 🎯 Overview

DeskGuardian is a comprehensive workplace wellness application designed to:

1. **Monitor Posture in Real-Time** — Uses MediaPipe pose detection to track body position via webcam
2. **Track Screen Time** — Detects prolonged continuous work sessions and suggests breaks
3. **Detect Work Breaks** — Identifies when users step away from their desk
4. **Predict Burnout Risk** — Uses a scikit-learn ML model to assess burnout probability based on posture, screen time, and break patterns
5. **Send Smart Alerts** — Delivers desktop notification popups for poor posture, excessive screen time, idle detection, and high burnout risk
6. **User Authentication** — Supports multi-user accounts with secure signup/login (hashed passwords)
7. **Analytics Dashboard** — Interactive dashboard with charts for posture distribution, screen time trends, burnout history, and session analytics

All metrics are logged to an SQLite database for historical analysis and dashboard visualization.

---

## ✨ Features

### User Authentication

- Secure signup and login system with PBKDF2-HMAC SHA-256 password hashing
- Multi-user support — each user has their own sessions, metrics, and history
- Clean login/signup UI with form validation and error feedback

### Real-Time Posture Detection

- Continuous webcam monitoring using MediaPipe Pose
- Classifies posture into 4 categories: **Good**, **Slightly Bad**, **Bad**, **Very Bad**
- Angle-based classification (back and neck deviation from vertical, based on ISO 11226)
- Real-time posture metrics displayed in the monitoring window

### Screen Time & Break Management

- Tracks continuous and cumulative screen time per session
- Automatically detects breaks when user is not visible for a configurable period
- Logs break duration and frequency to the database
- Configurable screen time limits

### Burnout Prediction

- Pre-trained scikit-learn classifier loaded from `data/burnout_model.pkl`
- Generates burnout probability score (0.0–1.0)
- Risk classification: Low Risk (<0.7) and High Risk (≥0.7)
- Periodic predictive evaluations at configurable intervals

### Desktop Notification Popups

- Custom PyQt5 notification popups that slide in from the bottom-right corner
- Color-coded by alert type (posture, screen time, burnout, break, user detection)
- Auto-dismiss with fade-out animation; stackable when multiple alerts arrive
- System tray icon integration for persistent background presence

### Analytics Dashboard

- Fully implemented PyQt5 dashboard accessible from the monitoring window
- Posture distribution charts, screen time trends, burnout assessment history
- Session-level analytics with aggregated metrics
- Auto-refreshing data at configurable intervals

### Comprehensive Logging

- Application-wide logging to console and file (`data/deskguardian.log`)
- All posture, break, and alert events logged to the SQLite database
- Full session history with metrics and timestamps

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DeskGuardianApp (main.py)                  │
│          Application controller: Login → Monitoring           │
└──────────────────┬──────────────────────────────┬────────────┘
                   │                              │
          ┌────────▼────────┐           ┌─────────▼──────────┐
          │  LoginSignupPage│           │ MonitoringWindow    │
          │  (modules/gui/) │           │ (modules/gui/)      │
          └────────┬────────┘           └───┬─────────┬──────┘
                   │                        │         │
          ┌────────▼────────┐               │    ┌────▼───────┐
          │  AuthService    │               │    │DashboardUI │
          │  (modules/auth/)│               │    │(modules/   │
          └─────────────────┘               │    │ dashboard/)│
                                            │    └────────────┘
           ┌────────────────────────────────┘
           │
    ┌──────▼──────────────────────────────────────────────┐
    │            Core Components (per session)              │
    ├──────────┬──────────┬───────────┬───────────────────┤
    │PoseDetect│SessionMgr│BurnoutMdl │NotificationEngine │
    │(MediaPipe│(Behavior │(ML Model) │(Popups + DB Log)  │
    │ + OpenCV)│ Tracking)│           │                   │
    └────┬─────┴────┬─────┴─────┬─────┴─────┬─────────────┘
         │          │           │           │
         └──────────┴───────────┴───────────┘
                         │
                    ┌────▼────┐
                    │DBManager│
                    │(SQLite) │
                    └┬────────┘
                     │
           ┌─────────▼──────────┐
           │    Database File   │
           │(data/deskguardian) │
           └────────────────────┘
```

---

## 🛠 Tech Stack

| Component              | Technology                                          |
| ---------------------- | --------------------------------------------------- |
| **Language**           | Python 3.10+                                        |
| **GUI Framework**      | PyQt5 (login, monitoring, dashboard, notifications) |
| **Computer Vision**    | MediaPipe Pose, OpenCV                              |
| **ML Framework**       | scikit-learn (burnout model)                         |
| **Database**           | SQLite3                                             |
| **Data Processing**    | NumPy, Pandas                                       |
| **Visualization**      | Matplotlib                                          |
| **Serialization**      | joblib (model persistence)                          |
| **Notifications**      | plyer (cross-platform desktop notifications)        |
| **Packaging**          | PyInstaller (standalone Windows executable)         |
| **Authentication**     | hashlib PBKDF2-HMAC SHA-256                         |

---

## 📁 Project Structure

```
DeskGuardian/
├── main.py                          # Application entry point (QApplication + tray icon)
├── requirements.txt                 # Python dependencies
├── DeskGuardian.spec                # PyInstaller spec for building .exe
├── README.md                        # This file
│
├── config/
│   ├── constants.py                 # Thresholds, limits, timings, alert types
│   └── settings.py                  # Feature toggles (logging, alerts)
│
├── core/
│   ├── system_controller.py         # Central orchestrator (headless/CLI mode)
│   ├── state_manager.py             # System state machine
│   └── background_timer.py          # Screen time and burnout check timers
│
├── database/
│   ├── db_manager.py                # SQLite CRUD operations
│   ├── models.py                    # Data models / schemas
│   └── schema.sql                   # Database schema definition (6 tables)
│
├── modules/
│   ├── auth/
│   │   └── auth_service.py          # User registration & login (password hashing)
│   │
│   ├── gui/
│   │   ├── login_page.py            # Login / Signup PyQt5 window
│   │   ├── monitoring_window.py     # Live camera feed + metrics + dashboard access
│   │   └── notification_popup.py    # Slide-in desktop notification popups
│   │
│   ├── behavior_tracking/
│   │   ├── session_manager.py       # Session lifecycle & integration layer
│   │   ├── screen_time_tracker.py   # Screen time metrics
│   │   └── break_detector.py        # Break event detection
│   │
│   ├── burnout_prediction/
│   │   ├── burnout_model.py         # ML model inference
│   │   └── feature_engineering.py   # Feature extraction for ML
│   │
│   ├── posture_detection/
│   │   ├── pose_detector.py         # Webcam & pose landmark extraction
│   │   ├── posture_classifier.py    # Angle-based posture classification
│   │   └── posture_metrics.py       # Angle computation (back, neck, shoulder)
│   │
│   ├── notification/
│   │   └── notification_engine.py   # Alert generation, popup dispatch, DB logging
│   │
│   └── dashboard/
│       ├── dashboard_ui.py          # PyQt5 analytics dashboard
│       └── analytics_engine.py      # Data aggregation for dashboard
│
├── tests/
│   ├── conftest.py                  # Pytest configuration
│   ├── test_analytics_engine.py     # Dashboard analytics tests
│   ├── test_auth_service.py         # Authentication tests
│   ├── test_break_detector.py       # Break detection tests
│   ├── test_helpers.py              # Utility function tests
│   ├── test_login_page_gui.py       # Login page GUI tests
│   ├── test_notification_engine.py  # Notification engine tests
│   └── test_posture_classifier.py   # Posture classification tests
│
├── utils/
│   ├── enums.py                     # PostureClass, AlertType, SystemState
│   ├── helpers.py                   # Utility functions
│   └── logger.py                    # Centralized logging
│
├── data/                            # Runtime data directory
│   ├── deskguardian.db              # SQLite database
│   ├── deskguardian.log             # Application log file
│   ├── burnout_model.pkl            # Pre-trained burnout classifier
│   └── burnout_scaler.pkl           # Feature scaler for burnout model
│
├── dist/                            # PyInstaller output (built executable)
├── build/                           # PyInstaller build artifacts
└── venv/                            # Python virtual environment
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10 or higher**
- **Webcam** (required for pose detection)
- **20MB+ disk space** (for database, logs, and ML models)
- **Windows** (primary target; macOS/Linux compatible with minor adjustments)

### Step 1: Clone Repository

```bash
git clone https://github.com/7vik2005/DeskGuardian.git
cd DeskGuardian
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python main.py
```

You should see:

1. The **Login / Signup** window appears
2. After logging in, the **Monitoring Window** opens with live camera feed
3. Real-time posture classification and metrics displayed in the bottom bar
4. Desktop notification popups appear for alerts

---

## 📦 Building a Standalone Executable

DeskGuardian can be packaged as a standalone Windows executable using PyInstaller:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build using the included spec file
pyinstaller DeskGuardian.spec
```

The built application will be available in `dist/DeskGuardian/`. Run `DeskGuardian.exe` to launch without needing a Python installation.

---

## ⚙️ Configuration

All configuration is centralized in the `config/` directory:

### config/constants.py

Contains system-wide thresholds:

```python
# Posture angle thresholds (degrees deviation from vertical, based on ISO 11226)
GOOD_POSTURE_MAX_BACK_ANGLE = 15
GOOD_POSTURE_MAX_NECK_ANGLE = 15
SLIGHT_BAD_POSTURE_MAX_BACK_ANGLE = 25
SLIGHT_BAD_POSTURE_MAX_NECK_ANGLE = 25
BAD_POSTURE_MAX_BACK_ANGLE = 40
BAD_POSTURE_MAX_NECK_ANGLE = 40

# Screen time & break thresholds
CONTINUOUS_SCREEN_TIME_LIMIT_MINUTES = 45      # Alert after 45 min continuous
BREAK_THRESHOLD_SECONDS = 120                  # 2 min absence = break
IDLE_FACE_NOT_DETECTED_SECONDS = 60            # No-user-detected timeout
POSTURE_ALERT_THRESHOLD_SECONDS = 10           # Continuous bad posture trigger

# Burnout evaluation
BURNOUT_EVALUATION_INTERVAL_MINUTES = 30       # Check burnout every 30 min
LOW_RISK_THRESHOLD = 0.4
HIGH_RISK_THRESHOLD = 0.7
```

### config/settings.py

Contains runtime defaults and feature toggles:

```python
# Logging
ENABLE_LOGGING = True
LOG_LEVEL = "INFO"                            # DEBUG, INFO, WARNING, ERROR, CRITICAL

# Alert toggles (disable to suppress specific alert categories)
ENABLE_POSTURE_ALERTS = True
ENABLE_SCREEN_TIME_ALERTS = True
ENABLE_BURNOUT_ALERTS = True
```

**To customize**: Edit these files and restart the application.

---

## 📖 Usage

### Starting the Application

```bash
python main.py
```

### Application Flow

1. **Login / Signup** — Create an account or log in with existing credentials
2. **Monitoring Window** — Live camera feed with real-time posture analysis
3. **Dashboard** — Click the "📊 Dashboard" button to view analytics
4. **Logout** — Click "Logout" to return to the login screen

### Monitoring Window Layout

```
┌────────────────────────────────────────────────────────┐
│  ● Monitoring Active   Posture: Good   📊 Dashboard  │
├────────────────────────────────────────────────────────┤
│                                                        │
│           [Live Webcam Feed with Pose Overlay]         │
│                                                        │
├────────────────────────────────────────────────────────┤
│  Back Angle   │  Neck Angle  │ Screen Time │ Session  │
│    12.3°      │    8.7°      │  23.5 min   │ 45.2 min │
└────────────────────────────────────────────────────────┘
```

**Bottom Metrics Bar:**

- **Back Angle** — Spine deviation from vertical (lower = better)
- **Neck Angle** — Head deviation from upright (lower = better)
- **Screen Time** — Cumulative active screen time this session
- **Session** — Total elapsed session time

### Notification Popups

Desktop popups appear in the bottom-right corner for:

| Alert Type              | Description                                    |
| ----------------------- | ---------------------------------------------- |
| 🔴 Posture Alert        | Sustained bad posture detected                 |
| 🟡 Screen Time Alert    | Continuous screen time limit exceeded          |
| 🔴 Burnout Alert        | High burnout risk probability (≥ 0.7)          |
| 🔵 No User Detected     | User absent from camera for extended period    |
| 🔵 User Detected        | User returned after absence                    |

### Exiting

- Click **Logout** to return to login
- Close the monitoring window to end the session

---

## 🔌 Core Modules

### DeskGuardianApp (`main.py`)

**Purpose**: Application controller and entry point

- Creates the `QApplication` and system tray icon
- Manages the Login → Monitoring → Logout lifecycle
- Handles transitions between windows

### AuthService (`modules/auth/auth_service.py`)

**Purpose**: User registration and authentication

- `signup(username, password, age, occupation)` — Register a new user with hashed password
- `login(username, password)` — Authenticate against stored credentials
- Uses PBKDF2-HMAC SHA-256 with random salt for password hashing

### MonitoringWindow (`modules/gui/monitoring_window.py`)

**Purpose**: Main monitoring interface with embedded camera feed

- Runs the pose detection loop via `QTimer` (~15 FPS)
- Displays real-time posture classification, angle metrics, screen time
- Triggers posture, screen time, burnout, and idle alerts
- Provides dashboard access and logout functionality

### PoseDetector (`modules/posture_detection/pose_detector.py`)

**Purpose**: Real-time pose detection and classification

- `process_frame()` — Captures webcam frame, detects landmarks, classifies posture
- Returns `(frame, posture_class, alert_triggered, back_angle, neck_angle)`

### SessionManager (`modules/behavior_tracking/session_manager.py`)

**Purpose**: Tracks session lifecycle and integrates behavior metrics

- `start_session()` / `end_session()` — Session lifecycle management
- `update(posture_class, alert_triggered, face_detected)` — Per-frame metrics processing
- Internally uses `ScreenTimeTracker` and `BreakDetector`

### BurnoutModel (`modules/burnout_prediction/burnout_model.py`)

**Purpose**: ML-based burnout risk assessment

- `predict_burnout(total_screen_time_min, bad_posture_count, ...)` — Returns probability (0.0–1.0)
- Pre-trained model loaded from `data/burnout_model.pkl` with scaler from `data/burnout_scaler.pkl`

### NotificationEngine (`modules/notification/notification_engine.py`)

**Purpose**: Generate alerts via desktop popups and log to database

- `send_posture_alert(session_id, duration)` — Bad posture notification
- `send_screen_time_alert(session_id, minutes)` — Screen time notification
- `send_burnout_alert(session_id, assessment_id, probability)` — Burnout risk notification
- `send_no_user_detected_alert(session_id, seconds)` — Idle detection notification
- `send_user_detected_notification(session_id)` — User return notification

### DashboardUI (`modules/dashboard/dashboard_ui.py`)

**Purpose**: Interactive analytics dashboard

- Posture distribution charts, screen time trends, burnout history
- Session-level metrics with aggregated data
- Auto-refreshing at configurable intervals

---

## 🗄 Database Schema

SQLite database with 6 core tables (defined in `database/schema.sql`):

### User

```sql
CREATE TABLE User (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    age INTEGER NOT NULL CHECK(age > 0),
    occupation TEXT,
    preferences_json TEXT
);
```

### Session

```sql
CREATE TABLE Session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    total_screen_time_minutes INTEGER DEFAULT 0,
    total_break_time_minutes INTEGER DEFAULT 0,
    bad_posture_count INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
```

### PostureEvent

```sql
CREATE TABLE PostureEvent (
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    timestamp DATETIME NOT NULL,
    posture_class TEXT NOT NULL,          -- 'Good', 'Slightly Bad', 'Bad', 'Very Bad'
    back_angle REAL,
    neck_angle REAL,
    shoulder_alignment REAL,
    is_alert_triggered BOOLEAN DEFAULT 0,
    FOREIGN KEY(session_id) REFERENCES Session(session_id) ON DELETE CASCADE
);
```

### BreakEvent

```sql
CREATE TABLE BreakEvent (
    break_id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    duration_minutes REAL NOT NULL CHECK(duration_minutes > 0),
    break_type TEXT DEFAULT 'Short Break',
    FOREIGN KEY(session_id) REFERENCES Session(session_id) ON DELETE CASCADE
);
```

### BurnoutAssessment

```sql
CREATE TABLE BurnoutAssessment (
    assessment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    interval_start DATETIME NOT NULL,
    interval_end DATETIME NOT NULL,
    burnout_probability REAL NOT NULL,     -- 0.0 to 1.0
    avg_screen_time_per_day REAL,
    avg_bad_posture_per_hour REAL,
    avg_breaks_per_hour REAL,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
```

### Alert

```sql
CREATE TABLE Alert (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_id INTEGER,
    assessment_id INTEGER,
    alert_time DATETIME NOT NULL,
    alert_type TEXT NOT NULL,              -- 'POSTURE_ALERT', 'SCREEN_TIME_ALERT', etc.
    message TEXT NOT NULL,
    resolved BOOLEAN DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
```

---

## 🧪 Testing

DeskGuardian includes a test suite located in `tests/`. Run all tests with:

```bash
pytest tests/ -v
```

### Test Coverage

| Test File                        | Covers                              |
| -------------------------------- | ----------------------------------- |
| `test_auth_service.py`           | Signup, login, password hashing     |
| `test_posture_classifier.py`     | Posture classification logic        |
| `test_break_detector.py`         | Break detection events              |
| `test_notification_engine.py`    | Alert generation and logging        |
| `test_analytics_engine.py`       | Dashboard data aggregation          |
| `test_login_page_gui.py`         | Login page GUI tests                |
| `test_helpers.py`                | Utility function tests              |

---

## 🐛 Troubleshooting

### Issue: "Webcam not available"

**Cause**: Camera not detected or already in use

**Solution:**

1. Check device manager for connected camera
2. Close other applications using the camera
3. Restart the application
4. Try USB camera if built-in doesn't work

### Issue: "Very Bad posture" constantly despite sitting straight

**Cause**: Posture angle thresholds too strict

**Solution:**

1. Open the monitoring window and check the angle values in the bottom bar
2. Adjust thresholds in `config/constants.py`:
   ```python
   GOOD_POSTURE_MAX_BACK_ANGLE = 20    # Increase from 15
   GOOD_POSTURE_MAX_NECK_ANGLE = 20
   ```
3. Restart the application

### Issue: Alerts not appearing

**Cause**: Alerts may be disabled in config

**Solution:** Check `config/settings.py`:

```python
ENABLE_POSTURE_ALERTS = True
ENABLE_SCREEN_TIME_ALERTS = True
ENABLE_BURNOUT_ALERTS = True
```

### Issue: Database locked error

**Cause**: Multiple instances running or improper shutdown

**Solution:**

1. Close all running instances
2. Delete `data/deskguardian.db` to reset
3. Restart application

### Issue: "ImportError: cannot import name..."

**Cause**: Missing dependencies or incomplete installation

**Solution:**

```bash
pip install --upgrade -r requirements.txt
```

### Issue: PyInstaller build fails

**Cause**: Missing hidden imports or data files

**Solution:**

1. Ensure all dependencies are installed in your virtual environment
2. Verify `data/burnout_model.pkl` and `data/burnout_scaler.pkl` exist
3. Run with `--debug` for more details:
   ```bash
   pyinstaller DeskGuardian.spec --debug
   ```

---

## 🤝 Contributing

### Code Style

- **PEP 8 compliance** for formatting
- **Type hints** where practical
- **Docstrings** for all classes and key methods

### Adding Features

1. **Create a branch**: `git checkout -b feature/my-feature`
2. **Implement changes** with tests
3. **Update README** if user-facing
4. **Run tests**: `pytest tests/ -v`
5. **Commit**: `git commit -m "feat: description"`
6. **Push**: `git push origin feature/my-feature`
7. **Create Pull Request**

### Reporting Bugs

Please include:

- Python version: `python --version`
- OS: Windows/macOS/Linux
- Steps to reproduce
- Error message and logs (`data/deskguardian.log`)

---

## 📝 License

This project is licensed under the MIT License. See LICENSE file for details.

---

## 👥 Team

- **Satvik** — Lead Developer

---

## 📧 Support & Questions

For questions or issues, please:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs in `data/deskguardian.log`
3. Open an issue on GitHub

---

**Last Updated**: March 31, 2026
**Version**: 2.0.0
