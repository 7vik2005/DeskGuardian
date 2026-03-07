# Quick Start Guide - DeskGuardian with All Updates

## Installation (5 minutes)

```bash
# 1. Navigate to project directory
cd "path/to/DeskGuardian"

# 2. Create virtual environment (if not already done)
python -m venv venv

# 3. Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# 4. Install/Update dependencies
pip install -r requirements.txt

# 5. Verify setup
python -m py_compile config/*.py core/*.py modules/**/*.py utils/*.py
```

---

## Quick Start (2 commands)

### Command 1: Run Main Application

```bash
python main.py
```

Expected output:

```
[INFO] Starting DeskGuardian Application...
[INFO] Using existing user: DefaultUser (ID: 1)
[INFO] System Initializing...
[INFO] Monitoring Started.
```

A webcam window titled "DeskGuardian - Monitoring" will open with real-time posture detection.

### Command 2: Open Dashboard (in separate terminal)

```bash
# Keep the main application running, open another terminal window
python -m modules.dashboard.dashboard_ui
```

A dashboard window will open with 5 tabs showing all analytics.

---

## What to Expect

### During Monitoring (Main Application)

1. **Webcam Feed**: Shows your posture with landmarks overlay
2. **Console Output**: Real-time logs like:

   ```
   [INFO] Good posture detected
   [WARNING] Bad posture detected!
   [ALERT] Bad posture detected for 35 seconds. Please sit upright.
   ```

3. **Desktop Notifications** (will appear in system tray):

   ```
   DeskGuardian - Bad Posture Alert
   ⚠️ Bad posture detected for 35 seconds. Please sit upright.
   ```

4. **No-User-Detected Alert** (after 60 seconds of no face):

   ```
   DeskGuardian - No User Detected
   👤 No user detected for 60 seconds. Closing camera to save resources.
   ```

   Then camera closes automatically.

5. **Burnout Alert** (during burnout checks):
   ```
   DeskGuardian - Burnout Risk Alert
   🔥 High burnout risk detected (Probability: 85%). Please take immediate rest.
   ```

### Dashboard Tabs

**Tab 1: Overview 📊**

- Current session duration
- Total screen time
- Bad posture count
- Average burnout probability

**Tab 2: Posture Analysis 🧍**

- Pie chart: Distribution of posture classes
- Table: Recent posture events (last 20)

**Tab 3: Screen Time & Breaks ⏰**

- Bar chart: Screen time per session
- Table: Break events with durations

**Tab 4: Burnout Prediction 🔥**

- Line chart: Burnout probability trend
- Status indicator: 🟢 Low / 🟡 Moderate / 🔴 High Risk
- Table: Assessment history

**Tab 5: Alert History 🔔**

- Table: All recent alerts (last 30)
- Alert type, message, timestamp, resolution status

---

## Testing the Features

### Test 1: Posture Detection ✅

```
Action: Sit upright with good posture
Expected: "Good" classification on screen
Timeline: 2 seconds

Action: Lean forward significantly
Expected: Screen shows "Bad" or "Very Bad"
Timeline: 2 seconds
```

### Test 2: Posture Alert 🔔

```
Action: Maintain bad posture for 30+ seconds
Expected: Desktop alert appears: "⚠️ Bad posture detected for 30 seconds..."
Timeline: 30-35 seconds

Check: Console shows "[WARNING] Bad posture alert triggered! Duration: 30s"
```

### Test 3: No-User-Detected Alert 👤

```
Action: Look away from camera for 60+ seconds
Expected: Desktop alert: "👤 No user detected for 60 seconds. Closing camera..."
Timeline: 60-65 seconds

Check: Camera window closes automatically
Action: Look at camera again
Expected: Alert: "✅ User detected. Resuming monitoring..."
```

### Test 4: Burnout Calculation 🔥

```
Action: Let application run for 30+ minutes with various activities
Expected: Burnout assessment runs (check console for "Running burnout evaluation...")
Timeline: Every 30 minutes automatically

Check: Dashboard Tab 4 shows new assessment
Check: If probability >= 0.7, desktop alert appears
```

### Test 5: Dashboard Updates 📊

```
Action: Open dashboard while monitoring
Expected: All 5 tabs load with data (if session has been running)
Check: Dashboard auto-refreshes every 5 seconds (watch values update)

Test Break Detection:
Action: Leave desk for 2+ minutes
Expected: BreakEvent table shows break start/end times
```

---

## Configuration & Customization

### Adjust Posture Thresholds (in `config/constants.py`)

```python
# Make stricter
GOOD_POSTURE_MAX_BACK_ANGLE = 10  # Shorter tolerance

# Make more lenient
GOOD_POSTURE_MAX_BACK_ANGLE = 20  # More tolerance
```

### Adjust No-User-Detected Timeout (in `config/constants.py`)

```python
# Close camera faster
IDLE_FACE_NOT_DETECTED_SECONDS = 30  # 30 seconds

# Close camera slower
IDLE_FACE_NOT_DETECTED_SECONDS = 120  # 2 minutes
```

### Adjust Burnout Check Frequency (in `config/constants.py`)

```python
# Check more frequently
BURNOUT_EVALUATION_INTERVAL_MINUTES = 15  # Every 15 minutes

# Check less frequently
BURNOUT_EVALUATION_INTERVAL_MINUTES = 60  # Every hour
```

### Enable/Disable Specific Alerts (in `config/settings.py`)

```python
ENABLE_POSTURE_ALERTS = True      # False to disable
ENABLE_SCREEN_TIME_ALERTS = True  # False to disable
ENABLE_BURNOUT_ALERTS = True      # False to disable
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'win10toast'"

```bash
Solution: pip install win10toast
```

### Issue: "Cannot open camera"

```bash
Solution:
- Check camera is connected
- Close other apps using camera (Teams, Zoom, etc.)
- Try unplugging and replugging USB camera
- On Linux: pip install opencv-python headless may be needed
```

### Issue: "Dashboard doesn't show data"

```bash
Solution:
- Ensure main app has been running for at least 1 session
- Check database exists: data/deskguardian.db
- Run: python -c "from database.db_manager import DBManager; print('DB OK')"
```

### Issue: "Posture still shows as 'Very Bad' when upright"

```bash
Solution:
- Check GOOD_POSTURE_MAX_BACK_ANGLE is 15 (not 10)
- Check GOOD_POSTURE_MAX_NECK_ANGLE is 15 (not 10)
- Verify constants.py was updated correctly
```

### Issue: "No desktop notifications appearing"

```bash
Solution on Windows:
- Check if win10toast is installed: pip list | grep win10toast
- Check Windows Notification Settings are enabled
- Notifications may appear in system tray

Solution on Linux:
- Install: pip install pynotify
- Check notification daemon is running
```

### Issue: "Camera doesn't close after no-user alert"

```bash
Solution:
- Check IDLE_FACE_NOT_DETECTED_SECONDS is 60 (not too high)
- Check console for any errors
- Try closing and reopening the application
```

---

## File Locations & Database

### Key Directories

```
DeskGuardian/
├── data/                          # Runtime data
│   ├── deskguardian.db           # SQLite database (auto-created)
│   ├── deskguardian.log          # Application log file
│   ├── burnout_model.pkl         # Trained ML model (auto-created)
│   └── burnout_scaler.pkl        # Feature scaler (auto-created)
├── config/
│   ├── constants.py              # All tunable constants
│   └── settings.py               # Feature toggles
└── ...
```

### Important Files to Know

```
main.py                 # Application entry point
config/constants.py     # Edit thresholds here
config/settings.py      # Edit alert toggles here
data/deskguardian.log  # Check logs for debugging
```

---

## Data Logging

All data is automatically logged to SQLite database (`data/deskguardian.db`):

### Tables

- **Session**: User sessions with screen time and posture counts
- **PostureEvent**: Individual posture classifications
- **BreakEvent**: Break periods with duration
- **BurnoutAssessment**: Periodic burnout probability assessments
- **Alert**: All system alerts with timestamps

### View Logs

```bash
# Check application logs
tail -f data/deskguardian.log

# Or open logs in editor
cat data/deskguardian.log
```

---

## Performance Tips

1. **Use lower FPS**: Set `FPS = 10` in constants.py if CPU usage is high
2. **Reduce dashboard refresh**: Set `DASHBOARD_REFRESH_INTERVAL_MS = 5000` in constants.py
3. **Close unnecessary apps**: Free up system resources
4. **Better lighting**: Improves pose detection accuracy

---

## Session Summary

After closing the application normally (press 'q' in the window), check:

```
[INFO] System Shutdown Complete.
```

Then open the dashboard to see session summary:

- Total sessions
- Total screen time
- Bad posture events
- Average burnout risk

---

## Integration Examples

### Run Monitoring in Background

```bash
# On Windows
start python main.py

# On Mac/Linux
python main.py &
```

### Scheduled Daily Checks

```bash
# Create a cron job (Mac/Linux) to run at 9 AM daily
0 9 * * * /path/to/venv/bin/python /path/to/DeskGuardian/main.py
```

---

## Next Steps

1. ✅ Install dependencies
2. ✅ Run main application
3. ✅ Open dashboard in separate terminal
4. ✅ Test features (posture, breaks, alerts)
5. ✅ Customize thresholds if needed
6. ✅ Review logs for insights

---

## Support

For issues or questions:

1. Check `data/deskguardian.log` for error messages
2. Review thresholds in `config/constants.py`
3. Verify all dependencies: `pip list`
4. Test individual components in isolation

---

**Happy monitoring! Stay healthy and maintain good posture!** 🧍‍♂️✨
