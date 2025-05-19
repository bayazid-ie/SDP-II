# notes_sharing.py

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QListWidget, QFileDialog,
    QMessageBox, QHBoxLayout, QLineEdit, QListWidgetItem, QComboBox
)
from PyQt5.QtGui import QFont, QIcon
import os
import shutil
import subprocess

NOTES_DIR = "shared_notes"

class NotesSharingDialog(QDialog):
    def __init__(self, username=None):
        super().__init__()
        self.setWindowTitle("Notes Sharing")
        self.setFixedSize(600, 500)
        self.username = username
        self.all_notes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("Shared Notes")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(title)

        search_layout = QHBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search notes...")
        self.search_bar.textChanged.connect(self.search_notes)
        search_layout.addWidget(self.search_bar)

        self.sort_box = QComboBox()
        self.sort_box.addItems(["Sort by Name", "Sort by Uploader", "Sort by File Type"])
        self.sort_box.currentIndexChanged.connect(self.sort_notes)
        search_layout.addWidget(self.sort_box)

        layout.addLayout(search_layout)

        self.notes_list = QListWidget()
        layout.addWidget(self.notes_list)

        button_layout = QHBoxLayout()

        upload_btn = QPushButton("Upload Note")
        upload_btn.clicked.connect(self.upload_note)
        button_layout.addWidget(upload_btn)

        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.preview_note)
        button_layout.addWidget(preview_btn)

        download_btn = QPushButton("Download Selected")
        download_btn.clicked.connect(self.download_note)
        button_layout.addWidget(download_btn)

        delete_btn = QPushButton("Delete Selected")
        delete_btn.clicked.connect(self.delete_note)
        button_layout.addWidget(delete_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        os.makedirs(NOTES_DIR, exist_ok=True)
        self.load_notes()

    def load_notes(self):
        self.notes_list.clear()
        self.all_notes.clear()

        for file_name in os.listdir(NOTES_DIR):
            if "_" in file_name:
                uploader, original_name = file_name.split("_", 1)
                display = f"{original_name} (uploaded by {uploader})"
            else:
                display = file_name

            self.all_notes.append((display, file_name))

        self.display_notes(self.all_notes)

    def display_notes(self, notes):
        self.notes_list.clear()
        for display, filename in notes:
            item = QListWidgetItem()
            item.setText(display)
            item.setData(1000, filename)

            if filename.endswith(".txt"):
                item.setIcon(QIcon.fromTheme("text-x-generic"))
                item.setText(f"📄 {display}")
            elif filename.endswith(".pdf"):
                item.setIcon(QIcon.fromTheme("application-pdf"))
                item.setText(f"📕 {display}")
            else:
                item.setIcon(QIcon.fromTheme("unknown"))
                item.setText(f"📁 {display}")

            self.notes_list.addItem(item)

    def search_notes(self, text):
        filtered = [(d, f) for d, f in self.all_notes if text.lower() in d.lower()]
        self.display_notes(filtered)

    def sort_notes(self):
        index = self.sort_box.currentIndex()
        if index == 0:
            sorted_notes = sorted(self.all_notes, key=lambda x: x[0].lower())  # Name
        elif index == 1:
            sorted_notes = sorted(self.all_notes, key=lambda x: x[1].split("_")[0].lower())  # Uploader
        elif index == 2:
            sorted_notes = sorted(self.all_notes, key=lambda x: os.path.splitext(x[1])[-1].lower())  # File type
        else:
            sorted_notes = self.all_notes

        self.display_notes(sorted_notes)

    def get_selected_filename(self):
        selected = self.notes_list.currentItem()
        if not selected:
            return None
        return selected.data(1000)

    def upload_note(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Note File")
        if file_path:
            file_name = os.path.basename(file_path)
            dest_file_name = f"{self.username}_{file_name}" if self.username else file_name
            dest_path = os.path.join(NOTES_DIR, dest_file_name)
            try:
                shutil.copy(file_path, dest_path)
                self.load_notes()
                QMessageBox.information(self, "Success", "Note uploaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to upload note.\n{str(e)}")

    def preview_note(self):
        actual_filename = self.get_selected_filename()
        if actual_filename:
            full_path = os.path.join(NOTES_DIR, actual_filename)

            try:
                if actual_filename.lower().endswith(".txt"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                    QMessageBox.information(self, "Text Preview", content[:3000])
                elif actual_filename.lower().endswith(".pdf"):
                    subprocess.Popen([full_path], shell=True)
                else:
                    QMessageBox.warning(self, "Preview Unsupported", "Only .txt and .pdf preview supported.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not preview file.\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a note to preview.")

    def download_note(self):
        actual_filename = self.get_selected_filename()
        if actual_filename:
            save_path, _ = QFileDialog.getSaveFileName(self, "Save Note As", actual_filename)
            if save_path:
                try:
                    shutil.copy(os.path.join(NOTES_DIR, actual_filename), save_path)
                    QMessageBox.information(self, "Success", "Note downloaded successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Download failed.\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a note to download.")

    def delete_note(self):
        actual_filename = self.get_selected_filename()
        if actual_filename:
            confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this note?")
            if confirm == QMessageBox.Yes:
                try:
                    os.remove(os.path.join(NOTES_DIR, actual_filename))
                    self.load_notes()
                    QMessageBox.information(self, "Deleted", "Note deleted successfully.")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Delete failed.\n{str(e)}")
        else:
            QMessageBox.warning(self, "No Selection", "Please select a note to delete.")
