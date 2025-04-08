import sys
import zipfile
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, QFileDialog, QLineEdit, QFrame, QDialog, QDialogButtonBox, QComboBox
import time

class zipauraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("zipaura")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                background-color: #222222;
                color: #e0e0e0;
            }

            #header {
                font-size: 32px;
                font-weight: 700;
                color: #ffffff;
                background: #1c1c1c;
                padding: 20px;
                text-align: center;
                border-bottom: 2px solid #444444;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25);
            }

            .toolbar {
                display: flex;
                gap: 1.5rem;
                margin-bottom: 3rem;
                justify-content: center;
            }

            .toolbar QPushButton {
                padding: 14px 25px;
                background: #448aff;
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
                transition: transform 0.2s ease, background-color 0.3s ease;
            }

            .toolbar QPushButton:hover {
                transform: translateY(-4px);
                background: #2979ff;
            }

            .main-container {
                margin-top: 2rem;
                margin-left: 2rem;
                margin-right: 2rem;
            }

            QTableWidget {
                width: 100%;
                border-collapse: collapse;
                border-radius: 10px;
                background-color: #2a2a2a;
                color: #e0e0e0;
                font-size: 16px;
                border: none;
                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
            }

            QTableWidget::item {
                padding: 15px;
                border-bottom: 1px solid #444444;
            }

            QTableWidget::item:hover {
                background-color: #555555;
            }

            QTableWidget::item:selected {
                background-color: #2979ff;
                color: #ffffff;
            }

            QTableWidget::horizontalHeader {
                background-color: #333333;  /* Dark background for header */
                color: #e0e0e0;
                font-weight: bold;
                padding: 12px;
                text-align: center;
                border-bottom: 2px solid #444444;
            }

            QTableWidget::verticalHeader {
                background-color: #333333;
                color: #e0e0e0;
                font-weight: bold;
                padding: 12px;
                text-align: center;
            }

            QLineEdit {
                padding: 8px;
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 8px;
            }
        """)

        self.initUI()

    def initUI(self):
        self.file_paths = []  # To store selected file paths
        self.archive_file = None  # This will hold the path of the current opened archive
        self.main_layout = QVBoxLayout(self)

        # Header
        header = QLabel("zipaura", self)
        header.setObjectName("header")
        self.main_layout.addWidget(header)

        # Search Bar
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search Files...")
        self.search_bar.textChanged.connect(self.search_files)
        self.main_layout.addWidget(self.search_bar)

        # Toolbar with buttons
        toolbar = QHBoxLayout()
        self.add_files_button = QPushButton("Add Files", self)
        self.add_files_button.clicked.connect(self.add_files)
        self.create_archive_button = QPushButton("Create Archive", self)
        self.create_archive_button.clicked.connect(self.create_archive)
        self.extract_button = QPushButton("Extract", self)
        self.extract_button.clicked.connect(self.extract_files)
        self.delete_button = QPushButton("Delete", self)
        self.delete_button.clicked.connect(self.delete_files)
        self.open_archive_button = QPushButton("Open Archive", self)
        self.open_archive_button.clicked.connect(self.open_archive)
        self.remove_files_button = QPushButton("Remove From Archive", self)
        self.remove_files_button.clicked.connect(self.remove_files)

        toolbar.addWidget(self.add_files_button)
        toolbar.addWidget(self.create_archive_button)
        toolbar.addWidget(self.extract_button)
        toolbar.addWidget(self.delete_button)
        toolbar.addWidget(self.open_archive_button)
        toolbar.addWidget(self.remove_files_button)

        self.main_layout.addLayout(toolbar)

        # File Table
        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(4)
        self.file_table.setHorizontalHeaderLabels(["File Name", "Size", "Compressed", "Date Modified"])

        # Explicitly set the header style for horizontal headers
        header = self.file_table.horizontalHeader()
        header.setStyleSheet("""
            QHeaderView::section {
                background-color: #333333;  /* Dark background for header */
                color: #e0e0e0;
                font-weight: bold;
                padding: 12px;
                text-align: center;
                border-bottom: 2px solid #444444;
            }
        """)

        self.main_layout.addWidget(self.file_table)

        self.setLayout(self.main_layout)

    def add_files(self):
        if not self.archive_file:
            self.show_error("No archive opened.")
            return
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if file_paths:
            with zipfile.ZipFile(self.archive_file, 'a') as archive:
                for file_path in file_paths:
                    archive.write(file_path, os.path.basename(file_path))
            self.refresh_archive()

    def create_archive(self):
        # Let the user choose a destination for the archive
        options = QFileDialog.Options()
        archive_file, _ = QFileDialog.getSaveFileName(self, "Save Archive", "", "ZIP Files (*.zip)", options=options)
        
        if archive_file:
            if not archive_file.endswith(".zip"):
                archive_file += ".zip"

            self.archive_file = archive_file  # Set the current archive to the new file
            with zipfile.ZipFile(archive_file, 'w') as archive:
                pass
            self.refresh_archive()

    def extract_files(self):
        if not self.archive_file:
            self.show_error("No archive opened.")
            return
        # Let the user choose a directory to extract the files to
        destination_folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if destination_folder:
            with zipfile.ZipFile(self.archive_file, 'r') as archive:
                archive.extractall(destination_folder)
            print(f"Extracted to: {destination_folder}")

    def delete_files(self):
        # Get selected rows
        selected_rows = self.file_table.selectionModel().selectedRows()
        for row in selected_rows:
            self.file_table.removeRow(row)

    def remove_files(self):
        if not self.archive_file:
            self.show_error("No archive opened.")
            return
        # Get selected rows
        selected_rows = self.file_table.selectionModel().selectedRows()
        file_names = []
        for row in selected_rows:
            item = self.file_table.item(row.row(), 0)
            file_names.append(item.text())

        with zipfile.ZipFile(self.archive_file, 'r') as archive:
            existing_files = archive.namelist()

        # Remove files that were selected
        files_to_remove = [file for file in file_names if file in existing_files]
        if files_to_remove:
            with zipfile.ZipFile(self.archive_file, 'a') as archive:
                temp_archive = zipfile.ZipFile(self.archive_file + ".temp", 'w')
                for file in existing_files:
                    if file not in files_to_remove:
                        temp_archive.write(archive.extract(file), file)
                temp_archive.close()
                os.remove(self.archive_file)
                os.rename(self.archive_file + ".temp", self.archive_file)

            self.refresh_archive()

    def open_archive(self):
        archive_file, _ = QFileDialog.getOpenFileName(self, "Open Archive", "", "ZIP Files (*.zip)", options=QFileDialog.Options())
        if archive_file:
            self.archive_file = archive_file
            self.refresh_archive()

    def refresh_archive(self):
        if not self.archive_file:
            self.show_error("No archive opened.")
        return
            self.file_table.setRowCount(0)  # Clear existing content
        with zipfile.ZipFile(self.archive_file, 'r') as archive:
            file_list = archive.namelist()
            for file in file_list:
                row_position = self.file_table.rowCount()
                self.file_table.insertRow(row_position)
                self.file_table.setItem(row_position, 0, QTableWidgetItem(file))
                file_size = archive.getinfo(file).file_size
                self.file_table.setItem(row_position, 1, QTableWidgetItem(f"{file_size / 1024 / 1024:.2f} MB"))
                self.file_table.setItem(row_position, 2, QTableWidgetItem(f"{file_size / 1024 / 1024:.2f} MB"))  # Dummy compressed size

                # Formatting the date from the tuple (year, month, day, hour, minute, second)
                date_tuple = archive.getinfo(file).date_time
                date_modified = f"{date_tuple[1]:02d}/{date_tuple[2]:02d}/{date_tuple[0]} {date_tuple[3]:02d}:{date_tuple[4]:02d}:{date_tuple[5]:02d}"
                self.file_table.setItem(row_position, 3, QTableWidgetItem(date_modified))


    def show_error(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        error_dialog.setGeometry(100, 100, 300, 150)
        error_label = QLabel(message, error_dialog)
        error_label.setAlignment(Qt.AlignCenter)
        error_dialog.exec_()

    def search_files(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            if search_text in item.text().lower():
                self.file_table.setRowHidden(row, False)
            else:
                self.file_table.setRowHidden(row, True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = zipauraGUI()
    window.show()
    sys.exit(app.exec_())
