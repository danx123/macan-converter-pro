import sys
import os
import fitz  # PyMuPDF
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
    QComboBox, QMessageBox, QFrame
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWebEngineWidgets import QWebEngineView

# --- Kelas Worker untuk Proses Konversi di Latar Belakang ---
# Ini penting agar aplikasi tidak "Not Responding" saat konversi berjalan
class ConversionWorker(QObject):
    # Sinyal untuk komunikasi dari thread worker ke thread utama (UI)
    progress_updated = pyqtSignal(int, str)  # (persentase, teks status)
    conversion_finished = pyqtSignal(str)   # (pesan sukses)
    conversion_error = pyqtSignal(str)      # (pesan error)

    def __init__(self, input_path, output_path, mode, out_format):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.mode = mode
        self.out_format = out_format
        self.is_running = True

    def run(self):
        """Fungsi utama yang menjalankan logika konversi."""
        try:
            if self.mode == "PDF ke Gambar":
                self._convert_pdf_to_image()
            elif self.mode == "PNG ke ICO":
                self._convert_png_to_ico()
            else:
                self.conversion_error.emit(f"Mode konversi tidak dikenal: {self.mode}")
        except Exception as e:
            self.conversion_error.emit(f"Terjadi kesalahan: {str(e)}")

    def stop(self):
        self.is_running = False

    # --- Logika Konversi ---
    def _convert_pdf_to_image(self):
        doc = fitz.open(self.input_path)
        total_pages = len(doc)
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]

        for i, page in enumerate(doc):
            if not self.is_running:
                break
            
            pix = page.get_pixmap(dpi=200) # Resolusi gambar bisa diubah
            output_filename = os.path.join(self.output_path, f"{base_name}_page_{i+1}.{self.out_format.lower()}")
            pix.save(output_filename)
            
            progress = int(((i + 1) / total_pages) * 100)
            status_text = f"Mengonversi halaman {i+1} dari {total_pages}..."
            self.progress_updated.emit(progress, status_text)
            
        doc.close()
        if self.is_running:
            self.conversion_finished.emit(f"Sukses! {total_pages} halaman PDF telah dikonversi.")

    def _convert_png_to_ico(self):
        self.progress_updated.emit(20, "Membuka file PNG...")
        img = Image.open(self.input_path)
        self.progress_updated.emit(60, "Menyimpan ke format ICO...")
        
        # Opsi ukuran untuk file .ico, bisa ditambah sesuai kebutuhan
        icon_sizes = [(128,128), (256,256)]
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = os.path.join(self.output_path, f"{base_name}.ico")
        
        img.save(output_filename, format='ICO', sizes=icon_sizes)
        self.progress_updated.emit(100, "Selesai!")
        self.conversion_finished.emit("Sukses! File PNG telah dikonversi ke ICO.")

# --- Kelas Utama Aplikasi (UI) ---
class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Converter Pro")
        self.setGeometry(100, 100, 600, 450)
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # Inisialisasi thread
        self.thread = None
        self.worker = None

        self._setup_ui()
        self._apply_stylesheet()
    
    def _setup_ui(self):
        """Membuat dan menata semua widget di jendela aplikasi."""
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Layout utama
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Judul
        title_label = QLabel("File Converter")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        # Frame untuk input dan output
        io_frame = QFrame()
        io_frame.setObjectName("ioFrame")
        io_layout = QVBoxLayout(io_frame)
        io_layout.setSpacing(10)
        
        # Widget Input File
        io_layout.addWidget(QLabel("1. Pilih File Input:"))
        input_layout = QHBoxLayout()
        self.input_path_edit = QLineEdit()
        self.input_path_edit.setPlaceholderText("Pilih file yang akan dikonversi...")
        self.input_path_edit.setReadOnly(True)
        browse_input_btn = QPushButton("Browse...")
        browse_input_btn.clicked.connect(self.browse_input_file)
        input_layout.addWidget(self.input_path_edit)
        input_layout.addWidget(browse_input_btn)
        io_layout.addLayout(input_layout)

        # Widget Output Folder
        io_layout.addWidget(QLabel("2. Pilih Folder Output:"))
        output_layout = QHBoxLayout()
        self.output_path_edit = QLineEdit()
        self.output_path_edit.setPlaceholderText("Pilih folder untuk menyimpan hasil...")
        self.output_path_edit.setReadOnly(True)
        browse_output_btn = QPushButton("Browse...")
        browse_output_btn.clicked.connect(self.browse_output_folder)
        output_layout.addWidget(self.output_path_edit)
        output_layout.addWidget(browse_output_btn)
        io_layout.addLayout(output_layout)

        main_layout.addWidget(io_frame)
        
        # Pengaturan Konversi
        settings_frame = QFrame()
        settings_frame.setObjectName("ioFrame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.addWidget(QLabel("3. Pilih Mode Konversi:"))
        
        settings_grid_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["PDF ke Gambar", "HTML ke Gambar", "PNG ke ICO"])
        self.mode_combo.currentTextChanged.connect(self._update_ui_for_mode)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG"])
        
        settings_grid_layout.addWidget(QLabel("Mode:"))
        settings_grid_layout.addWidget(self.mode_combo)
        settings_grid_layout.addSpacing(20)
        settings_grid_layout.addWidget(QLabel("Format Output:"))
        settings_grid_layout.addWidget(self.format_combo)
        settings_grid_layout.addStretch()
        
        settings_layout.addLayout(settings_grid_layout)
        main_layout.addWidget(settings_frame)

        # Tombol Konversi
        self.convert_btn = QPushButton("Mulai Konversi")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.clicked.connect(self.start_conversion)
        main_layout.addWidget(self.convert_btn)

        # Progress Bar dan Status
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Siap untuk mengonversi.")
        self.status_label.setObjectName("statusLabel")
        main_layout.addWidget(self.status_label)

        main_layout.addStretch() # Mendorong semua widget ke atas

    def _apply_stylesheet(self):
        """Menerapkan styling (QSS) untuk tampilan yang estetik."""
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E3440;
                color: #ECEFF4;
                font-family: Segoe UI, sans-serif;
            }
            #titleLabel {
                font-size: 24pt;
                font-weight: bold;
                color: #88C0D0;
                padding-bottom: 10px;
            }
            #statusLabel {
                color: #A3BE8C;
            }
            QLabel {
                font-size: 10pt;
            }
            QLineEdit {
                background-color: #4C566A;
                border: 1px solid #5E81AC;
                border-radius: 4px;
                padding: 6px;
                color: #D8DEE9;
            }
            QPushButton {
                background-color: #5E81AC;
                color: #ECEFF4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #81A1C1;
            }
            QPushButton:pressed {
                background-color: #4C566A;
            }
            #convertButton {
                background-color: #A3BE8C;
                font-weight: bold;
                color: #2E3440;
            }
            #convertButton:hover {
                background-color: #B48EAD;
            }
            QComboBox {
                background-color: #4C566A;
                border: 1px solid #5E81AC;
                border-radius: 4px;
                padding: 6px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png); /* Anda bisa membuat icon panah kecil */
            }
            QProgressBar {
                border: 1px solid #4C566A;
                border-radius: 4px;
                text-align: center;
                height: 10px;
            }
            QProgressBar::chunk {
                background-color: #88C0D0;
                border-radius: 4px;
            }
            #ioFrame {
                border: 1px solid #434C5E;
                border-radius: 5px;
                padding: 10px;
            }
        """)

    def browse_input_file(self):
        mode = self.mode_combo.currentText()
        if mode == "PDF ke Gambar":
            filter = "PDF Files (*.pdf)"
        elif mode == "HTML ke Gambar":
            filter = "HTML Files (*.html *.htm)"
        elif mode == "PNG ke ICO":
            filter = "PNG Files (*.png)"
        else:
            filter = "All Files (*)"
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Input", "", filter)
        if file_path:
            self.input_path_edit.setText(file_path)

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if folder_path:
            self.output_path_edit.setText(folder_path)

    def _update_ui_for_mode(self, mode):
        """Menyesuaikan UI berdasarkan mode konversi yang dipilih."""
        if mode in ["PDF ke Gambar", "HTML ke Gambar"]:
            self.format_combo.setEnabled(True)
        else: # PNG ke ICO
            self.format_combo.setEnabled(False)
            
        # Mengosongkan pilihan file jika mode berubah
        self.input_path_edit.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Siap untuk mengonversi.")

    def start_conversion(self):
        """Memulai proses konversi setelah validasi input."""
        input_path = self.input_path_edit.text()
        output_path = self.output_path_edit.text()
        mode = self.mode_combo.currentText()
        out_format = self.format_combo.currentText()

        # Validasi
        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih file input yang valid.")
            return
        if not output_path or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Output Tidak Valid", "Silakan pilih folder output yang valid.")
            return

        # Disable tombol agar tidak diklik dua kali
        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)

        # Logika khusus untuk HTML karena butuh QtWebEngine
        if mode == "HTML ke Gambar":
            self._convert_html_to_image(input_path, output_path, out_format)
            return

        # Setup worker dan thread untuk proses lain
        self.thread = QThread()
        self.worker = ConversionWorker(input_path, output_path, mode, out_format)
        self.worker.moveToThread(self.thread)

        # Hubungkan sinyal dari worker ke slot di UI
        self.thread.started.connect(self.worker.run)
        self.worker.progress_updated.connect(self.update_progress)
        self.worker.conversion_finished.connect(self.conversion_finished)
        self.worker.conversion_error.connect(self.conversion_error)
        
        # Mulai thread
        self.thread.start()

    def _convert_html_to_image(self, input_path, output_path, out_format):
        """Fungsi khusus untuk merender HTML."""
        self.status_label.setText("Membuka renderer HTML...")
        self.web_view = QWebEngineView()
        # Set ukuran render yang besar untuk kualitas yang baik
        self.web_view.resize(1920, 1080) 
        self.web_view.load(QUrl.fromLocalFile(os.path.abspath(input_path)))
        
        # Gunakan QTimer untuk memberi waktu halaman render sebelum diambil gambarnya
        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        self.render_timer.timeout.connect(lambda: self._capture_html(output_path, out_format))
        
        # Tunggu 5 detik (bisa disesuaikan)
        self.web_view.loadFinished.connect(lambda ok: self.render_timer.start(5000)) 
        self.progress_bar.setRange(0, 0) # Mode Indeterminate (bergerak terus)

    def _capture_html(self, output_path, out_format):
        self.status_label.setText("Mengambil gambar halaman...")
        pixmap = self.web_view.grab()
        base_name = os.path.splitext(os.path.basename(self.input_path_edit.text()))[0]
        output_filename = os.path.join(output_path, f"{base_name}.{out_format.lower()}")
        pixmap.save(output_filename)
        self.web_view.deleteLater() # Hapus view setelah selesai
        self.conversion_finished(f"Sukses! File HTML telah dikonversi ke {output_filename}")


    # --- Slot untuk menangani sinyal dari worker ---
    def update_progress(self, value, text):
        self.progress_bar.setValue(value)
        self.status_label.setText(text)

    def conversion_finished(self, message):
        self.status_label.setText(message)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)
        self.convert_btn.setEnabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        QMessageBox.information(self, "Selesai", message)
        
        # Buka folder output setelah selesai
        try:
            os.startfile(self.output_path_edit.text())
        except AttributeError:
            # Untuk macOS dan Linux
            import subprocess
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, self.output_path_edit.text()])


    def conversion_error(self, message):
        self.status_label.setText(f"Error: {message}")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.convert_btn.setEnabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
        """Memastikan thread berhenti saat aplikasi ditutup."""
        if self.thread and self.thread.isRunning():
            self.worker.stop()
            self.thread.quit()
            self.thread.wait()
        event.accept()

# --- Entry Point Aplikasi ---
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ConverterApp()
    window.show()
    sys.exit(app.exec())