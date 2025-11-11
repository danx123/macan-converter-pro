import sys
import os
import traceback

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QTabWidget, QComboBox, QLineEdit, QHBoxLayout, QMessageBox, QProgressBar,
    QStatusBar, QGroupBox, QFormLayout
)
from PyQt6.QtGui import QImage, QPainter, QIcon
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QObject, QThread, pyqtSignal, QUrl, QTimer, Qt, QSize

# === Worker Class for Threading ===
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.function(self, *self.args, **self.kwargs)
        except Exception as e:
            self.error.emit(f"{e}\n\nTraceback:\n{traceback.format_exc()}")
        finally:
            self.finished.emit()

# === Main Application Class ===
class MacanConverterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Converter Pro")
        self.setGeometry(100, 100, 650, 500)
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.setup_styles()

        # Main Layout
        main_layout = QVBoxLayout(self)
        
        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_pdf_tab(), "PDF → Image")
        self.tabs.addTab(self.create_html_tab(), "HTML → Image")
        self.tabs.addTab(self.create_ico_tab(), "PNG → ICO")
        main_layout.addWidget(self.tabs)

        # Status Bar and Progress Bar
        self.status_bar = QStatusBar()
        self.progress_bar = QProgressBar()
        self.status_bar.addPermanentWidget(self.progress_bar, 1)
        main_layout.addWidget(self.status_bar)

        self.setLayout(main_layout)
        self.web_view = None # Initialize web_view attribute

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
                font-size: 11pt;
            }
            QTabWidget::pane {
                border-top: 2px solid #4C566A;
            }
            QTabBar::tab {
                background: #3B4252;
                color: #D8DEE9;
                padding: 10px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4C566A;
                color: #ECEFF4;
            }
            QGroupBox {
                background-color: #3B4252;
                border: 1px solid #4C566A;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            QLineEdit, QComboBox {
                background-color: #4C566A;
                border: 1px solid #5E81AC;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #88C0D0;
            }
            QLabel {
                color: #D8DEE9;
            }
            QProgressBar {
                border: 1px solid #4C566A;
                border-radius: 5px;
                text-align: center;
                background-color: #3B4252;
            }
            QProgressBar::chunk {
                background-color: #88C0D0;
                border-radius: 4px;
            }
        """)

    def create_pdf_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        input_group = QGroupBox("Input")
        form_layout = QFormLayout()
        self.pdf_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file(self.pdf_path, "PDF Files (*.pdf)"))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.pdf_path)
        path_layout.addWidget(browse_btn)
        form_layout.addRow(QLabel("PDF File:"), path_layout)
        input_group.setLayout(form_layout)

        options_group = QGroupBox("Options")
        form_layout = QFormLayout()
        self.pdf_format = QComboBox()
        self.pdf_format.addItems(["png", "jpg", "bmp"])
        form_layout.addRow(QLabel("Output Format:"), self.pdf_format)
        options_group.setLayout(form_layout)
        
        output_group = QGroupBox("Output")
        form_layout = QFormLayout()
        self.pdf_output_folder = QLineEdit()
        out_btn = QPushButton("Select Folder...")
        out_btn.clicked.connect(lambda: self.browse_folder(self.pdf_output_folder))
        out_path_layout = QHBoxLayout()
        out_path_layout.addWidget(self.pdf_output_folder)
        out_path_layout.addWidget(out_btn)
        form_layout.addRow(QLabel("Output Folder:"), out_path_layout)
        output_group.setLayout(form_layout)

        self.pdf_convert_btn = QPushButton("Convert PDF to Images")
        self.pdf_convert_btn.clicked.connect(self.start_pdf_conversion)

        layout.addWidget(input_group)
        layout.addWidget(options_group)
        layout.addWidget(output_group)
        layout.addStretch()
        layout.addWidget(self.pdf_convert_btn)
        
        return tab

    def create_html_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        input_group = QGroupBox("Input")
        form_layout = QFormLayout()
        self.html_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file(self.html_path, "HTML Files (*.html *.htm)"))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.html_path)
        path_layout.addWidget(browse_btn)
        form_layout.addRow(QLabel("HTML File:"), path_layout)
        input_group.setLayout(form_layout)
        
        output_group = QGroupBox("Output")
        form_layout = QFormLayout()
        self.html_output_path = QLineEdit()
        out_btn = QPushButton("Save As...")
        out_btn.clicked.connect(lambda: self.browse_save_file(self.html_output_path, "Images (*.png *.jpg)"))
        out_path_layout = QHBoxLayout()
        out_path_layout.addWidget(self.html_output_path)
        out_path_layout.addWidget(out_btn)
        form_layout.addRow(QLabel("Output Image:"), out_path_layout)
        output_group.setLayout(form_layout)
        
        self.html_convert_btn = QPushButton("Convert HTML to Image")
        self.html_convert_btn.clicked.connect(self.start_html_conversion)
        
        layout.addWidget(input_group)
        layout.addWidget(output_group)
        layout.addStretch()
        layout.addWidget(self.html_convert_btn)

        return tab

    def create_ico_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        input_group = QGroupBox("Input")
        form_layout = QFormLayout()
        self.png_path = QLineEdit()
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(lambda: self.browse_file(self.png_path, "PNG Files (*.png)"))
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.png_path)
        path_layout.addWidget(browse_btn)
        form_layout.addRow(QLabel("PNG File:"), path_layout)
        input_group.setLayout(form_layout)
        
        options_group = QGroupBox("Options")
        form_layout = QFormLayout()
        self.ico_size = QComboBox()
        self.ico_size.addItems(["16x16", "24x24", "32x32", "48x48", "64x64", "128x128", "256x256"])
        self.ico_size.setCurrentText("32x32")
        form_layout.addRow(QLabel("Icon Size:"), self.ico_size)
        options_group.setLayout(form_layout)

        output_group = QGroupBox("Output")
        form_layout = QFormLayout()
        self.ico_output_path = QLineEdit()
        out_btn = QPushButton("Save As...")
        out_btn.clicked.connect(lambda: self.browse_save_file(self.ico_output_path, "ICO Files (*.ico)"))
        out_path_layout = QHBoxLayout()
        out_path_layout.addWidget(self.ico_output_path)
        out_path_layout.addWidget(out_btn)
        form_layout.addRow(QLabel("Output Icon:"), out_path_layout)
        output_group.setLayout(form_layout)
        
        self.ico_convert_btn = QPushButton("Convert PNG to ICO")
        self.ico_convert_btn.clicked.connect(self.start_ico_conversion)

        layout.addWidget(input_group)
        layout.addWidget(options_group)
        layout.addWidget(output_group)
        layout.addStretch()
        layout.addWidget(self.ico_convert_btn)
        
        return tab

    def browse_file(self, line_edit, file_filter):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", file_filter)
        if file:
            line_edit.setText(file)

    def browse_folder(self, line_edit):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            line_edit.setText(folder)

    def browse_save_file(self, line_edit, file_filter):
        file, _ = QFileDialog.getSaveFileName(self, "Save As", "", file_filter)
        if file:
            line_edit.setText(file)
            
    def run_in_thread(self, target_function, *args):
        self.thread = QThread()
        self.worker = Worker(target_function, *args)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.progress.connect(self.update_progress)
        self.worker.error.connect(self.show_error)
        self.worker.finished.connect(self.on_conversion_finished)

        self.thread.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_conversion_finished(self):
        self.status_bar.showMessage("Conversion successful!", 5000)
        self.progress_bar.setValue(100)
        QMessageBox.information(self, "Success", "Conversion completed successfully!")
        self.set_buttons_enabled(True)
        
    def show_error(self, message):
        self.status_bar.showMessage(f"Error: Conversion failed.", 5000)
        QMessageBox.critical(self, "Error", f"An error occurred:\n{message}")
        self.set_buttons_enabled(True) # Make sure buttons are always re-enabled on error
        self.progress_bar.setValue(0)

    def set_buttons_enabled(self, enabled):
        self.pdf_convert_btn.setEnabled(enabled)
        self.html_convert_btn.setEnabled(enabled)
        self.ico_convert_btn.setEnabled(enabled)

    def start_pdf_conversion(self):
        pdf_file = self.pdf_path.text()
        out_dir = self.pdf_output_folder.text()
        if not pdf_file or not out_dir:
            QMessageBox.warning(self, "Input Missing", "Please select a PDF file and an output folder.")
            return
        
        self.set_buttons_enabled(False)
        self.status_bar.showMessage("Converting PDF...")
        self.progress_bar.setValue(0)
        self.run_in_thread(self.convert_pdf_task, pdf_file, out_dir, self.pdf_format.currentText())

    def start_html_conversion(self):
        html_file = self.html_path.text()
        out_file = self.html_output_path.text()
        if not html_file or not out_file:
            QMessageBox.warning(self, "Input Missing", "Please select an HTML file and an output path.")
            return

        self.set_buttons_enabled(False)
        self.status_bar.showMessage("Converting HTML...")
        self.progress_bar.setRange(0, 0) # Indeterminate progress
        
        # Start the conversion process
        self.convert_html_task(html_file, out_file)
        
    def start_ico_conversion(self):
        png_file = self.png_path.text()
        out_file = self.ico_output_path.text()
        if not png_file or not out_file:
            QMessageBox.warning(self, "Input Missing", "Please select a PNG file and an output path.")
            return
        
        size_str = self.ico_size.currentText().split('x')[0]
        size = int(size_str)
        
        self.set_buttons_enabled(False)
        self.status_bar.showMessage("Converting to ICO...")
        self.progress_bar.setValue(0)
        self.run_in_thread(self.convert_ico_task, png_file, out_file, size)

    # --- Conversion Logic ---
    def convert_pdf_task(self, worker_ref, pdf_path, out_dir, fmt):
        doc = QPdfDocument(worker_ref)
        doc.load(pdf_path)
        
        page_count = doc.pageCount()
        if page_count == 0:
            raise Exception("Failed to load PDF or the PDF has no pages.")

        for i in range(page_count):
            dpi = 150
            page_size_points = doc.pageSizeF(i)
            target_size = (page_size_points * (dpi / 72.0)).toSize()
            
            image = doc.render(i, target_size)
            
            out_path = os.path.join(out_dir, f"page_{i+1}.{fmt}")
            if not image.save(out_path):
                raise Exception(f"Failed to save page {i+1} to {out_path}")
                
            progress_val = int(((i + 1) / page_count) * 100)
            worker_ref.progress.emit(progress_val)
    
    def convert_html_task(self, html_path, output_path):
        if self.web_view is not None:
             self.web_view.deleteLater()

        self.web_view = QWebEngineView()
        self.web_view.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen)
        self.web_view.show()

        # Store the output path in a temporary attribute
        self.html_output_path_temp = output_path
        
        # Connect the loadFinished signal
        self.web_view.loadFinished.connect(self.on_html_load_finished)
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath(html_path)))
    
    def on_html_load_finished(self, success):
        if success:
            # Give the page a moment to render any JavaScript
            QTimer.singleShot(500, self.capture_html_page)
        else:
            # FIX 1: Properly handle the failure case
            self.progress_bar.setRange(0, 100) # Reset progress bar
            self.show_error("Failed to load the HTML file.")
            if self.web_view:
                self.web_view.deleteLater()
                self.web_view = None

    def capture_html_page(self):
        # Ensure web_view still exists
        if not self.web_view:
            return

        try:
            pixmap = self.web_view.grab()
            if not pixmap.save(self.html_output_path_temp):
                 # FIX 2: Call the robust error handler
                 self.show_error("Failed to save the captured image.")
            else:
                 # FIX 3: Proper success handling
                 self.status_bar.showMessage("HTML Conversion successful!", 5000)
                 self.progress_bar.setRange(0, 100)
                 self.progress_bar.setValue(100)
                 QMessageBox.information(self, "Success", "Conversion completed successfully!")
                 self.set_buttons_enabled(True)
        except Exception as e:
            self.show_error(f"An unexpected error occurred during capture: {e}")
        finally:
            # FIX 4: Always clean up the web view
            if self.web_view:
                self.web_view.deleteLater()
                self.web_view = None
    
    def convert_ico_task(self, worker_ref, png_path, ico_path, size):
        worker_ref.progress.emit(10)
        image = QImage(png_path)
        if image.isNull():
            raise Exception("Failed to load PNG file.")
            
        worker_ref.progress.emit(50)
        icon_image = image.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        worker_ref.progress.emit(80)
        if not icon_image.save(ico_path):
             raise Exception("Failed to save ICO file. Check path and permissions.")


if __name__ == "__main__":
    # This attribute is important for QWebEngineView to work correctly
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)
    app = QApplication(sys.argv)
    window = MacanConverterApp()
    window.show()
    sys.exit(app.exec())