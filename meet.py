from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QGroupBox, QSpacerItem,
                             QSizePolicy, QFrame)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QFont, QIcon


class Meetup(QDialog):
    def __init__(self):
        super().__init__()

        # Main window setup
        self.setWindowTitle("Video Conference")
        self.setFixedSize(1280, 800)
        self.setWindowIcon(QIcon(":/icons/video_call.png"))  # Replace with your icon

        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(20)

        # Create header
        header = QLabel("Video Conference")
        header.setFont(QFont("Arial", 24, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        main_layout.addWidget(header)

        # Create horizontal layout for controls and webview
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Create control panel
        control_panel = QGroupBox("Meeting Controls")
        control_panel.setFixedWidth(350)
        control_panel.setStyleSheet("""
            QGroupBox {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 20px;
                padding-top: 20px;
                background-color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                font-weight: bold;
                color: #34495e;
            }
        """)
        
        control_layout = QVBoxLayout()
        control_layout.setSpacing(20)
        control_layout.setContentsMargins(20, 20, 20, 20)

        # Room name input
        room_label = QLabel("Room Name:")
        room_label.setFont(QFont("Arial", 12))
        room_label.setStyleSheet("color: #34495e;")
        
        self.room_input = QLineEdit()
        self.room_input.setPlaceholderText("Enter room name")
        self.room_input.setText("StudyRoom123")
        self.room_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                font-size: 16px;
            }
        """)

        # Buttons
        self.start_button = QPushButton("Start Meeting")
        self.start_button.clicked.connect(self.start_new_meeting)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        self.end_button = QPushButton("End Meeting")
        self.end_button.clicked.connect(self.end_meeting)
        self.end_button.setEnabled(False)
        self.end_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)

        # Add widgets to control layout
        control_layout.addWidget(room_label)
        control_layout.addWidget(self.room_input)
        control_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        control_layout.addWidget(self.start_button)
        control_layout.addWidget(self.end_button)
        control_layout.addStretch()

        control_panel.setLayout(control_layout)
        content_layout.addWidget(control_panel)

        # Create webview container
        webview_container = QFrame()
        webview_container.setFrameShape(QFrame.StyledPanel)
        webview_container.setStyleSheet("""
            QFrame {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        
        webview_layout = QVBoxLayout()
        webview_layout.setContentsMargins(0, 0, 0, 0)

        # Status label
        self.status_label = QLabel("Ready to start a meeting")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 16px; padding: 10px;")
        webview_layout.addWidget(self.status_label)

        # Webview
        self.webview = QWebEngineView()
        webview_layout.addWidget(self.webview)
        
        webview_container.setLayout(webview_layout)
        content_layout.addWidget(webview_container)

        main_layout.addLayout(content_layout)

        # Add footer
        footer = QLabel("© 2023 Video Conference App")
        footer.setFont(QFont("Arial", 8))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("color: #7f8c8d; padding: 10px;")
        main_layout.addWidget(footer)

        self.setLayout(main_layout)

    def start_new_meeting(self):
        room_name = self.room_input.text().strip() or "StudyRoom123"
        jitsi_url = f"https://meet.jit.si/{room_name}"
        self.webview.setUrl(QUrl(jitsi_url))
        self.status_label.setText(f"Meeting in progress: {room_name}")
        self.start_button.setEnabled(False)
        self.end_button.setEnabled(True)
        self.room_input.setEnabled(False)

    def end_meeting(self):
        self.webview.setUrl(QUrl("about:blank"))
        self.status_label.setText("Meeting ended")
        self.start_button.setEnabled(True)
        self.end_button.setEnabled(False)
        self.room_input.setEnabled(True)
