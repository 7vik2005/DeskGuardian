import logging

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QSignalSpy

from modules.gui.login_page import LoginSignupPage


logger = logging.getLogger(__name__)


def test_login_page_emits_success_signal(monkeypatch):
    logger.info("TC08 Step 1: Create LoginSignupPage widget")
    app = QApplication.instance() or QApplication([])
    widget = LoginSignupPage()

    logger.info("TC08 Step 2: Mock auth.login to return successful credentials")
    monkeypatch.setattr(widget.auth, "login", lambda username, password: (123, None))

    logger.info("TC08 Step 3: Enter input values username=charlie, password=secret")
    widget.login_username.setText("charlie")
    widget.login_password.setText("secret")

    logger.info("TC08 Step 4: Trigger login handler and wait for login_success signal")
    spy = QSignalSpy(widget.login_success)
    widget._on_login()
    app.processEvents()

    assert len(spy) == 1
    args = list(spy[0])
    logger.info("TC08 Signal Output: args=%s", args)
    assert args == [123, "charlie"]
    logger.info("TC08 Result: PASS")
