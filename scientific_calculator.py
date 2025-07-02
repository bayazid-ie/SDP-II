from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit, QHBoxLayout, QRadioButton, QComboBox, QDialog, QSpinBox, QFormLayout, QDialogButtonBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import math
import re

class MatrixDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix Input")
        self.setFixedSize(300, 250)

        # Spinboxes for selecting number of rows and columns
        self.rows_spinbox = QSpinBox(self)
        self.rows_spinbox.setRange(1, 10)
        self.rows_spinbox.setValue(2)

        self.cols_spinbox = QSpinBox(self)
        self.cols_spinbox.setRange(1, 10)
        self.cols_spinbox.setValue(2)

        self.layout = QFormLayout()
        self.layout.addRow("Rows:", self.rows_spinbox)
        self.layout.addRow("Columns:", self.cols_spinbox)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def get_matrix_dimensions(self):
        return self.rows_spinbox.value(), self.cols_spinbox.value()

class ScientificCalculator(QDialog):  # Changed QWidget to QDialog
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scientific Calculator")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #2e3b43;")

        self.history = []

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Display Field
        self.display = QLineEdit()
        self.display.setFont(QFont("Segoe UI", 18))
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(False)  # Allow text entry
        self.display.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        main_layout.addWidget(self.display)

        # Calculator Buttons
        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)
        self.create_buttons()

        # Footer: Deg/Rad and History
        footer_layout = QHBoxLayout()
        self.deg_button = QRadioButton("Deg")
        self.rad_button = QRadioButton("Rad")
        self.deg_button.setChecked(True)

        for btn in [self.deg_button, self.rad_button]:
            btn.setStyleSheet("color: white; font-size: 14px;")
        footer_layout.addWidget(self.deg_button)
        footer_layout.addWidget(self.rad_button)

        self.history_combo = QComboBox()
        self.history_combo.addItem("-- History --")
        self.history_combo.setStyleSheet("""
            padding: 5px;
            font-size: 14px;
        """)
        footer_layout.addWidget(self.history_combo)

        main_layout.addLayout(footer_layout)

        # Initialize state
        self.is_second_function = False

    def create_buttons(self):
        buttons = [
            ["C", "2nd", "π", "e", "[..]", "x", "(", ")", "⇄", "="],
            ["sin", "sin⁻¹", "cot", "√x", "xʸ", "7", "8", "9", "÷"],
            ["cos", "cos⁻¹", "sec", "∛x", "x³", "4", "5", "6", "×"],
            ["tan", "tan⁻¹", "csc", "x²", "1/x", "1", "2", "3", "−"],
            ["ncr", "npr", "%", "log", "10^x", "0", ".", "+", "⌫"]
        ]
        for row, items in enumerate(buttons):
            for col, item in enumerate(items):
                button = QPushButton(item)
                button.setFixedSize(66, 44)
                button.setFont(QFont("Segoe UI", 12))
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #e6e6e6;
                        color: black;
                        border-radius: 6px;
                    }
                    QPushButton:pressed {
                        background-color: #cccccc;
                    }
                """)
                button.clicked.connect(lambda checked, text=item: self.button_click(text))
                self.grid_layout.addWidget(button, row, col)

        # Swap backspace and equal button positions
        backspace_button = self.grid_layout.itemAtPosition(4, 8).widget()
        equal_button = self.grid_layout.itemAtPosition(4, 7).widget()

        self.grid_layout.addWidget(backspace_button, 4, 7)
        self.grid_layout.addWidget(equal_button, 4, 8)

    def button_click(self, text):
        if text == "C":
            self.display.clear()  # Clear the display field
            return
        
        if text == "2nd":
            self.is_second_function = not self.is_second_function
            return
        
        if text == "⌫":
            current_text = self.display.text()
            self.display.setText(current_text[:-1])  # Delete last character
            return
        
        if text == "=":
            try:
                expression = self.display.text()
                result = self.evaluate_expression(expression)
                self.display.setText(str(result))
                self.add_to_history(expression, result)
            except Exception as e:
                self.display.setText(f"Error: {str(e)}")
            return
        
        if text == "[..]":
            # Open matrix dialog to select row/column
            matrix_dialog = MatrixDialog()
            if matrix_dialog.exec_() == QDialog.Accepted:
                rows, cols = matrix_dialog.get_matrix_dimensions()
                matrix_input = f"Matrix ({rows}x{cols})"
                self.display.setText(matrix_input)
            return
        
        if text == "[::]":
            # Placeholder for any other function or toggle
            pass
        
        # Update the display with the button's text
        current_text = self.display.text()
        self.display.setText(current_text + text)

    def evaluate_expression(self, expression):
        # Replace constants
        expression = expression.replace("π", str(math.pi))
        expression = expression.replace("e", str(math.e))
        
        # Replace operators
        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")
        expression = expression.replace("x²", "**2")
        expression = expression.replace("x³", "**3")
        expression = expression.replace("xʸ", "**")
        expression = expression.replace("10^x", "10**")
        expression = expression.replace("√x", "math.sqrt")
        expression = expression.replace("∛x", "pow")  # We'll handle cube root in code
        
        # Define helper functions for missing math functions
        def cot(x):
            return 1 / math.tan(x)
        def sec(x):
            return 1 / math.cos(x)
        def csc(x):
            return 1 / math.sin(x)
        def acot(x):
            return math.atan(1/x) if x != 0 else math.pi/2
        def asec(x):
            return math.acos(1/x)
        def acsc(x):
            return math.asin(1/x)

        # Use regex to find trig function calls like sin(30), cos(45), etc.
        def replace_func(match):
            func = match.group(1)
            arg = match.group(2)
            
            if self.deg_button.isChecked():
                # Degree mode - convert argument degrees to radians before trig functions
                if self.is_second_function:
                    func_map = {
                        "sin": "math.asin",
                        "cos": "math.acos",
                        "tan": "math.atan",
                        "cot": "acot",
                        "sec": "asec",
                        "csc": "acsc"
                    }
                    python_func = func_map[func]
                    return f"math.degrees({python_func}(float({arg})))"
                else:
                    func_map = {
                        "sin": "math.sin",
                        "cos": "math.cos",
                        "tan": "math.tan",
                        "cot": "cot",
                        "sec": "sec",
                        "csc": "csc"
                    }
                    python_func = func_map[func]
                    return f"{python_func}(math.radians(float({arg})))"
            else:
                # Radian mode
                if self.is_second_function:
                    func_map = {
                        "sin": "math.asin",
                        "cos": "math.acos",
                        "tan": "math.atan",
                        "cot": "acot",
                        "sec": "asec",
                        "csc": "acsc"
                    }
                    python_func = func_map[func]
                    return f"{python_func}(float({arg}))"
                else:
                    func_map = {
                        "sin": "math.sin",
                        "cos": "math.cos",
                        "tan": "math.tan",
                        "cot": "cot",
                        "sec": "sec",
                        "csc": "csc"
                    }
                    python_func = func_map[func]
                    return f"{python_func}(float({arg}))"
        
        pattern = r"(sin|cos|tan|cot|sec|csc)\(([^)]+)\)"
        expression = re.sub(pattern, replace_func, expression)
        
        local_scope = {
            "math": math,
            "cot": cot,
            "sec": sec,
            "csc": csc,
            "acot": acot,
            "asec": asec,
            "acsc": acsc,
            "pow": pow,
            "float": float,
            "abs": abs,
        }
        
        try:
            result = eval(expression, {"__builtins__": None}, local_scope)
            return result
        except Exception as e:
            raise ValueError(f"Invalid expression: {expression}, error: {str(e)}")

    def add_to_history(self, expression, result):
        # Add the expression and result to history and update combo box
        history_entry = f"{expression} = {result}"
        self.history.append(history_entry)
        self.history_combo.addItem(history_entry)



