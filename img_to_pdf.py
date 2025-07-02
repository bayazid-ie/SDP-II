from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QFileDialog, QListWidget, QListWidgetItem,
    QLabel, QHBoxLayout, QMessageBox, QTextEdit
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize
from PIL import Image
import os

# ✅ Custom QListWidget to support drag & drop from file explorer
class DraggableImageList(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setIconSize(QSize(100, 100))

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self.parent().add_image(path)
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class ImageToPDFDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image to PDF Converter")
        self.setFixedSize(800, 500)
        self.setStyleSheet("""
            QDialog {
                background-color: #fdf6e3;
            }
            QPushButton {
                background-color: #268bd2;
                color: white;
                padding: 8px 15px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1e6fa4;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #ccc;
            }
        """)

        self.image_paths = []
        self.layout = QVBoxLayout(self)

        self.btn_layout = QHBoxLayout()
        self.select_btn = QPushButton("Select Images")
        self.select_btn.clicked.connect(self.select_images)
        self.btn_layout.addWidget(self.select_btn)

        self.convert_btn = QPushButton("Convert to PDF")
        self.convert_btn.clicked.connect(self.convert_to_pdf)
        self.btn_layout.addWidget(self.convert_btn)

        self.edit_btn = QPushButton("Edit PDF (Add Text)")
        self.edit_btn.clicked.connect(self.edit_pdf)
        self.btn_layout.addWidget(self.edit_btn)

        self.layout.addLayout(self.btn_layout)

        # ✅ Using the custom draggable image list
        self.image_list = DraggableImageList(self)
        self.layout.addWidget(self.image_list)

    def select_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Images", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if files:
            self.image_paths = files
            self.refresh_list()

    def refresh_list(self):
        self.image_list.clear()
        for path in self.image_paths:
            pixmap = QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item = QListWidgetItem(QIcon(pixmap), os.path.basename(path))
            item.setData(Qt.UserRole, path)
            self.image_list.addItem(item)

    # ✅ Used by drag-and-drop to add image if not already in list
    def add_image(self, path):
        if path not in self.image_paths:
            self.image_paths.append(path)
            pixmap = QPixmap(path).scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item = QListWidgetItem(QIcon(pixmap), os.path.basename(path))
            item.setData(Qt.UserRole, path)
            self.image_list.addItem(item)

    def convert_to_pdf(self):
        if self.image_list.count() == 0:
            QMessageBox.warning(self, "Warning", "No images selected!")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if save_path:
            img_list = []
            for i in range(self.image_list.count()):
                path = self.image_list.item(i).data(Qt.UserRole)
                try:
                    img = Image.open(path).convert("RGB")
                    img_list.append(img)
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Failed to open image {path}: {str(e)}")
                    return  # Exit if any image fails to open

            img_list[0].save(save_path, save_all=True, append_images=img_list[1:])
            QMessageBox.information(self, "Success", "PDF created successfully!")

    def edit_pdf(self):
        dialog = PDFEditorDialog()
        dialog.exec_()


class PDFEditorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Basic PDF Editor - Add Text")
        self.setFixedSize(500, 400)
        self.setStyleSheet("""
            QDialog {
                background-color: #fdf6e3;
            }
            QTextEdit {
                font-size: 14px;
                background-color: white;
                border: 1px solid #ccc;
            }
        """)

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit(self)
        layout.addWidget(QLabel("Write content to add to a new page in a PDF:"))
        layout.addWidget(self.text_edit)

        self.save_btn = QPushButton("Save as PDF")
        self.save_btn.clicked.connect(self.save_as_pdf)
        layout.addWidget(self.save_btn)

    def save_as_pdf(self):
        content = self.text_edit.toPlainText()
        if not content.strip():
            QMessageBox.warning(self, "Empty Text", "Please write something before saving.")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
        if save_path:
            from fpdf import FPDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in content.split('\n'):
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.output(save_path)
            QMessageBox.information(self, "Success", "PDF with text saved!")
