import logging

from utils.helpers import classify_burnout_risk


logger = logging.getLogger(__name__)


def test_classify_burnout_risk_boundaries():
    logger.info("TC01 Step 1: Prepare burnout probability boundary inputs")
    inputs = [0.39, 0.4, 0.69, 0.7]
    logger.info("TC01 Inputs: %s", inputs)

    logger.info("TC01 Step 2: Execute classify_burnout_risk for each input")
    outputs = [classify_burnout_risk(v) for v in inputs]
    logger.info("TC01 Actual Outputs: %s", outputs)

    logger.info("TC01 Step 3: Validate expected risk levels")
    assert outputs[0] == "Low Risk"
    assert outputs[1] == "Moderate Risk"
    assert outputs[2] == "Moderate Risk"
    assert outputs[3] == "High Risk"

    logger.info("TC01 Result: PASS")
