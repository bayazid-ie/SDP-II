from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QLineEdit,
    QHBoxLayout, QRadioButton, QComboBox, QDialog, QSpinBox, QFormLayout, QDialogButtonBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import math

class MatrixDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Matrix Input")
        self.setFixedSize(300, 250)

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


class ScientificCalculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scientific Calculator")
        self.setFixedSize(700, 500)
        self.setStyleSheet("background-color: #2e3b43;")

        self.history = []

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.display = QLineEdit()
        self.display.setFont(QFont("Segoe UI", 18))
        self.display.setAlignment(Qt.AlignRight)
        self.display.setReadOnly(False)
        self.display.setStyleSheet("""
            background-color: white;
            padding: 10px;
            border-radius: 8px;
        """)
        main_layout.addWidget(self.display)

        self.grid_layout = QGridLayout()
        main_layout.addLayout(self.grid_layout)
        self.create_buttons()

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
        self.is_second_function = False

    def create_buttons(self):
        buttons = [
            ["2nd", "π", "e", "[::]", "x", "(", ")", "⇄", "="],
            ["sin", "sinh", "cot", "∛x", "xʸ", "7", "8", "9", "÷"],
            ["cos", "cosh", "sec", "√x", "x³", "4", "5", "6", "×"],
            ["tan", "tanh", "csc", "x²", "1/x", "1", "2", "3", "−"],
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
        equal_button = self.grid_layout.itemAtPosition(0, 8).widget()
        self.grid_layout.addWidget(backspace_button, 0, 8)
        self.grid_layout.addWidget(equal_button, 4, 8)

    def button_click(self, text):
        if text == "C":
            self.display.clear()
            return

        if text == "2nd":
            self.is_second_function = not self.is_second_function
            return

        if text == "⌫":
            current_text = self.display.text()
            self.display.setText(current_text[:-1])
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

        if text == "[::]":
            matrix_dialog = MatrixDialog()
            if matrix_dialog.exec_() == QDialog.Accepted:
                rows, cols = matrix_dialog.get_matrix_dimensions()
                matrix_input = f"Matrix ({rows}x{cols})"
                self.display.setText(matrix_input)
            return

        current = self.display.text()

        # Special formatting behavior
        if text == "x²":
            self.display.setText(current + "**2")
            return
        if text == "x³":
            self.display.setText(current + "**3")
            return
        if text == "xʸ":
            self.display.setText(current + "**")
            return
        if text == "√x":
            self.display.setText(f"math.sqrt({current})")
            return
        if text == "∛x":
            self.display.setText(f"({current})**(1/3)")
            return
        if text == "1/x":
            self.display.setText(f"1/({current})")
            return
        if text == "10^x":
            self.display.setText(f"10**({current})")
            return
        if text == "x":
            return  # Ignore inserting plain x

        self.display.setText(current + text)

    def evaluate_expression(self, expression):
        expression = expression.replace("π", str(math.pi))
        expression = expression.replace("e", str(math.e))
        expression = expression.replace("log", "math.log10")

        if self.deg_button.isChecked():
            expression = expression.replace("sin", "math.sin(math.radians")
            expression = expression.replace("cos", "math.cos(math.radians")
            expression = expression.replace("tan", "math.tan(math.radians")
            expression = expression.replace("cot", "1/math.tan(math.radians")
            expression = expression.replace("sec", "1/math.cos(math.radians")
            expression = expression.replace("csc", "1/math.sin(math.radians")
        else:
            expression = expression.replace("sin", "math.sin")
            expression = expression.replace("cos", "math.cos")
            expression = expression.replace("tan", "math.tan")
            expression = expression.replace("cot", "1/math.tan")
            expression = expression.replace("sec", "1/math.cos")
            expression = expression.replace("csc", "1/math.sin")

        if self.is_second_function:
            expression = expression.replace("math.sin", "math.asin")
            expression = expression.replace("math.cos", "math.acos")
            expression = expression.replace("math.tan", "math.atan")

        expression = expression.replace("×", "*")
        expression = expression.replace("÷", "/")
        expression = expression.replace("−", "-")

        try:
            result = eval(expression)
            return result
        except Exception as e:
            raise ValueError(f"Invalid expression: {expression}")

    def add_to_history(self, expression, result):
        history_entry = f"{expression} = {result}"
        self.history.append(history_entry)
        self.history_combo.addItem(history_entry)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ScientificCalculator()
    win.show()
    sys.exit(app.exec_())
