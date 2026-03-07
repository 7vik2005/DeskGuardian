import os
import joblib
import numpy as np
from datetime import datetime
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from modules.burnout_prediction.feature_engineering import FeatureEngineering
from config.constants import (
    BURNOUT_PROBABILITY_MIN,
    BURNOUT_PROBABILITY_MAX,
    BURNOUT_WEIGHT_SCREEN_TIME,
    BURNOUT_WEIGHT_BAD_POSTURE,
    BURNOUT_WEIGHT_LOW_BREAKS
)
from utils.logger import Logger


MODEL_PATH = "data/burnout_model.pkl"
SCALER_PATH = "data/burnout_scaler.pkl"


class BurnoutModel:
    """
    Burnout Prediction Model using Research-Based Formulas

    Research Foundation:
    - Maslach Burnout Inventory (MBI) identifies three dimensions:
      Emotional Exhaustion, Depersonalization, Reduced Personal Accomplishment
    - Screen time correlates with exhaustion (Ayyagari et al., 2011)
    - Posture quality correlates with physical fatigue (Robertson et al., 2013)
    - Break frequency inversely correlates with burnout (Trougakos & Hideg, 2009)

    Formula: burnout_probability = sigmoid(weighted_features + intercept)
    """

    def __init__(self):
        self.model = None
        self.scaler = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        """Load existing model or train a new one."""
        if os.path.exists(MODEL_PATH) and os.path.exists(SCALER_PATH):
            self.model = joblib.load(MODEL_PATH)
            self.scaler = joblib.load(SCALER_PATH)
            Logger.info("Loaded existing burnout model from disk.")
        else:
            self._train_initial_model()
            joblib.dump(self.model, MODEL_PATH)
            joblib.dump(self.scaler, SCALER_PATH)
            Logger.info("Trained and saved new burnout model.")

    def _train_initial_model(self):
        """
        Train model on synthetic academic dataset based on research findings.

        Features (normalized):
        1. avg_screen_time_per_hour: Minutes spent on screen per hour (0-60)
        2. avg_bad_posture_per_hour: Count of bad/very bad posture frames per hour
        3. avg_breaks_per_hour: Number of breaks taken per hour (0-3)

        Labels:
        0 = Low Burnout Risk (<0.7 probability)
        1 = High Burnout Risk (>=0.7 probability)
        """

        # Research-informed synthetic data: 20 samples
        X = np.array([
            # Low Risk: Good screen time management, good posture, frequent breaks
            [20, 5, 4],      # 20 min/hr screen, minimal bad posture, 4 breaks
            [25, 8, 3],      # 25 min/hr, slightly bad posture, 3 breaks
            [30, 10, 3],     # 30 min/hr, moderate bad posture, 3 breaks
            [22, 6, 4],
            [28, 9, 3],

            # Borderline: Moderate screen time, some posture issues, few breaks
            [40, 15, 2],     # 40 min/hr, bad posture, 2 breaks - borderline
            [35, 12, 2],
            [38, 14, 1],

            # High Risk: Excessive screen time, poor posture, rare breaks
            [50, 20, 1],     # 50+ min/hr, severe bad posture, 1 break - high risk
            [55, 25, 1],     # 55+ min/hr, severe bad posture, rare breaks
            [60, 30, 0],     # 60 min/hr (full screen time), very bad posture, no breaks
            [58, 28, 0],
            [52, 22, 0],
            [48, 18, 1],     # Borderline high risk

            # Additional samples for balance
            [32, 11, 2],     # Low-Mid
            [42, 16, 1],     # Mid-High
            [26, 7, 3],      # Low
            [45, 17, 1],     # High
            [30, 9, 3],      # Low
            [50, 24, 0],     # High
        ])

        # Risk labels (0 = Low Risk, 1 = High Risk)
        y = np.array([
            0, 0, 0, 0, 0,        # Low risk
            0, 0, 0,               # Borderline (still low)
            1, 1, 1, 1, 1, 1,      # High risk
            0, 1, 0, 1, 0, 1       # Mixed
        ])

        # Standardize features for better model training
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        # Train logistic regression with regularization
        self.model = LogisticRegression(
            C=1.0,
            max_iter=1000,
            random_state=42,
            solver='lbfgs'
        )
        self.model.fit(X_scaled, y)

        Logger.info(f"Trained model with coefficients: {self.model.coef_}")

    # ======================================
    # PREDICT BURNOUT PROBABILITY
    # ======================================

    def predict_burnout(
        self,
        total_screen_time_minutes,
        bad_posture_count,
        total_breaks,
        session_duration_minutes
    ):
        """
        Predict burnout probability using research-based weighting.

        Args:
            total_screen_time_minutes: Total screen time in current session
            bad_posture_count: Count of bad/very bad posture events
            total_breaks: Number of break events
            session_duration_minutes: Length of session in minutes

        Returns:
            burnout_probability: Float between 0.0 and 1.0
        """

        try:
            # Normalize features to per-hour metrics
            session_hours = max(session_duration_minutes / 60, 0.1)

            avg_screen_time_per_hour = min(total_screen_time_minutes / session_hours, 60)
            avg_bad_posture_per_hour = bad_posture_count / session_hours
            avg_breaks_per_hour = total_breaks / session_hours

            # Create feature vector
            features = np.array([
                [avg_screen_time_per_hour, avg_bad_posture_per_hour, avg_breaks_per_hour]
            ])

            # Scale features using the same scaler used for training
            if self.scaler is not None:
                features_scaled = self.scaler.transform(features)
            else:
                features_scaled = features

            # Get probability from logistic regression
            probability = self.model.predict_proba(features_scaled)[0][1]

            # Enforce domain constraints
            probability = max(BURNOUT_PROBABILITY_MIN,
                            min(probability, BURNOUT_PROBABILITY_MAX))

            Logger.debug(
                f"Burnout Prediction - Screen: {avg_screen_time_per_hour:.1f} min/hr, "
                f"Bad Posture: {avg_bad_posture_per_hour:.1f}/hr, "
                f"Breaks: {avg_breaks_per_hour:.2f}/hr, "
                f"Probability: {probability:.2%}"
            )

            return probability

        except Exception as e:
            Logger.error(f"Error in burnout prediction: {e}")
            return 0.5  # Return neutral probability on error

