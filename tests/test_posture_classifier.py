import logging

from modules.posture_detection.posture_classifier import PostureClassifier
from utils.enums import PostureClass


logger = logging.getLogger(__name__)


def test_posture_classifier_good_posture():
    logger.info("TC02 Step 1: Initialize PostureClassifier")
    classifier = PostureClassifier()

    logger.info("TC02 Step 2: Classify good posture input back=5, neck=7")
    posture, alert = classifier.classify(5, 7)
    logger.info("TC02 Actual Output: posture=%s, alert=%s", posture, alert)

    logger.info("TC02 Step 3: Validate posture and alert state")
    assert posture == PostureClass.GOOD
    assert alert is False
    logger.info("TC02 Result: PASS")


def test_posture_classifier_alert_after_duration(monkeypatch):
    logger.info("TC03 Step 1: Initialize classifier and mocked time sequence")
    classifier = PostureClassifier()

    # First classify starts timer at 1000; second classify occurs at 1015.
    # This exceeds POSTURE_ALERT_THRESHOLD_SECONDS in config/constants.py.
    fake_times = iter([1000.0, 1000.0, 1015.0, 1015.0])

    class FakeTimeModule:
        @staticmethod
        def time():
            return next(fake_times)

    # Replace module-level `time` reference used by PostureClassifier only,
    # avoiding side effects on Python logging internals.
    monkeypatch.setattr(
        "modules.posture_detection.posture_classifier.time",
        FakeTimeModule,
    )

    logger.info("TC03 Step 2: Classify bad posture twice to simulate sustained bad posture")
    _, first_alert = classifier.classify(35, 35)
    posture, second_alert = classifier.classify(35, 35)
    logger.info(
        "TC03 Actual Output: posture=%s, first_alert=%s, second_alert=%s",
        posture,
        first_alert,
        second_alert,
    )

    logger.info("TC03 Step 3: Validate alert becomes true after threshold duration")
    assert posture in (PostureClass.BAD, PostureClass.VERY_BAD)
    assert first_alert is False
    assert second_alert is True
    logger.info("TC03 Result: PASS")
