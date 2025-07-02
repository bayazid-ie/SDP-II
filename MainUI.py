from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout, QScrollArea,
    QFrame, QDialog, QHBoxLayout, QPushButton, QMenu, QSlider, QCheckBox,
    QColorDialog, QFormLayout, QMessageBox, QLineEdit, QTextEdit
)
from PyQt5.QtGui import QFont, QPixmap, QCursor, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from scientific_calculator import ScientificCalculator
from notes import NotesDialog
from img_to_pdf import ImageToPDFDialog
from study_timer import StudyTimerDialog
from code_eidtor import CodeEditor
from task_scheduler import TaskSchedulerDialog

from database import get_user_info, update_user_profile
from study_room import StudyRoomWindow
from database import get_user_info

class VirtualStudyRoomUI(QWidget):
    def __init__(self, username=None):
        super().__init__()
        self.setWindowTitle("EduVerse - An all-encompassing academic universe for students")
        self.resize(1000, 500)
        self.username = username
        self.dark_mode = False
        self.font_size = 14
        self.font_color = "black"

        self.init_ui()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Top Bar
        top_bar = QHBoxLayout()
        self.title_label = QLabel("EduVerse", self)
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)

        self.profile_button = QPushButton(self)
        self.profile_button.setFixedSize(40, 40)
        self.load_profile_icon()
        self.profile_button.setCursor(QCursor(Qt.PointingHandCursor))
        self.profile_button.setStyleSheet("""
            QPushButton::menu-indicator { image: none; }
            border-radius: 20px;
            border: none;
        """)

        self.profile_menu = QMenu(self)
        self.profile_menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 8px 20px;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
        """)
        self.profile_menu.addAction("View Profile", self.view_profile)
        self.profile_menu.addAction("Settings", self.open_settings)
        self.profile_menu.addAction("Logout", self.logout)
        self.profile_button.setMenu(self.profile_menu)

        top_bar.addWidget(self.title_label, 1)
        top_bar.addWidget(self.profile_button, 0, Qt.AlignRight)
        self.main_layout.addLayout(top_bar)

        # Scrollable Feature Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("border: none;")

        self.content_widget = QWidget()
        self.grid_layout = QGridLayout(self.content_widget)
        self.grid_layout.setSpacing(15)

        self.features = [
            ("Study Room", "#2193b0", "#6dd5ed"),
            ("Code Editor", "#11998e", "#38ef7d"),
            ("Study Timer", "#fc4a1a", "#f7b733"),
            ("Task Scheduler", "#56ab2f", "#a8e063"),
            ("Calculator", "#ff512f", "#dd2476"),
            ("Img To Pdf", "#ff6347", "#4169e1"),
            ("Notes", "#ff7e5f", "#feb47b")
        ]

        self.load_feature_cards()
        self.scroll_area.setWidget(self.content_widget)
        self.main_layout.addWidget(self.scroll_area)
        self.apply_styles()

    def load_feature_cards(self):
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)

        row, col = 0, 0
        for feature, color1, color2 in self.features:
            card = self.create_feature_card(feature, color1, color2)
            self.grid_layout.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def create_feature_card(self, feature_name, color1, color2):
        card = QFrame(self)
        card.setFixedSize(300, 120)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color1}, stop:1 {color2});
                border-radius: 10px;
                border: none;
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 {color2}, stop:1 {color1});
            }}
        """)
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)

        feature_label = QLabel(feature_name, card)
        feature_label.setFont(QFont("Arial", self.font_size, QFont.Bold))
        feature_label.setAlignment(Qt.AlignCenter)
        feature_label.setStyleSheet(f"color: white; background: transparent;")

        card.mousePressEvent = lambda event: self.on_card_click(feature_name)

        layout.addWidget(feature_label)
        return card
    def on_card_click(self, feature_name):
        if feature_name == "Calculator":
            dialog = ScientificCalculator()
        elif feature_name == "Notes":
            dialog = NotesDialog()
        elif feature_name == "Img To Pdf":
            dialog = ImageToPDFDialog()
        elif feature_name == "Study Timer":
            dialog = StudyTimerDialog()
        elif feature_name == "Code Editor":
            dialog = CodeEditor()
        elif feature_name == "Task Scheduler":
            dialog = TaskSchedulerDialog()
        elif feature_name == "Study Room":
            dialog = StudyRoomWindow(self.username)
        

        else:
            dialog = FeatureDialog(feature_name)
        dialog.exec_()

    def load_profile_icon(self):
        pixmap = QPixmap("profile.png")
        if pixmap.isNull():
            self.profile_button.setText("👤")
            self.profile_button.setStyleSheet("""
                font-size: 20px;
                border: none;
                background-color: white;
                QPushButton::menu-indicator { image: none; }
                border-radius: 20px;
            """)
        else:
            pixmap = pixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_button.setIcon(pixmap)
            self.profile_button.setIconSize(self.profile_button.size())

    def view_profile(self):
        if hasattr(self, 'username') and self.username:
            dialog = ProfileDialog(self.username)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No user information available.")

    def open_settings(self):
        dialog = SettingsDialog(self.dark_mode, self.font_size, self.font_color)
        dialog.settings_updated.connect(self.update_settings)
        dialog.exec_()

    def update_settings(self, dark, size, color):
        self.dark_mode = dark
        self.font_size = size
        self.font_color = color
        self.apply_styles()

    def apply_styles(self):
        bg_color = "#2e2e2e" if self.dark_mode else "#f3f1fe"
        text_color = self.font_color if not self.dark_mode else "white"
        self.setStyleSheet(f"background-color: {bg_color}; color: {text_color};")
        self.title_label.setFont(QFont("Arial", self.font_size + 4, QFont.Bold))
        self.title_label.setStyleSheet(f"color: {text_color};")
        self.load_feature_cards()

    def logout(self):
        dialog = QMessageBox(self)
        dialog.setWindowTitle("Logout")
        dialog.setText("You have been logged out.")
        dialog.exec_()

class ProfileDialog(QDialog):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.setWindowTitle("Edit Profile")
        self.setMinimumSize(500, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("Edit Your Profile")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setVerticalSpacing(15)
        
        # Load current profile
        profile = get_user_info(self.username)
        
        # Non-editable username
        form_layout.addRow("Username:", QLabel(self.username))
        
        # Editable fields
        self.fields = {}
        profile_fields = [
            ('name', 'Full Name:'),
            ('email', 'Email:'),
            ('university', 'University:'),
            ('department', 'Department:'),
            ('address', 'Address:'),
            ('phone', 'Phone:'),
            ('bio', 'Bio:')
        ]
        
        for field, label in profile_fields:
            lbl = QLabel(label)
            if field == 'bio':
                input_widget = QTextEdit()
                input_widget.setPlainText(profile.get(field, ''))
                input_widget.setMaximumHeight(100)
            else:
                input_widget = QLineEdit()
                input_widget.setText(profile.get(field, ''))
            
            self.fields[field] = input_widget
            form_layout.addRow(lbl, input_widget)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_profile)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
    
    def save_profile(self):
        updates = {}
        for field, widget in self.fields.items():
            if isinstance(widget, QTextEdit):
                updates[field] = widget.toPlainText()
            else:
                updates[field] = widget.text()
        
        if update_user_profile(self.username, **updates):
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "Failed to update profile")

class FeatureDialog(QDialog):
    def __init__(self, feature_name):
        super().__init__()
        self.setWindowTitle(feature_name)
        self.setFixedSize(400, 300)
        layout = QVBoxLayout(self)
        label = QLabel(f"Welcome to {feature_name}!", self)
        label.setFont(QFont("Arial", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        self.setLayout(layout)

class SettingsDialog(QDialog):
    settings_updated = pyqtSignal(bool, int, str)

    def __init__(self, dark_mode=False, font_size=14, font_color="black"):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 250)
        self.selected_color = font_color

        self.dark_mode_checkbox = QCheckBox("Dark Mode", self)
        self.dark_mode_checkbox.setChecked(dark_mode)
        self.dark_mode_checkbox.stateChanged.connect(self.emit_settings)

        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setRange(10, 30)
        self.font_size_slider.setValue(font_size)
        self.font_size_slider.valueChanged.connect(self.emit_settings)

        self.font_color_button = QPushButton("Select Font Color", self)
        self.font_color_button.clicked.connect(self.select_font_color)

        layout = QVBoxLayout(self)
        layout.addWidget(self.dark_mode_checkbox)
        layout.addWidget(self.font_size_slider)
        layout.addWidget(self.font_color_button)

        self.setLayout(layout)

    def emit_settings(self):
        dark = self.dark_mode_checkbox.isChecked()
        size = self.font_size_slider.value()
        self.settings_updated.emit(dark, size, self.selected_color)

    def select_font_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()

