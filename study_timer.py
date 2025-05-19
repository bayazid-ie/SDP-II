from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QLineEdit,
    QHBoxLayout, QTimeEdit, QSpinBox, QListWidgetItem, QProgressBar, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, QTime
import sqlite3

class StudyTimerDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Study Timer & Routine Planner")
        self.setMinimumSize(500, 500)

        self.tasks = []
        self.current_task_index = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

        self.is_paused = False
        self.total_seconds = 0
        self.remaining_seconds = 0

        # Initialize database
        self.db = sqlite3.connect('study_tasks.db')
        self.cursor = self.db.cursor()
        self.create_table()

        self.init_ui()

    def create_table(self):
        # Create a table to store tasks if it doesn't exist
        self.cursor.execute(""" 
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                subject TEXT,
                start_time TEXT,
                duration INTEGER
            )
        """)
        self.db.commit()

    def load_tasks(self):
        # Load tasks from the database and display them
        self.cursor.execute("SELECT id, subject, start_time, duration FROM tasks")
        rows = self.cursor.fetchall()
        for row in rows:
            task_id, subject, start_time, duration = row
            task_text = f"{subject} | Start: {start_time} | {duration} min"
            self.tasks.append((task_id, subject, start_time, duration))
            self.task_list.addItem(task_text)

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.routine_label = QLabel("📘 Today's Study Routine")
        self.routine_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #37474F;")
        layout.addWidget(self.routine_label)

        self.task_list = QListWidget()
        self.task_list.itemSelectionChanged.connect(self.task_selection_changed)  # Add this line
        layout.addWidget(self.task_list)

        # Input fields
        input_layout = QHBoxLayout()
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")
        self.start_time_input = QTimeEdit()
        self.start_time_input.setDisplayFormat("hh:mm AP")
        self.duration_input = QSpinBox()
        self.duration_input.setSuffix(" min")
        self.duration_input.setRange(1, 300)

        input_layout.addWidget(self.subject_input)
        input_layout.addWidget(self.start_time_input)
        input_layout.addWidget(self.duration_input)

        layout.addLayout(input_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Add Task")
        self.add_btn.clicked.connect(self.add_task)
        self.start_btn = QPushButton("▶️ Start Timer")
        self.start_btn.clicked.connect(self.start_task_timer)
        self.start_btn.setEnabled(False)

        self.pause_btn = QPushButton("⏸️ Pause")
        self.pause_btn.clicked.connect(self.pause_timer)
        self.pause_btn.setEnabled(False)

        self.reset_btn = QPushButton("🔁 Reset")
        self.reset_btn.clicked.connect(self.reset_timer)
        self.reset_btn.setEnabled(False)

        self.delete_btn = QPushButton("🗑️ Delete Task")
        self.delete_btn.clicked.connect(self.delete_task)
        self.delete_btn.setEnabled(False)

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.pause_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        # Timer Display
        self.timer_label = QLabel("⏳ 00:00")
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #00796B;")
        layout.addWidget(self.timer_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.setStyleSheet("""
            QDialog {
                background-color: #F0F4C3;
            }
            QLineEdit, QTimeEdit, QSpinBox, QListWidget {
                padding: 5px;
                font-size: 14px;
                border: 1px solid #BDBDBD;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #81C784;
                font-weight: bold;
                border-radius: 5px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)

        # Load tasks from the database when the app starts
        self.load_tasks()

    def task_selection_changed(self):
        """Enable/disable buttons based on task selection"""
        selected = self.task_list.currentRow() != -1
        self.start_btn.setEnabled(selected)
        self.delete_btn.setEnabled(selected)

    def add_task(self):
        subject = self.subject_input.text().strip()
        start_time = self.start_time_input.time().toString("hh:mm AP")
        duration = self.duration_input.value()

        if subject:
            task_text = f"{subject} | Start: {start_time} | {duration} min"
            self.tasks.append((None, subject, start_time, duration))  # No task_id yet
            self.task_list.addItem(task_text)

            # Save task to the database
            self.cursor.execute("INSERT INTO tasks (subject, start_time, duration) VALUES (?, ?, ?)", 
                                (subject, start_time, duration))
            self.db.commit()

            # Get the task_id of the newly inserted task
            task_id = self.cursor.lastrowid
            self.tasks[-1] = (task_id, subject, start_time, duration)  # Update with task_id

            self.subject_input.clear()
            self.duration_input.setValue(1)
        else:
            QMessageBox.warning(self, "Missing Info", "Please enter a subject.")

    def delete_task(self):
        selected_task = self.task_list.currentRow()
        if selected_task != -1:
            task_id = self.tasks[selected_task][0]

            # Remove from the database
            self.cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            self.db.commit()

            # Remove from the QListWidget
            self.task_list.takeItem(selected_task)
            self.tasks.pop(selected_task)

            # Reset buttons
            self.delete_btn.setEnabled(False)
            self.start_btn.setEnabled(False)

        else:
            QMessageBox.warning(self, "No Task Selected", "Select a task from the list to delete.")

    def start_task_timer(self):
        if self.timer.isActive():
            QMessageBox.warning(self, "Timer Running", "A task is already running.")
            return

        self.current_task_index = self.task_list.currentRow()
        if self.current_task_index == -1:
            QMessageBox.warning(self, "No Task Selected", "Select a task from the list.")
            return

        _, _, _, duration = self.tasks[self.current_task_index]
        self.total_seconds = duration * 60
        self.remaining_seconds = self.total_seconds
        self.timer.start(1000)
        self.update_timer_display()

        # Highlight current task
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setBackground(Qt.white)
        self.task_list.item(self.current_task_index).setBackground(Qt.lightGray)

        self.pause_btn.setEnabled(True)
        self.reset_btn.setEnabled(True)
        self.add_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def update_timer(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_timer_display()

            progress = ((self.total_seconds - self.remaining_seconds) / self.total_seconds) * 100
            self.progress_bar.setValue(int(progress))

        if self.remaining_seconds <= 0:
            self.timer.stop()
            self.update_timer_display()
            self.progress_bar.setValue(100)
            QMessageBox.information(self, "Time's Up", "Study time completed!")
            self.pause_btn.setEnabled(False)
            self.reset_btn.setEnabled(False)
            self.add_btn.setEnabled(True)
            self.task_list.item(self.current_task_index).setBackground(Qt.white)

    def update_timer_display(self):
        mins, secs = divmod(self.remaining_seconds, 60)
        self.timer_label.setText(f"⏳ {mins:02d}:{secs:02d}")

    def pause_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.pause_btn.setText("▶️ Resume")
        else:
            self.timer.start(1000)
            self.pause_btn.setText("⏸️ Pause")

    def reset_timer(self):
        self.timer.stop()
        self.remaining_seconds = self.total_seconds
        self.update_timer_display()
        self.progress_bar.setValue(0)
        self.pause_btn.setEnabled(False)
        self.reset_btn.setEnabled(False)
        self.pause_btn.setText("⏸️ Pause")
        self.add_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.task_list.item(self.current_task_index).setBackground(Qt.white)

    def closeEvent(self, event):
        self.db.close()  # Close the database connection when the app is closed
        event.accept()