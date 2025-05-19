import sqlite3
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
    QDateEdit, QTimeEdit, QListWidget, QListWidgetItem, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtGui import QColor
from database import create_task_table, insert_task, get_all_tasks, delete_task

class TaskSchedulerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Scheduler")
        self.setMinimumSize(600, 500)

        self.tasks = []  # Store tasks in memory
        self.init_ui()
        self.setStyle()

        # Initialize database table
        create_task_table()
        # Load existing tasks from the database
        self.load_existing_tasks()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Enter Task Title")
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(self.title_input)

        # Category
        self.category_input = QComboBox()
        self.category_input.addItems(["Assignment", "Exam", "Study", "Meeting", "Other"])
        layout.addWidget(QLabel("Category:"))
        layout.addWidget(self.category_input)

        # Date & Time
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)

        self.time_input = QTimeEdit()
        self.time_input.setTime(QTime.currentTime())

        datetime_layout = QHBoxLayout()
        datetime_layout.addWidget(QLabel("Date:"))
        datetime_layout.addWidget(self.date_input)
        datetime_layout.addWidget(QLabel("Time:"))
        datetime_layout.addWidget(self.time_input)
        layout.addLayout(datetime_layout)

        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter Task Description")
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.description_input)

        # Add Task Button
        self.add_button = QPushButton("Add Task")
        self.add_button.setStyleSheet(""" 
            QPushButton {
                background-color: #5A9EFF;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4C8BFF;
            }
        """)
        self.add_button.clicked.connect(self.add_task)
        layout.addWidget(self.add_button)

        # Delete Task Button
        self.delete_button = QPushButton("Delete Task")
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #FF4D4D;
            }
        """)
        self.delete_button.clicked.connect(self.delete_task)
        layout.addWidget(self.delete_button)

        # Task list
        self.task_list = QListWidget()
        layout.addWidget(QLabel("Scheduled Tasks:"))
        layout.addWidget(self.task_list)

        self.setLayout(layout)

    def setStyle(self):
        # General Styling
        self.setStyleSheet(""" 
            QDialog {
                background-color: #2E2E2E;
                color: white;
                font-family: 'Arial', sans-serif;
            }
            QLabel {
                font-size: 14px;
                color: #B0B0B0;
            }
            QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {
                background-color: #444444;
                color: white;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {
                border: 2px solid #5A9EFF;
            }
            QListWidget {
                background-color: #333333;
                border-radius: 5px;
                padding: 10px;
                margin-top: 20px;
            }
            QListWidgetItem {
                padding: 10px;
                background-color: #444444;
                border-radius: 5px;
                margin-bottom: 10px;
            }
            QListWidgetItem:hover {
                background-color: #5A9EFF;
            }
        """)

    def add_task(self):
        title = self.title_input.text()
        category = self.category_input.currentText()
        date = self.date_input.date().toString("yyyy-MM-dd")
        time = self.time_input.time().toString("HH:mm")
        description = self.description_input.toPlainText()

        if not title.strip():
            QMessageBox.warning(self, "Input Error", "Task title cannot be empty.")
            return

        task_id = insert_task(title, category, date, time, description)

        task_info = f"{date} {time} | {category} | {title} - {description}"

        task_item = QListWidgetItem(task_info)
        task_item.setForeground(QColor("white"))
        task_item.setData(1, task_id)
        self.task_list.addItem(task_item)

        self.title_input.clear()
        self.description_input.clear()
        self.category_input.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.time_input.setTime(QTime.currentTime())

    def load_existing_tasks(self):
        tasks = get_all_tasks()
        for task in tasks:
            task_info = f"{task[3]} {task[4]} | {task[2]} | {task[1]} - {task[5]}"
            item = QListWidgetItem(task_info)
            item.setForeground(QColor("white"))
            item.setData(1, task[0])
            self.task_list.addItem(item)

    def delete_task(self):
        selected_item = self.task_list.currentItem()
        if selected_item:
            task_id = selected_item.data(1)
            delete_task(task_id)
            self.task_list.takeItem(self.task_list.row(selected_item))