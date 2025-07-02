from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from database import insert_user, create_table, check_user_credentials  
from reset_password_window import ResetPasswordWindow
from MainUI import VirtualStudyRoomUI  

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Window")
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #f3f1fe;")
        self.init_ui()

    def init_ui(self):
        label = QLabel("Welcome to the Virtual Study Room!")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 20))

        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Virtual Study Room")
        self.resize(1000, 500)
        self.setStyleSheet("background-color:#f3f1fe")
        self.init_ui()

        # Ensure the users table exists
        create_table()

    def init_ui(self):
        # Main layout for the entire window
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(30, 10, 30, 10)
        self.main_layout.setSpacing(20)

        # LEFT: Image
        left_label = QLabel()
        pixmap = QPixmap("D:/ICPC/login.jpg")
        if not pixmap.isNull():
            pixmap = pixmap.scaledToWidth(650, Qt.SmoothTransformation)
            left_label.setPixmap(pixmap)
            left_label.setFixedWidth(650)
            left_label.setAlignment(Qt.AlignCenter)
        else:
            left_label.setText("Image not found.")

        # Add the image to the main layout
        self.main_layout.addWidget(left_label, 2)

        # Create the login and signup forms
        self.login_form = self.create_login_form()
        self.signup_form = self.create_signup_form()
        self.signup_form.hide()  # Hide signup form initially

        # Add both forms to the main layout
        self.main_layout.addWidget(self.login_form, 1)
        self.main_layout.addWidget(self.signup_form, 1)

        self.setLayout(self.main_layout)

    def create_login_form(self):
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(30, 10, 30, 10)

        title = QLabel("Sign in")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        input_style = """
            QLineEdit {
                border: none;
                border-bottom: 2px solid black;
                font-size: 16px;
                padding: 5px;
                background: transparent;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2196F3;
            }
        """

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Username")
        self.login_username.setStyleSheet(input_style)

        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Password")
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setStyleSheet(input_style)

        login_button = QPushButton("Sign in")
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        login_button.clicked.connect(self.handle_login)  # Changed from self.login to self.handle_login

        signup_label = QLabel("Don't have an account? <a href='#'>Sign up</a>")
        signup_label.setAlignment(Qt.AlignCenter)
        signup_label.setOpenExternalLinks(False)
        signup_label.linkActivated.connect(self.show_signup_form)

        forgot_password_label = QLabel("<a href='#'>Forgot Password?</a>")
        forgot_password_label.setAlignment(Qt.AlignCenter)
        forgot_password_label.setOpenExternalLinks(False)
        forgot_password_label.linkActivated.connect(self.show_reset_password_form)

        form_layout.addStretch()
        form_layout.addWidget(title)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.login_username)
        form_layout.addWidget(self.login_password)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_button)
        form_layout.addSpacing(10)
        form_layout.addWidget(signup_label)
        form_layout.addSpacing(10)
        form_layout.addWidget(forgot_password_label)
        form_layout.addStretch()

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setFixedWidth(350)

        return form_container

    def handle_login(self):  # Renamed from login to handle_login
        # Get the input data from the login form fields
        username = self.login_username.text()
        password = self.login_password.text()

        if not username or not password:
            QMessageBox.warning(self, "Error", "Please fill in both fields!")
            return

        # Check if the credentials are correct
        if check_user_credentials(username, password):
            QMessageBox.information(self, "Success", "Login successful!")

            # Show the main window after successful login
            self.MainUI = VirtualStudyRoomUI(username)  # Pass the username
            self.MainUI.show()

            # Close the login window
            self.close()
        else:
            QMessageBox.warning(self, "Error", "Invalid username or password!")

    def create_signup_form(self):
        form_layout = QVBoxLayout()
        form_layout.setAlignment(Qt.AlignCenter)
        form_layout.setContentsMargins(30, 10, 30, 10)

        title = QLabel("Create Account")
        title.setFont(QFont("Arial", 20))
        title.setAlignment(Qt.AlignCenter)

        input_style = """
            QLineEdit {
                border: none;
                border-bottom: 2px solid black;
                font-size: 16px;
                padding: 5px;
                background: transparent;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2196F3;
            }
        """

        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Name")
        self.signup_name.setStyleSheet(input_style)

        self.signup_username = QLineEdit()
        self.signup_username.setPlaceholderText("Username")
        self.signup_username.setStyleSheet(input_style)

        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email")
        self.signup_email.setStyleSheet(input_style)

        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("Password")
        self.signup_password.setEchoMode(QLineEdit.Password)
        self.signup_password.setStyleSheet(input_style)

        self.signup_retype_password = QLineEdit()
        self.signup_retype_password.setPlaceholderText("Retype Password")
        self.signup_retype_password.setEchoMode(QLineEdit.Password)
        self.signup_retype_password.setStyleSheet(input_style)

        submit_button = QPushButton("Sign Up")
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3; 
                color: white; 
                padding: 8px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        submit_button.clicked.connect(self.signup)

        login_label = QLabel("Already have an account? <a href='#'>Sign in</a>")
        login_label.setAlignment(Qt.AlignCenter)
        login_label.setOpenExternalLinks(False)
        login_label.linkActivated.connect(self.show_login_form)

        form_layout.addStretch()
        form_layout.addWidget(title)
        form_layout.addSpacing(20)
        form_layout.addWidget(self.signup_name)
        form_layout.addWidget(self.signup_username)
        form_layout.addWidget(self.signup_email)
        form_layout.addWidget(self.signup_password)
        form_layout.addWidget(self.signup_retype_password)
        form_layout.addSpacing(20)
        form_layout.addWidget(submit_button)
        form_layout.addSpacing(10)
        form_layout.addWidget(login_label)
        form_layout.addStretch()

        form_container = QWidget()
        form_container.setLayout(form_layout)
        form_container.setFixedWidth(350)

        return form_container

    def signup(self):
        # Get the input data from the signup form fields
        name = self.signup_name.text()
        username = self.signup_username.text()
        email = self.signup_email.text()
        password = self.signup_password.text()
        retype_password = self.signup_retype_password.text()

        if password != retype_password:
            QMessageBox.warning(self, "Error", "Passwords do not match!")
            return

        if not name or not username or not email or not password:
            QMessageBox.warning(self, "Error", "Please fill in all fields!")
            return

        # Insert user into the database
        if insert_user(name, username, email, password):
            QMessageBox.information(self, "Success", "Account created successfully.")
            self.show_login_form()  # Switch back to login form
        else:
            QMessageBox.warning(self, "Error", "Username or email already exists.")

    def show_signup_form(self):
        """ Show signup form and hide login form """
        self.login_form.hide()
        self.signup_form.show()

    def show_login_form(self):
        """ Show login form and hide signup form """
        self.signup_form.hide()
        self.login_form.show()

    def show_reset_password_form(self):
        """ Open the ResetPasswordWindow when 'Forgot Password?' is clicked """
        self.reset_password_window = ResetPasswordWindow()
        self.reset_password_window.show()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())