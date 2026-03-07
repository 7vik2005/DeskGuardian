import sys
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem,
    QFrame, QScrollArea
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from modules.dashboard.analytics_engine import AnalyticsEngine
from utils.logger import Logger


class DashboardUI(QMainWindow):
    """
    Comprehensive DeskGuardian Dashboard

    Features:
    - Real-time session summary
    - Posture analysis with trends
    - Screen time visualization
    - Break frequency analysis
    - Burnout prediction with risk assessment
    - Alert history
    """

    def __init__(self, user_id):
        super().__init__()

        self.user_id = user_id
        self.analytics = AnalyticsEngine(user_id)

        self.setWindowTitle("DeskGuardian - Comprehensive Dashboard")
        self.setGeometry(50, 50, 1400, 900)
        self.setStyleSheet(self._get_stylesheet())

        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Create tab widget for different views
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        # Tab 1: Overview/Summary
        self.tabs.addTab(self._create_overview_tab(), "📊 Overview")

        # Tab 2: Posture Analysis
        self.tabs.addTab(self._create_posture_tab(), "🧍 Posture Analysis")

        # Tab 3: Screen Time & Breaks
        self.tabs.addTab(self._create_screen_time_tab(), "⏰ Screen Time & Breaks")

        # Tab 4: Burnout Prediction
        self.tabs.addTab(self._create_burnout_tab(), "🔥 Burnout Prediction")

        # Tab 5: Alerts History
        self.tabs.addTab(self._create_alerts_tab(), "🔔 Alert History")

        # Refresh button
        refresh_layout = QHBoxLayout()
        self.refresh_button = QPushButton("🔄 Refresh Dashboard")
        self.refresh_button.clicked.connect(self.refresh_all)
        self.refresh_button.setStyleSheet("padding: 10px; font-size: 12px; font-weight: bold;")
        refresh_layout.addStretch()
        refresh_layout.addWidget(self.refresh_button)
        self.main_layout.addLayout(refresh_layout)

        # Auto-refresh every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_all)
        self.timer.start(5000)

        # Initial refresh
        self.refresh_all()

    # ======================================
    # TAB 1: OVERVIEW
    # ======================================

    def _create_overview_tab(self):
        """Summary of current session and user stats."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Session Summary
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)

        self.summary_label = QLabel("Loading summary...")
        self.summary_label.setFont(QFont("Arial", 11))
        self.summary_label.setStyleSheet("padding: 15px; background-color: #f0f0f0; border-radius: 5px;")
        summary_layout.addWidget(self.summary_label)

        layout.addWidget(self._create_section_header("📌 Current Session Summary"))
        layout.addWidget(summary_frame)

        # Key Metrics Grid
        metrics_frame = QFrame()
        metrics_layout = QHBoxLayout(metrics_frame)

        self.metric_widgets = {}
        metrics = [
            ("Total Sessions", "total_sessions"),
            ("Total Screen Time (min)", "total_screen_time_minutes"),
            ("Total Bad Posture Count", "total_bad_posture_count"),
            ("Avg Burnout Risk", "avg_burnout_probability"),
        ]

        for metric_name, metric_key in metrics:
            metric_widget = self._create_metric_box(metric_name, "0")
            self.metric_widgets[metric_key] = metric_widget
            metrics_layout.addWidget(metric_widget)

        layout.addWidget(self._create_section_header("📈 Key Statistics"))
        layout.addWidget(metrics_frame)

        layout.addStretch()
        return widget

    # ======================================
    # TAB 2: POSTURE ANALYSIS
    # ======================================

    def _create_posture_tab(self):
        """Posture classification distribution and trends."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Posture Distribution Pie Chart
        self.posture_figure = Figure(figsize=(8, 5), dpi=100)
        self.posture_canvas = FigureCanvas(self.posture_figure)
        layout.addWidget(self._create_section_header("🧍 Posture Distribution"))
        layout.addWidget(self.posture_canvas)

        # Posture Events Table
        self.posture_table = QTableWidget()
        self.posture_table.setColumnCount(4)
        self.posture_table.setHorizontalHeaderLabels(
            ["Timestamp", "Posture Class", "Duration (sec)", "Alert Triggered"]
        )
        self.posture_table.setColumnWidth(0, 180)
        self.posture_table.setColumnWidth(1, 120)
        layout.addWidget(self._create_section_header("📝 Recent Posture Events"))
        layout.addWidget(self.posture_table)

        return widget

    # ======================================
    # TAB 3: SCREEN TIME & BREAKS
    # ======================================

    def _create_screen_time_tab(self):
        """Screen time and break analysis."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Screen Time Chart
        self.screen_time_figure = Figure(figsize=(8, 5), dpi=100)
        self.screen_time_canvas = FigureCanvas(self.screen_time_figure)
        layout.addWidget(self._create_section_header("⏰ Screen Time Timeline"))
        layout.addWidget(self.screen_time_canvas)

        # Break Events Table
        self.break_table = QTableWidget()
        self.break_table.setColumnCount(4)
        self.break_table.setHorizontalHeaderLabels(
            ["Start Time", "End Time", "Duration (min)", "Break Type"]
        )
        self.break_table.setColumnWidth(0, 150)
        self.break_table.setColumnWidth(1, 150)
        layout.addWidget(self._create_section_header("☕ Break History"))
        layout.addWidget(self.break_table)

        return widget

    # ======================================
    # TAB 4: BURNOUT PREDICTION
    # ======================================

    def _create_burnout_tab(self):
        """Burnout risk assessment and trends."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Burnout Probability Trend
        self.burnout_figure = Figure(figsize=(8, 5), dpi=100)
        self.burnout_canvas = FigureCanvas(self.burnout_figure)
        layout.addWidget(self._create_section_header("📊 Burnout Risk Trend"))
        layout.addWidget(self.burnout_canvas)

        # Current Risk Status
        risk_frame = QFrame()
        risk_layout = QHBoxLayout(risk_frame)

        self.burnout_risk_label = QLabel("Risk Status: CALCULATING...")
        self.burnout_risk_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.burnout_risk_label.setStyleSheet(
            "padding: 20px; background-color: #FFF3CD; border-radius: 5px; color: #856404;"
        )
        risk_layout.addWidget(self.burnout_risk_label)

        layout.addWidget(self._create_section_header("⚠️ Current Risk Assessment"))
        layout.addWidget(risk_frame)

        # Burnout Assessment Details Table
        self.burnout_table = QTableWidget()
        self.burnout_table.setColumnCount(5)
        self.burnout_table.setHorizontalHeaderLabels(
            ["Assessment Date", "Probability", "Risk Level", "Avg Screen Time", "Avg Bad Posture"]
        )
        layout.addWidget(self._create_section_header("📋 Burnout Assessment History"))
        layout.addWidget(self.burnout_table)

        return widget

    # ======================================
    # TAB 5: ALERTS
    # ======================================

    def _create_alerts_tab(self):
        """Alert history and notifications."""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(5)
        self.alerts_table.setHorizontalHeaderLabels(
            ["Alert Time", "Alert Type", "Message", "Status", "Resolved"]
        )
        self.alerts_table.setColumnWidth(0, 150)
        self.alerts_table.setColumnWidth(1, 140)
        self.alerts_table.setColumnWidth(2, 400)

        layout.addWidget(self.alerts_table)
        return widget

    # ======================================
    # REFRESH ALL DATA
    # ======================================

    def refresh_all(self):
        """Refresh all dashboard data."""
        try:
            Logger.debug("Refreshing dashboard...")

            # Overview
            self._update_overview()

            # Posture
            self._update_posture_analysis()

            # Screen Time
            self._update_screen_time_analysis()

            # Burnout
            self._update_burnout_analysis()

            # Alerts
            self._update_alerts_history()

        except Exception as e:
            Logger.error(f"Dashboard refresh error: {e}")

    def _update_overview(self):
        """Update overview statistics."""
        try:
            summary = self.analytics.get_session_summary()

            summary_text = (
                f"<b>Current Session Status:</b><br><br>"
                f"Session Duration: {summary.get('session_duration_minutes', 0):.1f} minutes<br>"
                f"Current Screen Time: {summary.get('current_screen_time_minutes', 0):.1f} minutes<br>"
                f"Status: {'ACTIVE' if summary.get('session_active', False) else 'INACTIVE'}"
            )

            self.summary_label.setText(summary_text)

            # Update metrics
            self.metric_widgets["total_sessions"].setText(
                str(summary.get("total_sessions", 0))
            )
            self.metric_widgets["total_screen_time_minutes"].setText(
                f"{summary.get('total_screen_time_minutes', 0):.1f}"
            )
            self.metric_widgets["total_bad_posture_count"].setText(
                str(summary.get("total_bad_posture_count", 0))
            )
            self.metric_widgets["avg_burnout_probability"].setText(
                f"{summary.get('avg_burnout_probability', 0):.1%}"
            )

        except Exception as e:
            Logger.error(f"Error updating overview: {e}")

    def _update_posture_analysis(self):
        """Update posture distribution and events."""
        try:
            posture_dist = self.analytics.get_posture_distribution()

            # Plot pie chart
            self.posture_figure.clear()
            ax = self.posture_figure.add_subplot(111)

            if posture_dist:
                labels = [item["posture_class"] for item in posture_dist]
                sizes = [item["count"] for item in posture_dist]
                colors = ["#90EE90", "#FFD700", "#ff9999", "#FF6347"]

                ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors[:len(labels)])
                ax.set_title("Posture Distribution (All Sessions)")
            else:
                ax.text(0.5, 0.5, "No posture data", ha="center", va="center")

            self.posture_canvas.draw()

            # Update posture events table
            events = self.analytics.get_recent_posture_events(limit=20)
            self.posture_table.setRowCount(len(events) if events else 0)

            if events:
                for row, event in enumerate(events):
                    self.posture_table.setItem(row, 0, QTableWidgetItem(
                        event.get("timestamp", "N/A")
                    ))
                    self.posture_table.setItem(row, 1, QTableWidgetItem(
                        event.get("posture_class", "N/A")
                    ))
                    self.posture_table.setItem(row, 2, QTableWidgetItem(
                        str(event.get("duration", 0))
                    ))
                    self.posture_table.setItem(row, 3, QTableWidgetItem(
                        "Yes" if event.get("is_alert_triggered") else "No"
                    ))

        except Exception as e:
            Logger.error(f"Error updating posture analysis: {e}")

    def _update_screen_time_analysis(self):
        """Update screen time and break analysis."""
        try:
            screen_time_data = self.analytics.get_screen_time_by_session()
            break_events = self.analytics.get_break_events(limit=20)

            # Plot screen time chart
            self.screen_time_figure.clear()
            ax = self.screen_time_figure.add_subplot(111)

            if screen_time_data:
                sessions = [item.get("session_id", i) for i, item in enumerate(screen_time_data)]
                times = [item.get("total_screen_time_minutes", 0) for item in screen_time_data]

                ax.bar(range(len(sessions)), times, color="skyblue")
                ax.set_xlabel("Session #")
                ax.set_ylabel("Screen Time (minutes)")
                ax.set_title("Screen Time Per Session")
                ax.grid(axis="y", alpha=0.3)
            else:
                ax.text(0.5, 0.5, "No screen time data", ha="center", va="center")

            self.screen_time_canvas.draw()

            # Update break events table
            self.break_table.setRowCount(len(break_events) if break_events else 0)

            if break_events:
                for row, event in enumerate(break_events):
                    self.break_table.setItem(row, 0, QTableWidgetItem(
                        event.get("start_time", "N/A")
                    ))
                    self.break_table.setItem(row, 1, QTableWidgetItem(
                        event.get("end_time", "N/A")
                    ))
                    self.break_table.setItem(row, 2, QTableWidgetItem(
                        f"{event.get('duration_minutes', 0):.1f}"
                    ))
                    self.break_table.setItem(row, 3, QTableWidgetItem(
                        event.get("break_type", "Short Break")
                    ))

        except Exception as e:
            Logger.error(f"Error updating screen time analysis: {e}")

    def _update_burnout_analysis(self):
        """Update burnout prediction and risk assessment."""
        try:
            burnout_trend = self.analytics.get_burnout_trend()
            current_risk = self.analytics.get_current_burnout_risk()

            # Plot burnout trend
            self.burnout_figure.clear()
            ax = self.burnout_figure.add_subplot(111)

            if burnout_trend:
                dates = [item.get("assessment_date", f"Assessment {i}")
                        for i, item in enumerate(burnout_trend)]
                probs = [item.get("burnout_probability", 0) for item in burnout_trend]

                ax.plot(range(len(dates)), probs, marker='o', color="red", linewidth=2)
                ax.axhline(y=0.7, color='orange', linestyle='--', label='High Risk Threshold')
                ax.axhline(y=0.4, color='green', linestyle='--', label='Low Risk Threshold')
                ax.set_xlabel("Assessment #")
                ax.set_ylabel("Burnout Probability")
                ax.set_title("Burnout Probability Trend")
                ax.set_ylim([0, 1])
                ax.legend()
                ax.grid(alpha=0.3)
            else:
                ax.text(0.5, 0.5, "No burnout data", ha="center", va="center")

            self.burnout_canvas.draw()

            # Update risk label
            if current_risk:
                prob = current_risk.get("burnout_probability", 0)
                if prob >= 0.7:
                    risk_text = f"🔴 HIGH RISK - Probability: {prob:.1%}"
                    color = "#f8d7da"
                elif prob >= 0.4:
                    risk_text = f"🟡 MODERATE RISK - Probability: {prob:.1%}"
                    color = "#fff3cd"
                else:
                    risk_text = f"🟢 LOW RISK - Probability: {prob:.1%}"
                    color = "#d4edda"

                self.burnout_risk_label.setText(risk_text)
                self.burnout_risk_label.setStyleSheet(
                    f"padding: 20px; background-color: {color}; border-radius: 5px;"
                )

            # Update burnout table
            self.burnout_table.setRowCount(len(burnout_trend) if burnout_trend else 0)

            if burnout_trend:
                for row, item in enumerate(burnout_trend):
                    self.burnout_table.setItem(row, 0, QTableWidgetItem(
                        item.get("assessment_date", "N/A")
                    ))

                    prob = item.get("burnout_probability", 0)
                    self.burnout_table.setItem(row, 1, QTableWidgetItem(
                        f"{prob:.1%}"
                    ))

                    risk_level = (
                        "HIGH" if prob >= 0.7 else "MODERATE" if prob >= 0.4 else "LOW"
                    )
                    self.burnout_table.setItem(row, 2, QTableWidgetItem(risk_level))
                    self.burnout_table.setItem(row, 3, QTableWidgetItem(
                        f"{item.get('avg_screen_time_per_day', 0):.1f}"
                    ))
                    self.burnout_table.setItem(row, 4, QTableWidgetItem(
                        f"{item.get('avg_bad_posture_per_hour', 0):.1f}"
                    ))

        except Exception as e:
            Logger.error(f"Error updating burnout analysis: {e}")

    def _update_alerts_history(self):
        """Update alert history table."""
        try:
            alerts = self.analytics.get_recent_alerts(limit=30)

            self.alerts_table.setRowCount(len(alerts) if alerts else 0)

            if alerts:
                for row, alert in enumerate(alerts):
                    self.alerts_table.setItem(row, 0, QTableWidgetItem(
                        alert.get("alert_time", "N/A")
                    ))
                    self.alerts_table.setItem(row, 1, QTableWidgetItem(
                        alert.get("alert_type", "N/A")
                    ))
                    self.alerts_table.setItem(row, 2, QTableWidgetItem(
                        alert.get("message", "N/A")
                    ))
                    self.alerts_table.setItem(row, 3, QTableWidgetItem(
                        "Resolved" if alert.get("resolved") else "Open"
                    ))
                    self.alerts_table.setItem(row, 4, QTableWidgetItem(
                        "Yes" if alert.get("resolved") else "No"
                    ))

        except Exception as e:
            Logger.error(f"Error updating alerts history: {e}")

    # ======================================
    # HELPER METHODS
    # ======================================

    def _create_section_header(self, title):
        """Create a section header label."""
        label = QLabel(title)
        label.setFont(QFont("Arial", 13, QFont.Bold))
        label.setStyleSheet("padding: 10px 0px; color: #333; border-bottom: 2px solid #007bff;")
        return label

    def _create_metric_box(self, title, value):
        """Create a metric display box."""
        widget = QLabel(value)
        widget.setFont(QFont("Arial", 16, QFont.Bold))
        widget.setAlignment(Qt.AlignCenter)
        widget.setStyleSheet(
            "padding: 20px; background-color: #e8f4f8; border-radius: 8px; "
            "border: 1px solid #007bff;"
        )

        container = QFrame()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(title_label)
        layout.addWidget(widget)

        container.data_label = widget
        container.setText = lambda v: widget.setText(str(v))

        return container

    def _get_stylesheet(self):
        """Return custom stylesheet for dashboard."""
        return """
        QMainWindow {
            background-color: #f5f5f5;
        }
        QTabWidget::pane {
            border: 1px solid #ccc;
        }
        QTabBar::tab {
            padding: 8px 20px;
            background-color: #e0e0e0;
            border: 1px solid #999;
        }
        QTabBar::tab:selected {
            background-color: #007bff;
            color: white;
        }
        QLabel {
            color: #333;
        }
        QPushButton {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #0056b3;
        }
        QTableWidget {
            background-color: white;
            alternate-background-color: #f9f9f9;
            border: 1px solid #ddd;
        }
        QHeaderView::section {
            background-color: #007bff;
            color: white;
            padding: 5px;
            border: none;
        }
        QFrame {
            background-color: white;
            border-radius: 5px;
        }
        """


# ======================================
# STANDALONE RUN
# ======================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DashboardUI(user_id=1)
    window.show()
    sys.exit(app.exec_())

