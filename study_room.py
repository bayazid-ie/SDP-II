from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QListWidget,
    QPushButton, QLineEdit, QMessageBox, QFileDialog, QTabWidget, QWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import os
import shutil
from datetime import datetime

from database import (
    create_study_room_tables,
    insert_message,
    get_all_messages,
    insert_shared_file,
    get_all_shared_files,
)

class StudyRoomWindow(QDialog):
    def __init__(self, username=None):
        super().__init__()
        self.username = username or "Guest"
        self.setWindowTitle(f"Study Room - {self.username}")
        self.setMinimumSize(800, 600)

        # Initialize DB tables
        create_study_room_tables()

        # Load persistent data
        self.chat_history = get_all_messages()
        self.shared_files = get_all_shared_files()

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout()

        self.status_label = QLabel("Persistent Study Room - Data saved between sessions")
        self.status_label.setAlignment(Qt.AlignRight)
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        self.main_layout.addWidget(self.status_label)

        self.tabs = QTabWidget()

        self.chat_tab = QWidget()
        self.init_chat_tab()
        self.tabs.addTab(self.chat_tab, "Chat")

        self.files_tab = QWidget()
        self.init_files_tab()
        self.tabs.addTab(self.files_tab, "Shared Files")

        self.main_layout.addWidget(self.tabs)
        self.setLayout(self.main_layout)

    def init_chat_tab(self):
        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)

        for sender, message, timestamp in self.chat_history:
            self.append_chat_message(sender, message, timestamp)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)

        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)
        self.chat_tab.setLayout(layout)

    def init_files_tab(self):
        layout = QVBoxLayout()

        self.shared_files_list = QListWidget()
        for file in self.shared_files:
            item_text = f"{file['name']} ({file['size']} KB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, file["path"])
            self.shared_files_list.addItem(item)

        self.shared_files_list.itemDoubleClicked.connect(self.view_file)

        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.upload_file)

        self.download_button = QPushButton("Download Selected File")
        self.download_button.clicked.connect(self.download_file)

        layout.addWidget(self.shared_files_list)
        layout.addWidget(self.upload_button)
        layout.addWidget(self.download_button)
        self.files_tab.setLayout(layout)

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            insert_message(self.username, message)
            self.append_chat_message(self.username, message)
            self.message_input.clear()

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File to Share")
        if file_path:
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / 1024  # Size in KB

            insert_shared_file(file_name, f"{file_size:.1f}", file_path, self.username)

            item_text = f"{file_name} ({file_size:.1f} KB)"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, file_path)
            self.shared_files_list.addItem(item)

            self.append_chat_message("System", f"{self.username} shared {file_name}")

    def view_file(self, item):
        path = item.data(Qt.UserRole)
        if os.path.exists(path):
            try:
                os.startfile(path)  # Windows
            except AttributeError:
                import subprocess
                try:
                    subprocess.call(["open", path])  # macOS
                except:
                    subprocess.call(["xdg-open", path])  # Linux
        else:
            QMessageBox.warning(self, "File Not Found", "The selected file is missing.")

    def download_file(self):
        selected_item = self.shared_files_list.currentItem()
        if not selected_item:
            QMessageBox.warning(self, "No File Selected", "Please select a file to download.")
            return

        original_path = selected_item.data(Qt.UserRole)
        if not os.path.exists(original_path):
            QMessageBox.warning(self, "File Not Found", "The original file is missing.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save File As", selected_item.text().split(" (")[0])
        if save_path:
            try:
                shutil.copyfile(original_path, save_path)
                QMessageBox.information(self, "Download Successful", f"File saved to:\n{save_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")

    def append_chat_message(self, sender, message, timestamp=None):
        ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        display_time = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%H:%M")
        formatted_message = f"[{display_time}] <b>{sender}:</b> {message}"
        self.chat_display.append(formatted_message)
