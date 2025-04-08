import sys
import zipfile
import rarfile
import os
from datetime import datetime
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QPixmap
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHBoxLayout, QLabel, 
                            QFileDialog, QLineEdit, QFrame, QDialog, QProgressBar,
                            QHeaderView, QMessageBox, QTextEdit, QMainWindow)
from pypresence import Presence  # Import pypresence for Discord Rich Presence
import time

class ContentViewer(QMainWindow):
    def __init__(self, filename, content):
        super().__init__()
        self.setWindowTitle(f"Viewing: {filename}")
        self.setGeometry(150, 150, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(content)
        layout.addWidget(self.text_edit)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QTextEdit {
                background-color: #2a2a2a;
                color: #e0e0e0;
                border: 1px solid #333333;
                border-radius: 4px;
                padding: 4px;
            }
        """)

class zipauraGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("zipaura - Archive Manager")
        self.setGeometry(100, 100, 800, 500)
        self.archive_file = None
        self.current_path = ""
        self.path_history = []
        self.content_viewers = []
        self.archive_type = None
        
        self.setAcceptDrops(True)
        
        # Discord Rich Presence setup
        self.client_id = "1359129471470272552"  # Replace with your Discord Application ID
        self.rpc = Presence(self.client_id)
        self.rpc_connected = False
        self.start_time = time.time()  # Track when the app started for elapsed time
        self.connect_rpc()

        self.setup_styles()
        self.initUI()
        self.update_presence("Idle", "No archive loaded")  # Initial presence

    def connect_rpc(self):
        """Connect to Discord RPC."""
        try:
            self.rpc.connect()
            self.rpc_connected = True
            print("Connected to Discord RPC")
        except Exception as e:
            print(f"Failed to connect to Discord RPC: {e}")
            self.rpc_connected = False

    def update_presence(self, state, details):
        """Update Discord Rich Presence."""
        if self.rpc_connected:
            try:
                self.rpc.update(
                    state=state,  # e.g., "Browsing Archive"
                    details=details,  # e.g., "example.zip"
                    start=self.start_time,  # Show elapsed time since app started
                    large_image="0d917273-f5f9-4040-8ebc-6697581a1e04",  # Replace with an image key from your Discord assets
                    large_text="zipaura - Archive Manager"
                )
                print(f"Updated Rich Presence: {state} - {details}")
            except Exception as e:
                print(f"Failed to update Rich Presence: {e}")

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', sans-serif;
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            #header {
                font-size: 24px;
                font-weight: bold;
                color: #ffffff;
                background: linear-gradient(45deg, #1c2526, #2d3839);
                padding: 10px;
                text-align: center;
                border-bottom: 2px solid #448aff;
            }
            QPushButton {
                padding: 8px 12px;
                background: #448aff;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: 600;
                font-size: 12px;
                transition: all 0.2s;
            }
            QPushButton:hover {
                background: #2962ff;
                transform: translateY(-2px);
            }
            QPushButton:disabled {
                background: #666666;
                color: #999999;
            }
            QTableWidget {
                background-color: #2a2a2a;
                border: 1px solid #333333;
                border-radius: 4px;
                gridline-color: #444444;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QHeaderView::section {
                background-color: #333333;
                color: #e0e0e0;
                padding: 6px;
                border: 1px solid #444444;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit {
                padding: 4px;
                background-color: #333333;
                color: #e0e0e0;
                border: 1px solid #444444;
                border-radius: 4px;
                font-size: 12px;
            }
            QProgressBar {
                border: 1px solid #444444;
                border-radius: 3px;
                text-align: center;
                background-color: #333333;
                height: 12px;
            }
            QProgressBar::chunk {
                background-color: #448aff;
                border-radius: 2px;
            }
        """)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)

        self.header = QLabel("zipaura - Archive Manager", self)
        self.header.setObjectName("header")
        main_layout.addWidget(self.header)

        search_layout = QHBoxLayout()
        search_layout.setSpacing(5)
        self.search_bar = QLineEdit(self)
        self.search_bar.setPlaceholderText("Search files...")
        self.search_bar.textChanged.connect(self.search_files)
        self.status_label = QLabel("No archive loaded")
        search_layout.addWidget(self.search_bar)
        search_layout.addWidget(self.status_label)
        main_layout.addLayout(search_layout)

        toolbar = QHBoxLayout()
        toolbar.setSpacing(5)
        buttons = [
            ("New Archive", self.create_archive),
            ("Open Archive", self.open_archive),
            ("Go Back", self.go_back),
            ("Add Files", self.add_files),
            ("Extract Sel.", self.extract_files),
            ("Remove Sel.", self.remove_files),
            ("Extract All", self.extract_all),
            ("Compress", self.compress_archive),
            ("Decompress", self.decompress_archive),
        ]
        
        self.toolbar_buttons = {}
        for text, handler in buttons:
            btn = QPushButton(text, self)
            btn.clicked.connect(handler)
            toolbar.addWidget(btn)
            self.toolbar_buttons[text] = btn
        
        self.toolbar_buttons["Go Back"].setEnabled(False)
        main_layout.addLayout(toolbar)

        self.file_table = QTableWidget(self)
        self.file_table.setColumnCount(5)
        self.file_table.setHorizontalHeaderLabels([
            "Name", "Size", "Comp. Size", "Ratio", "Modified"
        ])
        self.file_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.file_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.file_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.file_table.doubleClicked.connect(self.handle_double_click)
        main_layout.addWidget(self.file_table)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)

        self.setLayout(main_layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1:
                filename = urls[0].toLocalFile().lower()
                if filename.endswith(('.zip', '.rar')):
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().urls()[0]
        archive_file = url.toLocalFile()
        print(f"Dropped file: {archive_file}")
        self.load_dropped_archive(archive_file)
        event.acceptProposedAction()

    def load_dropped_archive(self, archive_file):
        if not archive_file:
            return
        
        print(f"Attempting to open dropped archive: {archive_file}")
        try:
            if archive_file.lower().endswith('.zip'):
                with zipfile.ZipFile(archive_file, 'r') as test_archive:
                    test_archive.testzip()
                    print(f"ZIP contents: {test_archive.namelist()}")
                self.archive_type = 'zip'
            elif archive_file.lower().endswith('.rar'):
                with rarfile.RarFile(archive_file, 'r') as test_archive:
                    test_archive.testrar()
                    print(f"RAR contents: {test_archive.namelist()}")
                self.archive_type = 'rar'
            else:
                raise ValueError("Unsupported archive format")
            
            self.archive_file = archive_file
            self.current_path = ""
            self.path_history = []
            self.refresh_archive()
            self.update_status(f"Loaded: {os.path.basename(archive_file)}")
            self.update_presence("Browsing Archive", os.path.basename(archive_file))
            self.toolbar_buttons["Go Back"].setEnabled(False)
        except (zipfile.BadZipFile, rarfile.BadRarFile):
            self.show_message("Error", "Invalid or corrupted archive file", QMessageBox.Critical)
        except Exception as e:
            self.show_message("Error", f"Failed to open archive: {str(e)}", QMessageBox.Critical)

    def update_status(self, message):
        self.status_label.setText(message)
        print(f"Status: {message}")

    def show_message(self, title, message, icon=QMessageBox.Information):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setIcon(icon)
        msg.exec_()

    def create_archive(self):
        archive_file, _ = QFileDialog.getSaveFileName(self, "Create New Archive", "", "ZIP Files (*.zip);;RAR Files (*.rar)")
        if archive_file:
            if not (archive_file.endswith('.zip') or archive_file.endswith('.rar')):
                archive_file += '.zip'
            self.archive_file = archive_file
            self.current_path = ""
            self.path_history = []
            try:
                if archive_file.lower().endswith('.zip'):
                    with zipfile.ZipFile(archive_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                        self.archive_type = 'zip'
                elif archive_file.lower().endswith('.rar'):
                    with rarfile.RarFile(archive_file, 'w', compression=rarfile.RAR_M5) as archive:
                        self.archive_type = 'rar'
                self.refresh_archive()
                self.update_status(f"Created: {os.path.basename(archive_file)}")
                self.update_presence("Created Archive", os.path.basename(archive_file))
                self.toolbar_buttons["Go Back"].setEnabled(False)
            except Exception as e:
                self.show_message("Error", f"Failed to create archive: {str(e)}", QMessageBox.Critical)

    def open_archive(self):
        archive_file, _ = QFileDialog.getOpenFileName(self, "Open Archive", "", "ZIP Files (*.zip);;RAR Files (*.rar)")
        if archive_file:
            self.load_dropped_archive(archive_file)

    def add_files(self):
        if not self.archive_file:
            self.show_message("Error", "Please create or open an archive first", QMessageBox.Warning)
            return
        
        files, _ = QFileDialog.getOpenFileNames(self, "Add Files to Archive")
        if files:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(files))
            try:
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(self.archive_file, 'a', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
                        for i, file_path in enumerate(files):
                            arcname = os.path.join(self.current_path, os.path.basename(file_path)).replace('\\', '/')
                            archive.write(file_path, arcname)
                            self.progress_bar.setValue(i + 1)
                elif self.archive_type == 'rar':
                    with rarfile.RarFile(self.archive_file, 'a', compression=rarfile.RAR_M5) as archive:
                        for i, file_path in enumerate(files):
                            arcname = os.path.join(self.current_path, os.path.basename(file_path)).replace('\\', '/')
                            archive.write(file_path, arcname)
                            self.progress_bar.setValue(i + 1)
                self.refresh_archive()
                self.update_presence("Adding Files", os.path.basename(self.archive_file))
            except Exception as e:
                self.show_message("Error", f"Failed to add files: {str(e)}", QMessageBox.Critical)
            finally:
                self.progress_bar.setVisible(False)

    def extract_files(self):
        if not self.archive_file:
            self.show_message("Error", "No archive loaded", QMessageBox.Warning)
            return
        
        selected = self.file_table.selectionModel().selectedRows()
        if not selected:
            self.show_message("Warning", "Please select files to extract", QMessageBox.Warning)
            return

        folder = QFileDialog.getExistingDirectory(self, "Select Extraction Folder")
        if folder:
            try:
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(self.archive_file, 'r') as archive:
                        for index in selected:
                            file_name = os.path.join(self.current_path, self.file_table.item(index.row(), 0).text()).replace('\\', '/')
                            archive.extract(file_name, folder)
                elif self.archive_type == 'rar':
                    with rarfile.RarFile(self.archive_file, 'r') as archive:
                        for index in selected:
                            file_name = os.path.join(self.current_path, self.file_table.item(index.row(), 0).text()).replace('\\', '/')
                            archive.extract(file_name, folder)
                self.show_message("Success", f"Extracted {len(selected)} file(s) to {folder}")
                self.update_presence("Extracting Files", os.path.basename(self.archive_file))
            except Exception as e:
                self.show_message("Error", f"Failed to extract files: {str(e)}", QMessageBox.Critical)

    def extract_all(self):
        if not self.archive_file:
            self.show_message("Error", "No archive loaded", QMessageBox.Warning)
            return
        
        folder = QFileDialog.getExistingDirectory(self, "Select Extraction Folder")
        if folder:
            try:
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(self.archive_file, 'r') as archive:
                        archive.extractall(folder)
                elif self.archive_type == 'rar':
                    with rarfile.RarFile(self.archive_file, 'r') as archive:
                        archive.extractall(folder)
                self.show_message("Success", f"Extracted all files to {folder}")
                self.update_presence("Extracting All", os.path.basename(self.archive_file))
            except Exception as e:
                self.show_message("Error", f"Failed to extract all files: {str(e)}", QMessageBox.Critical)

    def remove_files(self):
        if not self.archive_file:
            self.show_message("Error", "No archive loaded", QMessageBox.Warning)
            return
        
        selected = self.file_table.selectionModel().selectedRows()
        if not selected:
            self.show_message("Warning", "Please select files to remove", QMessageBox.Warning)
            return

        files_to_remove = [os.path.join(self.current_path, self.file_table.item(index.row(), 0).text()).replace('\\', '/') 
                         for index in selected]
        
        try:
            temp_file = self.archive_file + ".tmp"
            if self.archive_type == 'zip':
                with zipfile.ZipFile(self.archive_file, 'r') as old_archive:
                    with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as new_archive:
                        for item in old_archive.infolist():
                            if item.filename not in files_to_remove:
                                new_archive.writestr(item, old_archive.read(item.filename))
            elif self.archive_type == 'rar':
                with rarfile.RarFile(self.archive_file, 'r') as old_archive:
                    with rarfile.RarFile(temp_file, 'w', compression=rarfile.RAR_M5) as new_archive:
                        for item in old_archive.infolist():
                            if item.filename not in files_to_remove:
                                new_archive.writestr(item, old_archive.read(item.filename))
            os.remove(self.archive_file)
            os.rename(temp_file, self.archive_file)
            self.refresh_archive()
            self.show_message("Success", f"Removed {len(files_to_remove)} file(s)")
            self.update_presence("Removing Files", os.path.basename(self.archive_file))
        except Exception as e:
            self.show_message("Error", f"Failed to remove files: {str(e)}", QMessageBox.Critical)

    def compress_archive(self):
        if not self.archive_file:
            self.show_message("Error", "No archive loaded", QMessageBox.Warning)
            return
        
        try:
            temp_file = self.archive_file + ".tmp"
            if self.archive_type == 'zip':
                with zipfile.ZipFile(self.archive_file, 'r') as old_archive:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setMaximum(len(old_archive.infolist()))
                    with zipfile.ZipFile(temp_file, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as new_archive:
                        for i, item in enumerate(old_archive.infolist()):
                            new_archive.writestr(item, old_archive.read(item.filename))
                            self.progress_bar.setValue(i + 1)
            elif self.archive_type == 'rar':
                with rarfile.RarFile(self.archive_file, 'r') as old_archive:
                    self.progress_bar.setVisible(True)
                    self.progress_bar.setMaximum(len(old_archive.infolist()))
                    with rarfile.RarFile(temp_file, 'w', compression=rarfile.RAR_M5) as new_archive:
                        for i, item in enumerate(old_archive.infolist()):
                            new_archive.writestr(item, old_archive.read(item.filename))
                            self.progress_bar.setValue(i + 1)
            os.remove(self.archive_file)
            os.rename(temp_file, self.archive_file)
            self.refresh_archive()
            self.show_message("Success", "Archive compressed to maximum level")
            self.update_presence("Compressing Archive", os.path.basename(self.archive_file))
        except Exception as e:
            self.show_message("Error", f"Failed to compress archive: {str(e)}", QMessageBox.Critical)
        finally:
            self.progress_bar.setVisible(False)

    def decompress_archive(self):
        if not self.archive_file:
            self.show_message("Error", "No archive loaded", QMessageBox.Warning)
            return
        
        folder = QFileDialog.getExistingDirectory(self, "Select Decompression Folder")
        if folder:
            try:
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(self.archive_file, 'r') as archive:
                        archive.extractall(folder)
                elif self.archive_type == 'rar':
                    with rarfile.RarFile(self.archive_file, 'r') as archive:
                        archive.extractall(folder)
                self.show_message("Success", f"Decompressed all files to {folder}")
                self.update_presence("Decompressing Archive", os.path.basename(self.archive_file))
            except Exception as e:
                self.show_message("Error", f"Failed to decompress archive: {str(e)}", QMessageBox.Critical)

    def handle_double_click(self, index):
        if not self.archive_file:
            print("No archive loaded")
            return
        
        row = index.row()
        item = self.file_table.item(row, 0)
        if not item:
            print("No item at row", row)
            return
            
        name = item.text()
        full_path = os.path.join(self.current_path, name).replace('\\', '/')
        print(f"Double-clicked: {full_path}")
        
        try:
            if self.archive_type == 'zip':
                archive_class = zipfile.ZipFile
            elif self.archive_type == 'rar':
                archive_class = rarfile.RarFile
            else:
                return

            with archive_class(self.archive_file, 'r') as archive:
                namelist = archive.namelist()
                print(f"Archive namelist: {namelist}")
                
                is_folder = (full_path + '/' in namelist or 
                           any(f.startswith(full_path + '/') for f in namelist))
                print(f"Is folder: {is_folder}")
                
                if is_folder:
                    print(f"Navigating to folder: {full_path}")
                    self.path_history.append(self.current_path)
                    self.current_path = full_path
                    self.refresh_archive()
                    self.toolbar_buttons["Go Back"].setEnabled(True)
                    self.header.setText(f"zipaura - Archive Manager - /{self.current_path}")
                    self.update_presence("Browsing Folder", f"{os.path.basename(self.archive_file)} - {self.current_path}")
                else:
                    if full_path in namelist:
                        print(f"Attempting to view file: {full_path}")
                        try:
                            content = archive.read(full_path).decode('utf-8', errors='replace')
                            viewer = ContentViewer(name, content)
                            viewer.show()
                            self.content_viewers.append(viewer)
                            print(f"Opened viewer for: {name}")
                            self.update_presence("Viewing File", name)
                        except UnicodeDecodeError:
                            self.show_message("Warning", "Cannot display binary file contents", QMessageBox.Warning)
                            print("File is binary")
                    else:
                        print(f"Path not found in archive: {full_path}")
                        self.show_message("Error", f"Item not found in archive: {name}", QMessageBox.Warning)
        except Exception as e:
            self.show_message("Error", f"Failed to process item: {str(e)}", QMessageBox.Critical)
            print(f"Error: {str(e)}")

    def go_back(self):
        if self.path_history:
            self.current_path = self.path_history.pop()
            self.refresh_archive()
            self.toolbar_buttons["Go Back"].setEnabled(bool(self.path_history))
            self.header.setText(f"zipaura - Archive Manager - /{self.current_path}" 
                              if self.current_path else "zipaura - Archive Manager")
            self.update_presence("Browsing Folder", f"{os.path.basename(self.archive_file)} - {self.current_path or 'root'}")

    def refresh_archive(self):
        self.file_table.setRowCount(0)
        if not self.archive_file or not os.path.exists(self.archive_file):
            self.update_status("No archive loaded")
            self.update_presence("Idle", "No archive loaded")
            return

        try:
            if self.archive_type == 'zip':
                archive_class = zipfile.ZipFile
            elif self.archive_type == 'rar':
                archive_class = rarfile.RarFile
            else:
                self.update_status("No archive loaded")
                return

            with archive_class(self.archive_file, 'r') as archive:
                file_list = archive.namelist()
                print(f"Raw archive contents: {file_list}")
                if not file_list:
                    self.update_status("Empty archive")
                    self.update_presence("Browsing Archive", "Empty archive")
                    return

                items = {}
                for info in archive.infolist():
                    filename = info.filename.rstrip('/')
                    print(f"Processing: {filename}")
                    normalized_current = self.current_path.replace('\\', '/')
                    if normalized_current:
                        if not filename.startswith(normalized_current + '/'):
                            continue
                        relative_name = filename[len(normalized_current) + 1:]
                    else:
                        relative_name = filename

                    if not relative_name:
                        continue

                    if '/' in relative_name:
                        folder_name = relative_name.split('/')[0]
                        if folder_name and folder_name not in items:
                            items[folder_name] = None
                            print(f"Added folder: {folder_name}")
                    else:
                        items[relative_name] = info
                        print(f"Added file: {relative_name}")

                print(f"Items to display: {items}")
                if not items:
                    self.update_status(f"Empty directory: /{self.current_path}" if self.current_path else "Empty archive root")
                    self.update_presence("Browsing Archive", "Empty directory")
                    return

                for name, info in sorted(items.items()):
                    row = self.file_table.rowCount()
                    self.file_table.insertRow(row)
                    self.file_table.setItem(row, 0, QTableWidgetItem(name))
                    
                    if info is None:  # Folder
                        self.file_table.setItem(row, 1, QTableWidgetItem("Folder"))
                        self.file_table.setItem(row, 2, QTableWidgetItem(""))
                        self.file_table.setItem(row, 3, QTableWidgetItem(""))
                        self.file_table.setItem(row, 4, QTableWidgetItem(""))
                    else:  # File
                        orig_size = info.file_size / 1024
                        comp_size = (info.compress_size / 1024 if self.archive_type == 'zip' else info.file_size / 1024)
                        ratio = (1 - comp_size / orig_size) * 100 if orig_size > 0 else 0
                        date = datetime(*info.date_time[:6]).strftime("%Y-%m-%d %H:%M:%S")
                        
                        self.file_table.setItem(row, 1, QTableWidgetItem(f"{orig_size:.2f} KB"))
                        self.file_table.setItem(row, 2, QTableWidgetItem(f"{comp_size:.2f} KB"))
                        self.file_table.setItem(row, 3, QTableWidgetItem(f"{ratio:.1f}%"))
                        self.file_table.setItem(row, 4, QTableWidgetItem(date))
                
                self.update_status(f"Showing {len(items)} items at: /{self.current_path}" if self.current_path else f"Showing {len(items)} items at archive root")
                self.update_presence("Browsing Archive", f"{os.path.basename(self.archive_file)} - {self.current_path or 'root'}")
        except (zipfile.BadZipFile, rarfile.BadRarFile):
            self.show_message("Error", "Invalid or corrupted archive file", QMessageBox.Critical)
            self.archive_file = None
            self.update_status("No archive loaded")
            self.update_presence("Idle", "No archive loaded")
        except Exception as e:
            self.show_message("Error", f"Failed to refresh archive: {str(e)}", QMessageBox.Critical)
            self.update_status("Error loading archive")
            self.update_presence("Error", "Failed to load archive")

    def search_files(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.file_table.rowCount()):
            item = self.file_table.item(row, 0)
            self.file_table.setRowHidden(row, search_text not in item.text().lower())

    def closeEvent(self, event):
        for viewer in self.content_viewers:
            viewer.close()
        if self.rpc_connected:
            self.rpc.close()  # Close the Discord RPC connection
            print("Disconnected from Discord RPC")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = zipauraGUI()
    window.show()
    sys.exit(app.exec_())