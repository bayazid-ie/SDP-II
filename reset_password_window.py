from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class ResetPasswordWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reset Password")
        self.resize(400, 200)
        self.setStyleSheet("background-color:#f3f1fe;")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Reset Your Password")
        title.setStyleSheet("font-size: 16px;")
        title.setAlignment(Qt.AlignCenter)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        self.email_input.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid black;
                font-size: 14px;
                padding: 5px;
                background: transparent;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2196F3;
            }
        """)

        submit_button = QPushButton("Send Reset Link")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        submit_button.clicked.connect(self.send_reset_email)

        layout.addWidget(title)
        layout.addSpacing(15)
        layout.addWidget(self.email_input)
        layout.addSpacing(10)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def send_reset_email(self):
        email = self.email_input.text().strip()
        if email:
            QMessageBox.information(self, "Success", f"Password reset link sent to {email}.")
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Please enter a valid email.")
