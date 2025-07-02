import sqlite3
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton,
                             QVBoxLayout, QMessageBox)

DB_FILE = "user.db"

class ProfileManager(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id  # ID of the logged-in user
        self.setWindowTitle("Profile Manager")

        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        self.name_label = QLabel("Name:")
        self.name_edit = QLineEdit()

        self.username_label = QLabel("Username:")
        self.username_edit = QLineEdit()
        self.username_edit.setReadOnly(True)  # username usually stays unique

        self.email_label = QLabel("Email:")
        self.email_edit = QLineEdit()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.update_profile)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_edit)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_edit)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_user_data(self):
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, username, email FROM users WHERE id=?", (self.user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            self.name_edit.setText(user[0])
            self.username_edit.setText(user[1])
            self.email_edit.setText(user[2])

    def update_profile(self):
        name = self.name_edit.text()
        email = self.email_edit.text()

        if not name or not email:
            QMessageBox.warning(self, "Error", "Name and email cannot be empty.")
            return

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users SET name=?, email=? WHERE id=?
            """, (name, email, self.user_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Profile updated successfully!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Email already in use.")
        finally:
            conn.close()
