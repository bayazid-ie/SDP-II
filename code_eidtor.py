import os
import tempfile
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QFileDialog,
    QLabel, QComboBox, QStatusBar, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QTextCursor, QTextCharFormat, QSyntaxHighlighter
from PyQt5.QtCore import QProcess, Qt, QRegExp, pyqtSignal

class CppHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlightingRules = []
        
        # C/C++ keywords
        keywords = [
            "\\basm\\b", "\\bauto\\b", "\\bbool\\b", "\\bbreak\\b", "\\bcase\\b",
            "\\bcatch\\b", "\\bchar\\b", "\\bclass\\b", "\\bconst\\b", "\\bconst_cast\\b",
            "\\bcontinue\\b", "\\bdefault\\b", "\\bdelete\\b", "\\bdo\\b", "\\bdouble\\b",
            "\\bdynamic_cast\\b", "\\belse\\b", "\\benum\\b", "\\bexplicit\\b", "\\bexport\\b",
            "\\bextern\\b", "\\bfalse\\b", "\\bfloat\\b", "\\bfor\\b", "\\bfriend\\b",
            "\\bgoto\\b", "\\bif\\b", "\\binline\\b", "\\bint\\b", "\\blong\\b",
            "\\bmutable\\b", "\\bnamespace\\b", "\\bnew\\b", "\\boperator\\b", "\\bprivate\\b",
            "\\bprotected\\b", "\\bpublic\\b", "\\bregister\\b", "\\breinterpret_cast\\b",
            "\\breturn\\b", "\\bshort\\b", "\\bsigned\\b", "\\bsizeof\\b", "\\bstatic\\b",
            "\\bstatic_cast\\b", "\\bstruct\\b", "\\bswitch\\b", "\\btemplate\\b", "\\bthis\\b",
            "\\bthrow\\b", "\\btrue\\b", "\\btry\\b", "\\btypedef\\b", "\\btypeid\\b",
            "\\btypename\\b", "\\bunion\\b", "\\bunsigned\\b", "\\busing\\b", "\\bvirtual\\b",
            "\\bvoid\\b", "\\bvolatile\\b", "\\bwchar_t\\b", "\\bwhile\\b"
        ]
        
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        for pattern in keywords:
            self.highlightingRules.append((QRegExp(pattern), keyword_format))
        
        # Preprocessor directives
        preprocessor_format = QTextCharFormat()
        preprocessor_format.setForeground(QColor("#C586C0"))
        self.highlightingRules.append((QRegExp("#.*"), preprocessor_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.highlightingRules.append((QRegExp("\".*\""), string_format))
        self.highlightingRules.append((QRegExp("\'.*\'"), string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.highlightingRules.append((QRegExp("//[^\n]*"), comment_format))
        self.highlightingRules.append((QRegExp("/\\*.*\\*/"), comment_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.highlightingRules.append((QRegExp("\\b\\d+\\b"), number_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            expression = QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)
        
        self.setCurrentBlockState(0)

class CodeEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("C/C++ Editor")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            QLabel {
                color: #c586c0;
                font-weight: bold;
            }
        """)
        
        self.current_file = None
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.read_stdout)
        self.process.readyReadStandardError.connect(self.read_stderr)
        
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Toolbar
        toolbar = QHBoxLayout()
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["C", "C++"])
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #333;
                color: #fff;
                padding: 4px;
                border: 1px solid #444;
                border-radius: 4px;
            }
        """)
        self.lang_combo.setFixedWidth(100)
        
        self.run_btn = self.create_button("Run", self.run_code, "#0e639c")
        self.open_btn = self.create_button("Open", self.open_file, "#007acc")
        self.save_btn = self.create_button("Save", self.save_file, "#388a34")
        self.save_as_btn = self.create_button("Save As", self.save_file_as, "#388a34")
        self.clear_btn = self.create_button("Clear", self.clear_output, "#d6563c")
        
        toolbar.addWidget(self.lang_combo)
        toolbar.addStretch(1)
        toolbar.addWidget(self.open_btn)
        toolbar.addWidget(self.save_btn)
        toolbar.addWidget(self.save_as_btn)
        toolbar.addWidget(self.run_btn)
        toolbar.addWidget(self.clear_btn)
        
        # Editor
        self.editor = QPlainTextEdit()
        self.editor.setFont(QFont("Consolas", 12))
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #444;
            }
        """)
        self.highlighter = CppHighlighter(self.editor.document())
        
        # Output
        self.output = QPlainTextEdit()
        self.output.setFont(QFont("Consolas", 11))
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #444;
            }
        """)
        self.output.setReadOnly(True)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2d2d2d;
                color: #9cdcfe;
                border: 1px solid #444;
                padding-left: 5px;
            }
        """)
        self.status_bar.showMessage("Ready")
        
        # Layout
        layout.addLayout(toolbar)
        layout.addWidget(QLabel("Editor:"))
        layout.addWidget(self.editor)
        layout.addWidget(QLabel("Output:"))
        layout.addWidget(self.output)
        layout.addWidget(self.status_bar)

    def create_button(self, text, slot, color):
        btn = QPushButton(text)
        btn.clicked.connect(slot)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {self.lighten_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color)};
            }}
        """)
        return btn
    
    def lighten_color(self, hex_color, amount=20):
        r = min(255, int(hex_color[1:3], 16) + amount)
        g = min(255, int(hex_color[3:5], 16) + amount)
        b = min(255, int(hex_color[5:7], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def darken_color(self, hex_color, amount=20):
        r = max(0, int(hex_color[1:3], 16) - amount)
        g = max(0, int(hex_color[3:5], 16) - amount)
        b = max(0, int(hex_color[5:7], 16) - amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, 
            "Open File", 
            "", 
            "C/C++ Files (*.c *.cpp *.h *.hpp);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'r') as file:
                    self.editor.setPlainText(file.read())
                    self.current_file = path
                    self.update_language_by_extension(path)
                    self.status_bar.showMessage(f"Opened: {path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{str(e)}")
    
    def save_file(self):
        if self.current_file:
            self._save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        default_ext = ".cpp" if self.lang_combo.currentText() == "C++" else ".c"
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save File",
            f"untitled{default_ext}",
            f"{self.lang_combo.currentText()} Files (*{default_ext});;All Files (*)"
        )
        if path:
            self._save_to_file(path)
            self.current_file = path
    
    def _save_to_file(self, path):
        try:
            with open(path, 'w') as file:
                file.write(self.editor.toPlainText())
                self.status_bar.showMessage(f"Saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def update_language_by_extension(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext == '.c':
            self.lang_combo.setCurrentIndex(0)  # C
        elif ext in ('.cpp', '.h', '.hpp'):
            self.lang_combo.setCurrentIndex(1)  # C++
    
    def run_code(self):
        if not self.editor.toPlainText().strip():
            QMessageBox.warning(self, "Warning", "Editor is empty!")
            return
        
        self.output.clear()
        self.status_bar.showMessage("Running...")
        
        code = self.editor.toPlainText()
        is_cpp = self.lang_combo.currentText() == "C++"
        
        try:
            # Create temp file
            with tempfile.NamedTemporaryFile(
                mode='w', 
                delete=False, 
                suffix='.cpp' if is_cpp else '.c'
            ) as tmp_file:
                tmp_file.write(code)
                tmp_path = tmp_file.name
            
            # Determine compiler and executable path
            compiler = "g++" if is_cpp else "gcc"
            exe_path = tmp_path + (".exe" if os.name == 'nt' else ".out")
            
            # Compile
            compile_cmd = [compiler, tmp_path, "-o", exe_path]
            compile_proc = QProcess()
            compile_proc.start(compile_cmd[0], compile_cmd[1:])
            
            if not compile_proc.waitForFinished(5000):
                raise Exception("Compilation timed out")
            
            if compile_proc.exitCode() != 0:
                error = compile_proc.readAllStandardError().data().decode()
                raise Exception(f"Compilation failed:\n{error}")
            
            # Run
            self.process.start(exe_path)
            
        except Exception as e:
            self.output.appendPlainText(f"Error: {str(e)}")
            self.status_bar.showMessage("Execution failed")
    
    def clear_output(self):
        self.output.clear()
        self.status_bar.showMessage("Output cleared")
    
    def read_stdout(self):
        text = self.process.readAllStandardOutput().data().decode()
        self.output.appendPlainText(text)
    
    def read_stderr(self):
        text = self.process.readAllStandardError().data().decode()
        self.output.appendPlainText(f"Error: {text}")
    
    def closeEvent(self, event):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(1000):
                self.process.kill()
        event.accept()

