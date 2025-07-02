from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QMenuBar, QMenu,
    QAction, QFileDialog, QColorDialog, QFontDialog, QInputDialog
)
from PyQt5.QtGui import QColor, QTextCursor, QTextTableFormat, QFont
from PyQt5.QtCore import Qt


class NotesDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Advanced Notes")
        self.setMinimumSize(800, 600)

        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Arial", 12))

        layout = QVBoxLayout()
        layout.setMenuBar(self.create_menu_bar())
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        # File Menu
        file_menu = QMenu("File", self)
        file_menu.addAction("New", self.new_file)
        file_menu.addAction("Open", self.open_file)
        file_menu.addAction("Save", self.save_file)
        file_menu.addAction("Save As", self.save_file_as)

        # Edit Menu
        edit_menu = QMenu("Edit", self)
        edit_menu.addAction("Undo", self.text_edit.undo)
        edit_menu.addAction("Redo", self.text_edit.redo)
        edit_menu.addAction("Cut", self.text_edit.cut)
        edit_menu.addAction("Copy", self.text_edit.copy)
        edit_menu.addAction("Paste", self.text_edit.paste)
        edit_menu.addAction("Select All", self.text_edit.selectAll)

        # Format Menu
        format_menu = QMenu("Format", self)
        format_menu.addAction("Font", self.select_font)
        format_menu.addAction("Text Color", self.select_text_color)
        format_menu.addAction("Background Color", self.select_background_color)

        # Insert Menu
        insert_menu = QMenu("Insert", self)
        insert_menu.addAction("Table", self.insert_table)

        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(edit_menu)
        menu_bar.addMenu(format_menu)
        menu_bar.addMenu(insert_menu)

        return menu_bar

    # === File Menu Functionalities ===
    def new_file(self):
        self.text_edit.clear()

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt *.md *.rtf *.html)")
        if file_name:
            with open(file_name, "r", encoding="utf-8") as file:
                self.text_edit.setPlainText(file.read())

    def save_file(self):
        try:
            if hasattr(self, 'current_file') and self.current_file:
                with open(self.current_file, "w", encoding="utf-8") as file:
                    file.write(self.text_edit.toPlainText())
            else:
                self.save_file_as()
        except Exception as e:
            print("Save error:", e)

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "Text Files (*.txt)")
        if file_name:
            self.current_file = file_name
            self.save_file()

    # === Format Menu Functionalities ===
    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.text_edit.setCurrentFont(font)

    def select_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_edit.setTextColor(color)

    def select_background_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_edit.setTextBackgroundColor(color)

    # === Insert Menu ===
    def insert_table(self):
        rows, ok1 = QInputDialog.getInt(self, "Insert Table", "Rows:", 2, 1)
        cols, ok2 = QInputDialog.getInt(self, "Insert Table", "Columns:", 2, 1)
        if ok1 and ok2:
            cursor = self.text_edit.textCursor()
            table_format = QTextTableFormat()
            table_format.setBorder(1)
            table_format.setCellPadding(4)
            table_format.setCellSpacing(2)
            table_format.setAlignment(Qt.AlignCenter)
            cursor.insertTable(rows, cols, table_format)
