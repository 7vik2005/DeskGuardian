from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QColor

from modules.auth.auth_service import AuthService


class LoginSignupPage(QWidget):

    login_success = pyqtSignal(int, str)

    def __init__(self):
        super().__init__()

        self.auth = AuthService()

        self.setWindowTitle("DeskGuardian - Welcome")
        self.setFixedSize(500, 680)
        self.setStyleSheet(self._stylesheet())

        self.stack = QStackedWidget()

        root = QVBoxLayout(self)
        root.setAlignment(Qt.AlignCenter)
        root.setContentsMargins(40, 24, 40, 24)

        header = QLabel("DeskGuardian")
        header.setAlignment(Qt.AlignCenter)
        header.setFont(QFont("Segoe UI", 26, QFont.Bold))
        header.setObjectName("mainHeader")

        subtitle = QLabel("Your personal posture guardian")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setObjectName("subtitle")

        root.addWidget(header)
        root.addWidget(subtitle)

        root.addSpacing(14)

        self.card = QFrame()
        self.card.setObjectName("card")
        self.card.setFixedWidth(410)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 80))
        self.card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 24, 32, 24)

        self.stack.addWidget(self._build_login_page())
        self.stack.addWidget(self._build_signup_page())

        card_layout.addWidget(self.stack)

        root.addWidget(self.card)

    # LOGIN PAGE

    def _build_login_page(self):
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setSpacing(4)

        title = QLabel("Login")
        title.setObjectName("title")
        layout.addWidget(title)

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        layout.addWidget(self._field_label("Username"))
        layout.addWidget(self.login_username)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self._field_label("Password"))
        layout.addWidget(self.login_password)

        self.login_error = QLabel("")
        self.login_error.setObjectName("error")
        layout.addWidget(self.login_error)

        login_btn = QPushButton("Login")
        login_btn.clicked.connect(self._on_login)
        layout.addWidget(login_btn)

        layout.addSpacing(8)

        switch_label = QLabel("Don't have an account?")
        switch_label.setAlignment(Qt.AlignCenter)

        signup_link = QPushButton("Create Account")
        signup_link.setObjectName("linkBtn")
        signup_link.clicked.connect(lambda: self.stack.setCurrentIndex(1))

        layout.addWidget(switch_label)
        layout.addWidget(signup_link)

        return page

    # SIGNUP PAGE

    def _build_signup_page(self):
        page = QFrame()
        layout = QVBoxLayout(page)
        layout.setSpacing(10)

        title = QLabel("Create Account")
        title.setObjectName("title")
        layout.addWidget(title)

        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Username")
        layout.addWidget(self._field_label("Username"))
        layout.addWidget(self.signup_username)

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self._field_label("Password"))
        layout.addWidget(self.signup_password)

        self.signup_age = QLineEdit()
        self.signup_age.setPlaceholderText("Age")
        self.signup_age.setValidator(QIntValidator(1, 150))
        layout.addWidget(self._field_label("Age"))
        layout.addWidget(self.signup_age)

        self.signup_error = QLabel("")
        self.signup_error.setObjectName("error")
        layout.addWidget(self.signup_error)

        signup_btn = QPushButton("Sign Up")
        signup_btn.clicked.connect(self._on_signup)
        layout.addWidget(signup_btn)

        layout.addSpacing(6)

        switch_label = QLabel("Already have an account?")
        switch_label.setAlignment(Qt.AlignCenter)

        login_link = QPushButton("Back to Login")
        login_link.setObjectName("linkBtn")
        login_link.clicked.connect(lambda: self.stack.setCurrentIndex(0))

        layout.addWidget(switch_label)
        layout.addWidget(login_link)

        return page

    # HANDLERS

    def _on_login(self):
        username = self.login_username.text().strip()
        password = self.login_password.text()

        self.login_error.setText("")

        user_id, err = self.auth.login(username, password)

        if err:
            self.login_error.setText(err)
        else:
            self.login_success.emit(user_id, username)

    def _on_signup(self):

        username = self.signup_username.text().strip()
        password = self.signup_password.text()
        age_text = self.signup_age.text().strip()

        self.signup_error.setText("")

        if not age_text or not age_text.isdigit() or int(age_text) < 1:
            self.signup_error.setText("Please enter a valid age.")
            return

        age = int(age_text)

        user_id, err = self.auth.signup(username, password, age)

        if err:
            self.signup_error.setText(err)
        else:

            QMessageBox.information(
                self,
                "Success",
                "Account created! You can now log in."
            )

            self.stack.setCurrentIndex(0)
            self.login_username.setText(username)

    # HELPERS

    @staticmethod
    def _field_label(text):
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    @staticmethod
    def _stylesheet():
        return """

        QWidget {
            background: #f4f6f9;
            font-family: "Segoe UI";
        }

        QFrame {
            background: transparent;
        }

        #card {
            background: white;
            border-radius: 12px;
        }

        #mainHeader {
            color: #1f2937;
        }

        #subtitle {
            color: #6b7280;
            font-size: 14px;
        }

        #title {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 6px;
        }

        #fieldLabel {
            color: #555;
            font-size: 11px;
            margin-top: 8px;
            margin-bottom: 0px;
        }

        QLineEdit {
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #d1d5db;
            font-size: 13px;
            background: white;
        }

        QLineEdit:focus {
            border: 2px solid #3b82f6;
        }

        QPushButton {
            padding: 10px;
            background: #3b82f6;
            color: white;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
        }

        QPushButton:hover {
            background: #2563eb;
        }

        QPushButton#linkBtn {
            background: none;
            color: #3b82f6;
            font-weight: normal;
        }

        QPushButton#linkBtn:hover {
            text-decoration: underline;
            background: none;
        }

        #error {
            color: #ef4444;
        }

        """
