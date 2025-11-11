import sys
import os
import fitz  # PyMuPDF
import re
import subprocess
from PIL import Image
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QProgressBar,
    QComboBox, QMessageBox, QFrame, QTabWidget, QCheckBox, QGridLayout
)
from PyQt6.QtCore import QThread, QObject, pyqtSignal, QUrl
from PyQt6.QtGui import QIcon

# --- Kelas Worker untuk Proses Konversi File di Latar Belakang ---
class FileConversionWorker(QObject):
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(str)
    conversion_error = pyqtSignal(str)

    def __init__(self, input_path, output_path, mode, out_format, ico_sizes=None):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.mode = mode
        self.out_format = out_format
        self.ico_sizes = ico_sizes if ico_sizes else []
        self.is_running = True

    def run(self):
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

    def _convert_pdf_to_image(self):
        doc = fitz.open(self.input_path)
        total_pages = len(doc)
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]

        for i, page in enumerate(doc):
            if not self.is_running:
                break
            
            pix = page.get_pixmap(dpi=200)
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
        if not self.ico_sizes:
            self.conversion_error.emit("Tidak ada ukuran resolusi ICO yang dipilih.")
            return
            
        img = Image.open(self.input_path)
        self.progress_updated.emit(60, "Menyimpan ke format ICO dengan ukuran yang dipilih...")
        
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = os.path.join(self.output_path, f"{base_name}.ico")
        
        img.save(output_filename, format='ICO', sizes=self.ico_sizes)
        self.progress_updated.emit(100, "Selesai!")
        self.conversion_finished.emit("Sukses! File PNG telah dikonversi ke ICO.")

# --- Kelas Worker untuk Proses Konversi Video di Latar Belakang ---
class VideoConversionWorker(QObject):
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(str)
    conversion_error = pyqtSignal(str)

    def __init__(self, ffmpeg_path, input_path, output_path, out_format, resolution, quality):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.input_path = input_path
        self.output_path = output_path
        self.out_format = out_format
        self.resolution = resolution
        self.quality = quality
        self.is_running = True

    def _get_media_duration(self):
        """Mendapatkan durasi media dalam detik menggunakan ffmpeg."""
        command = [
            self.ffmpeg_path, '-i', self.input_path
        ]
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            result = subprocess.run(command, capture_output=True, text=True, stderr=subprocess.STDOUT, startupinfo=startupinfo)
            output = result.stdout
            duration_search = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", output)
            if duration_search:
                hours = int(duration_search.group(1))
                minutes = int(duration_search.group(2))
                seconds = int(duration_search.group(3))
                return (hours * 3600) + (minutes * 60) + seconds
        except Exception:
            return None
        return None

    def run(self):
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = os.path.join(self.output_path, f"{base_name}.{self.out_format}")

        command = [
            self.ffmpeg_path,
            '-i', self.input_path
        ]
        
        quality_map = {
            "Tinggi": "18",
            "Sedang": "23",
            "Rendah": "28"
        }
        crf_value = quality_map.get(self.quality, "23") 
        command.extend(['-crf', crf_value])

        resolution_map = {
            "360p": "360",
            "480p": "480",
            "720p": "720",
            "1080p": "1080",
            "2K": "1440",
            "4K": "2160"
        }
        if self.resolution in resolution_map:
            height = resolution_map[self.resolution]
            command.extend(['-vf', f'scale=-2:{height}'])

        command.extend(['-y', output_filename])
        
        try:
            self.progress_updated.emit(0, "Mendapatkan info video...")
            total_duration = self._get_media_duration()
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True, 
                encoding='utf-8',
                startupinfo=startupinfo
            )

            for line in iter(process.stdout.readline, ""):
                if not self.is_running:
                    process.terminate()
                    break

                if total_duration:
                    time_search = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
                    if time_search:
                        hours = int(time_search.group(1))
                        minutes = int(time_search.group(2))
                        seconds = int(time_search.group(3))
                        current_time = (hours * 3600) + (minutes * 60) + seconds
                        progress = int((current_time / total_duration) * 100)
                        self.progress_updated.emit(progress, f"Mengonversi... {progress}%")

            process.wait()

            if self.is_running and process.returncode == 0:
                self.conversion_finished.emit(f"Sukses! Video telah dikonversi ke {self.out_format.upper()}.")
            elif self.is_running:
                self.conversion_error.emit(f"Gagal mengonversi {os.path.basename(self.input_path)}. Kode exit: {process.returncode}")

        except Exception as e:
            self.conversion_error.emit(f"Terjadi kesalahan saat menjalankan ffmpeg: {str(e)}")

    def stop(self):
        self.is_running = False

# --- Kelas Worker untuk Proses Konversi Audio di Latar Belakang ---
class AudioConversionWorker(QObject):
    progress_updated = pyqtSignal(int, str)
    conversion_finished = pyqtSignal(str)
    conversion_error = pyqtSignal(str)

    def __init__(self, ffmpeg_path, input_path, output_path, out_format, bitrate):
        super().__init__()
        self.ffmpeg_path = ffmpeg_path
        self.input_path = input_path
        self.output_path = output_path
        self.out_format = out_format
        self.bitrate = bitrate
        self.is_running = True

    def _get_media_duration(self):
        """Mendapatkan durasi media dalam detik menggunakan ffmpeg."""
        command = [
            self.ffmpeg_path, '-i', self.input_path
        ]
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            result = subprocess.run(command, capture_output=True, text=True, stderr=subprocess.STDOUT, startupinfo=startupinfo)
            output = result.stdout
            duration_search = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", output)
            if duration_search:
                hours = int(duration_search.group(1))
                minutes = int(duration_search.group(2))
                seconds = int(duration_search.group(3))
                return (hours * 3600) + (minutes * 60) + seconds
        except Exception:
            return None
        return None

    def run(self):
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        output_filename = os.path.join(self.output_path, f"{base_name}.{self.out_format}")

        command = [
            self.ffmpeg_path,
            '-i', self.input_path,
            '-vn'  # Nonaktifkan video
        ]
        
        bitrate_k = self.bitrate.split(' ')[0] + 'k'
        command.extend(['-b:a', bitrate_k])
        
        command.extend(['-y', output_filename])
        
        try:
            self.progress_updated.emit(0, "Mendapatkan info audio...")
            total_duration = self._get_media_duration()
            
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                universal_newlines=True, 
                encoding='utf-8',
                startupinfo=startupinfo
            )

            for line in iter(process.stdout.readline, ""):
                if not self.is_running:
                    process.terminate()
                    break

                if total_duration:
                    time_search = re.search(r"time=(\d{2}):(\d{2}):(\d{2})\.(\d{2})", line)
                    if time_search:
                        hours = int(time_search.group(1))
                        minutes = int(time_search.group(2))
                        seconds = int(time_search.group(3))
                        current_time = (hours * 3600) + (minutes * 60) + seconds
                        progress = int((current_time / total_duration) * 100)
                        self.progress_updated.emit(progress, f"Mengonversi... {progress}%")

            process.wait()

            if self.is_running and process.returncode == 0:
                self.conversion_finished.emit(f"Sukses! Audio telah dikonversi ke {self.out_format.upper()}.")
            elif self.is_running:
                self.conversion_error.emit(f"Gagal mengonversi {os.path.basename(self.input_path)}. Kode exit: {process.returncode}")

        except Exception as e:
            self.conversion_error.emit(f"Terjadi kesalahan saat menjalankan ffmpeg: {str(e)}")

    def stop(self):
        self.is_running = False

# --- Kelas Utama Aplikasi (UI) ---
class ConverterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Macan Converter Pro")
        self.setGeometry(100, 100, 650, 600)
        icon_path = "icon.ico"
        if hasattr(sys, "_MEIPASS"):
            icon_path = os.path.join(sys._MEIPASS, icon_path)
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.thread = None
        self.worker = None

        # Atribut untuk batch mode video
        self.video_batch_files = []
        self.current_batch_index = 0
        
        # Atribut untuk batch mode audio
        self.audio_batch_files = []
        self.current_audio_batch_index = 0
        
        self._setup_ui()
        self._apply_stylesheet()
        self._update_ui_for_mode(self.mode_combo.currentText())

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        title_label = QLabel("Macan Converter Pro")
        title_label.setObjectName("titleLabel")
        main_layout.addWidget(title_label)

        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)

        file_converter_tab = self._create_file_converter_tab()
        video_converter_tab = self._create_video_converter_tab()
        audio_converter_tab = self._create_audio_converter_tab()
        
        tab_widget.addTab(file_converter_tab, "File Converter")
        tab_widget.addTab(video_converter_tab, "Video Converter")
        tab_widget.addTab(audio_converter_tab, "Audio Converter")

    def _create_file_converter_tab(self):
        """Membuat widget untuk Tab File Converter."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        io_frame = QFrame()
        io_frame.setObjectName("ioFrame")
        io_layout = QVBoxLayout(io_frame)
        io_layout.setSpacing(10)
        
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
        layout.addWidget(io_frame)

        settings_frame = QFrame()
        settings_frame.setObjectName("ioFrame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.addWidget(QLabel("3. Pilih Mode Konversi:"))
        
        settings_grid_layout = QHBoxLayout()
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["PDF ke Gambar", "PNG ke ICO"])
        self.mode_combo.currentTextChanged.connect(self._update_ui_for_mode)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["PNG", "JPG"])
        
        settings_grid_layout.addWidget(QLabel("Mode:"))
        settings_grid_layout.addWidget(self.mode_combo, 1)
        settings_grid_layout.addSpacing(20)
        settings_grid_layout.addWidget(QLabel("Format Output:"))
        settings_grid_layout.addWidget(self.format_combo, 1)
        settings_layout.addLayout(settings_grid_layout)
        
        self.ico_sizes_frame = QFrame()
        self.ico_sizes_frame.setObjectName("icoFrame")
        ico_layout = QVBoxLayout(self.ico_sizes_frame)
        ico_layout.addWidget(QLabel("Pilih Resolusi ICO:"))
        ico_grid = QGridLayout()
        self.ico_checkboxes = {}
        sizes = ["16x16", "32x32", "48x48", "64x64", "128x128", "256x256"]
        positions = [(i, j) for i in range(2) for j in range(3)]
        for position, size in zip(positions, sizes):
            checkbox = QCheckBox(size)
            checkbox.setChecked(True)
            self.ico_checkboxes[size] = checkbox
            ico_grid.addWidget(checkbox, *position)
        ico_layout.addLayout(ico_grid)
        settings_layout.addWidget(self.ico_sizes_frame)

        layout.addWidget(settings_frame)

        self.convert_btn = QPushButton("Mulai Konversi File")
        self.convert_btn.setObjectName("convertButton")
        self.convert_btn.clicked.connect(self.start_file_conversion)
        layout.addWidget(self.convert_btn)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Siap untuk mengonversi.")
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        layout.addStretch()
        return tab_widget

    def _create_video_converter_tab(self):
        """Membuat widget untuk Tab Video Converter."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        video_io_frame = QFrame()
        video_io_frame.setObjectName("ioFrame")
        video_io_layout = QVBoxLayout(video_io_frame)
        
        video_io_layout.addWidget(QLabel("1. Pilih File Video Input:"))
        vid_input_layout = QHBoxLayout()
        self.vid_input_path_edit = QLineEdit()
        self.vid_input_path_edit.setReadOnly(True)
        self.vid_input_path_edit.setPlaceholderText("Pilih satu file video...")
        vid_browse_btn = QPushButton("Browse...")
        vid_browse_btn.clicked.connect(self.browse_video_input_file)
        vid_input_layout.addWidget(self.vid_input_path_edit)
        vid_input_layout.addWidget(vid_browse_btn)
        video_io_layout.addLayout(vid_input_layout)

        video_io_layout.addWidget(QLabel("2. Pilih Folder Output:"))
        vid_output_layout = QHBoxLayout()
        self.vid_output_path_edit = QLineEdit()
        self.vid_output_path_edit.setPlaceholderText("Pilih folder tujuan...")
        self.vid_output_path_edit.setReadOnly(True)
        vid_browse_output_btn = QPushButton("Browse...")
        vid_browse_output_btn.clicked.connect(self.browse_video_output_folder)
        vid_output_layout.addWidget(self.vid_output_path_edit)
        vid_output_layout.addWidget(vid_browse_output_btn)
        video_io_layout.addLayout(vid_output_layout)

        self.batch_mode_checkbox = QCheckBox("Batch Mode (Konversi Banyak File Sekaligus)")
        self.batch_mode_checkbox.stateChanged.connect(self._update_video_input_ui)
        video_io_layout.addWidget(self.batch_mode_checkbox)
        
        layout.addWidget(video_io_frame)

        vid_settings_frame = QFrame()
        vid_settings_frame.setObjectName("ioFrame")
        vid_settings_layout = QVBoxLayout(vid_settings_frame)
        vid_settings_layout.addWidget(QLabel("3. Atur Opsi Konversi Video:"))

        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format Output:"))
        self.vid_format_combo = QComboBox()
        self.vid_format_combo.addItems(["mp4", "mkv", "avi", "mov", "webm", "gif"])
        format_layout.addWidget(self.vid_format_combo, 1)
        vid_settings_layout.addLayout(format_layout)

        res_quality_layout = QHBoxLayout()
        
        res_quality_layout.addWidget(QLabel("Resolusi:"))
        self.vid_resolution_combo = QComboBox()
        self.vid_resolution_combo.addItems([
            "Original Size", "360p", "480p", "720p", "1080p", "2K", "4K"
        ])
        res_quality_layout.addWidget(self.vid_resolution_combo, 1)
        
        res_quality_layout.addSpacing(20)

        res_quality_layout.addWidget(QLabel("Kualitas:"))
        self.vid_quality_combo = QComboBox()
        self.vid_quality_combo.addItems(["Tinggi", "Sedang", "Rendah"])
        self.vid_quality_combo.setCurrentText("Sedang") 
        res_quality_layout.addWidget(self.vid_quality_combo, 1)

        vid_settings_layout.addLayout(res_quality_layout)
        layout.addWidget(vid_settings_frame)

        self.vid_convert_btn = QPushButton("Mulai Konversi Video")
        self.vid_convert_btn.setObjectName("convertButton")
        self.vid_convert_btn.clicked.connect(self.start_video_conversion)
        layout.addWidget(self.vid_convert_btn)

        self.vid_progress_bar = QProgressBar()
        self.vid_progress_bar.setValue(0)
        self.vid_progress_bar.setTextVisible(False)
        layout.addWidget(self.vid_progress_bar)
        
        self.vid_status_label = QLabel("Siap untuk mengonversi video.")
        self.vid_status_label.setObjectName("statusLabel")
        layout.addWidget(self.vid_status_label)

        layout.addStretch()
        return tab_widget

    def _create_audio_converter_tab(self):
        """Membuat widget untuk Tab Audio Converter."""
        tab_widget = QWidget()
        layout = QVBoxLayout(tab_widget)
        layout.setContentsMargins(10, 20, 10, 10)
        layout.setSpacing(15)

        audio_io_frame = QFrame()
        audio_io_frame.setObjectName("ioFrame")
        audio_io_layout = QVBoxLayout(audio_io_frame)
        
        audio_io_layout.addWidget(QLabel("1. Pilih File Audio Input:"))
        audio_input_layout = QHBoxLayout()
        self.audio_input_path_edit = QLineEdit()
        self.audio_input_path_edit.setReadOnly(True)
        self.audio_input_path_edit.setPlaceholderText("Pilih satu file audio...")
        audio_browse_btn = QPushButton("Browse...")
        audio_browse_btn.clicked.connect(self.browse_audio_input_file)
        audio_input_layout.addWidget(self.audio_input_path_edit)
        audio_input_layout.addWidget(audio_browse_btn)
        audio_io_layout.addLayout(audio_input_layout)

        audio_io_layout.addWidget(QLabel("2. Pilih Folder Output:"))
        audio_output_layout = QHBoxLayout()
        self.audio_output_path_edit = QLineEdit()
        self.audio_output_path_edit.setPlaceholderText("Pilih folder tujuan...")
        self.audio_output_path_edit.setReadOnly(True)
        audio_browse_output_btn = QPushButton("Browse...")
        audio_browse_output_btn.clicked.connect(self.browse_audio_output_folder)
        audio_output_layout.addWidget(self.audio_output_path_edit)
        audio_output_layout.addWidget(audio_browse_output_btn)
        audio_io_layout.addLayout(audio_output_layout)

        self.audio_batch_mode_checkbox = QCheckBox("Batch Mode (Konversi Banyak File Sekaligus)")
        self.audio_batch_mode_checkbox.stateChanged.connect(self._update_audio_input_ui)
        audio_io_layout.addWidget(self.audio_batch_mode_checkbox)
        
        layout.addWidget(audio_io_frame)

        audio_settings_frame = QFrame()
        audio_settings_frame.setObjectName("ioFrame")
        audio_settings_layout = QVBoxLayout(audio_settings_frame)
        audio_settings_layout.addWidget(QLabel("3. Atur Opsi Konversi Audio:"))
        settings_hbox = QHBoxLayout()
        
        settings_hbox.addWidget(QLabel("Format Output:"))
        self.audio_format_combo = QComboBox()
        self.audio_format_combo.addItems(["mp3", "wav", "aac", "flac", "ogg", "wma", "m4a"])
        settings_hbox.addWidget(self.audio_format_combo, 1)

        settings_hbox.addSpacing(20)

        settings_hbox.addWidget(QLabel("Bitrate:"))
        self.audio_bitrate_combo = QComboBox()
        self.audio_bitrate_combo.addItems(["96 kbps", "128 kbps", "192 kbps", "256 kbps", "320 kbps"])
        self.audio_bitrate_combo.setCurrentText("192 kbps")
        settings_hbox.addWidget(self.audio_bitrate_combo, 1)

        audio_settings_layout.addLayout(settings_hbox)
        layout.addWidget(audio_settings_frame)

        self.audio_convert_btn = QPushButton("Mulai Konversi Audio")
        self.audio_convert_btn.setObjectName("convertButton")
        self.audio_convert_btn.clicked.connect(self.start_audio_conversion)
        layout.addWidget(self.audio_convert_btn)

        self.audio_progress_bar = QProgressBar()
        self.audio_progress_bar.setValue(0)
        self.audio_progress_bar.setTextVisible(False)
        layout.addWidget(self.audio_progress_bar)
        
        self.audio_status_label = QLabel("Siap untuk mengonversi audio.")
        self.audio_status_label.setObjectName("statusLabel")
        layout.addWidget(self.audio_status_label)

        layout.addStretch()
        return tab_widget

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #2E3440; color: #ECEFF4; font-family: Segoe UI, sans-serif;
            }
            QTabWidget::pane { border-top: 2px solid #434C5E; }
            QTabBar::tab {
                background: #3B4252; color: #D8DEE9; padding: 10px;
                border: 1px solid #434C5E; border-bottom: none; border-top-left-radius: 4px; border-top-right-radius: 4px;
            }
            QTabBar::tab:selected { background: #434C5E; color: #ECEFF4; }
            #titleLabel { font-size: 24pt; font-weight: bold; color: #88C0D0; padding-bottom: 10px; }
            #statusLabel { color: #A3BE8C; }
            QLabel { font-size: 10pt; }
            QCheckBox { font-size: 9pt; padding-top: 5px; }
            QLineEdit {
                background-color: #4C566A; border: 1px solid #5E81AC; border-radius: 4px;
                padding: 6px; color: #D8DEE9;
            }
            QPushButton {
                background-color: #5E81AC; color: #ECEFF4; border: none; padding: 8px 16px;
                border-radius: 4px; font-size: 10pt;
            }
            QPushButton:hover { background-color: #81A1C1; }
            QPushButton:pressed { background-color: #4C566A; }
            #convertButton { background-color: #A3BE8C; font-weight: bold; color: #2E3440; }
            #convertButton:hover { background-color: #B48EAD; }
            QComboBox {
                background-color: #4C566A; border: 1px solid #5E81AC; border-radius: 4px; padding: 6px;
            }
            QComboBox::drop-down { border: none; }
            QProgressBar {
                border: 1px solid #4C566A; border-radius: 4px; text-align: center; height: 10px;
            }
            QProgressBar::chunk { background-color: #88C0D0; border-radius: 4px; }
            #ioFrame, #icoFrame {
                border: 1px solid #434C5E; border-radius: 5px; padding: 10px;
            }
        """)

    # --- Logika untuk File Converter ---
    def browse_input_file(self):
        mode = self.mode_combo.currentText()
        filters = {
            "PDF ke Gambar": "PDF Files (*.pdf)",
            "PNG ke ICO": "PNG Files (*.png)"
        }
        filter = filters.get(mode, "All Files (*)")
        file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Input", "", filter)
        if file_path:
            self.input_path_edit.setText(file_path)

    def browse_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output")
        if folder_path:
            self.output_path_edit.setText(folder_path)

    def _update_ui_for_mode(self, mode):
        is_pdf_mode = mode == "PDF ke Gambar"
        self.format_combo.setVisible(is_pdf_mode)
        self.ico_sizes_frame.setVisible(not is_pdf_mode)
        
        self.input_path_edit.clear()
        self.progress_bar.setValue(0)
        self.status_label.setText("Siap untuk mengonversi.")

    def start_file_conversion(self):
        input_path = self.input_path_edit.text()
        output_path = self.output_path_edit.text()
        mode = self.mode_combo.currentText()
        out_format = self.format_combo.currentText()

        if not input_path or not os.path.exists(input_path):
            QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih file input yang valid.")
            return
        if not output_path or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Output Tidak Valid", "Silakan pilih folder output yang valid.")
            return

        ico_sizes = []
        if mode == "PNG ke ICO":
            for size_str, checkbox in self.ico_checkboxes.items():
                if checkbox.isChecked():
                    w, h = map(int, size_str.split('x'))
                    ico_sizes.append((w, h))
            if not ico_sizes:
                QMessageBox.warning(self, "Input Tidak Valid", "Pilih setidaknya satu ukuran resolusi untuk file ICO.")
                return

        self.convert_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        
        self.thread = QThread()
        self.worker = FileConversionWorker(input_path, output_path, mode, out_format, ico_sizes)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_updated.connect(lambda v, t: self.update_progress(self.progress_bar, self.status_label, v, t))
        self.worker.conversion_finished.connect(self.on_file_conversion_finished)
        self.worker.conversion_error.connect(lambda msg: self.conversion_error(self.convert_btn, self.progress_bar, self.status_label, msg))
        
        self.thread.start()
        
    def on_file_conversion_finished(self, msg):
        self.conversion_finished(self.convert_btn, self.progress_bar, self.status_label, msg)

    # --- Logika untuk Video Converter ---
    def _update_video_input_ui(self):
        """Mengupdate UI input video berdasarkan status batch mode."""
        is_batch = self.batch_mode_checkbox.isChecked()
        if is_batch:
            self.vid_input_path_edit.setPlaceholderText("Pilih beberapa file video untuk konversi batch...")
        else:
            self.vid_input_path_edit.setPlaceholderText("Pilih satu file video...")
        self.vid_input_path_edit.clear()
        self.video_batch_files = []

    def browse_video_input_file(self):
        """Membuka file dialog untuk satu atau banyak file video."""
        is_batch = self.batch_mode_checkbox.isChecked()
        filter = "Video Files (*.mp4 *.mkv *.avi *.mov *.flv *.wmv)"
        
        if is_batch:
            files, _ = QFileDialog.getOpenFileNames(self, "Pilih File-file Video", "", filter)
            if files:
                self.video_batch_files = files
                self.vid_input_path_edit.setText(f"{len(files)} file video dipilih.")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Video", "", filter)
            if file_path:
                self.vid_input_path_edit.setText(file_path)

    def browse_video_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output Video")
        if folder_path:
            self.vid_output_path_edit.setText(folder_path)
            
    def _find_ffmpeg(self):
        """Mencari path ffmpeg, baik di direktori lokal maupun di sistem PATH."""
        local_path = "ffmpeg.exe" if os.name == 'nt' else "ffmpeg"
        if hasattr(sys, "_MEIPASS"): 
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        local_ffmpeg = os.path.join(base_path, local_path)
        if os.path.exists(local_ffmpeg):
            return local_ffmpeg

        from shutil import which
        if which("ffmpeg"):
            return "ffmpeg"
            
        return None

    def start_video_conversion(self):
        """Memulai proses konversi video untuk mode tunggal atau batch."""
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            QMessageBox.critical(self, "FFmpeg Tidak Ditemukan",
                "ffmpeg tidak ditemukan di direktori aplikasi atau di sistem PATH. "
                "Silakan letakkan file 'ffmpeg.exe' (Windows) atau 'ffmpeg' (Mac/Linux) di sebelah aplikasi ini.")
            return

        output_path = self.vid_output_path_edit.text()
        if not output_path or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Output Tidak Valid", "Silakan pilih folder output video yang valid.")
            return

        is_batch = self.batch_mode_checkbox.isChecked()

        if is_batch:
            if not self.video_batch_files:
                QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih setidaknya satu file video untuk mode batch.")
                return
            self.current_batch_index = 0
            self._start_next_batch_video_conversion()
        else:
            input_path = self.vid_input_path_edit.text()
            if not input_path or not os.path.exists(input_path):
                QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih file video input yang valid.")
                return
            self._start_single_video_conversion(input_path)
    
    def _start_single_video_conversion(self, input_path):
        """Helper untuk memulai konversi satu file video."""
        self.vid_convert_btn.setEnabled(False)
        self.vid_progress_bar.setValue(0)
        self.vid_status_label.setText(f"Mempersiapkan konversi untuk {os.path.basename(input_path)}...")

        out_format = self.vid_format_combo.currentText()
        resolution = self.vid_resolution_combo.currentText()
        quality = self.vid_quality_combo.currentText()
        output_path = self.vid_output_path_edit.text()

        self.thread = QThread()
        self.worker = VideoConversionWorker(self.ffmpeg_path, input_path, output_path, out_format, resolution, quality)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_updated.connect(self.on_video_progress_update)
        self.worker.conversion_finished.connect(self.on_video_conversion_finished)
        self.worker.conversion_error.connect(self.on_video_conversion_error)
        
        self.thread.start()
        
    def _start_next_batch_video_conversion(self):
        """Memulai konversi untuk file berikutnya dalam antrian batch."""
        if self.current_batch_index < len(self.video_batch_files):
            input_path = self.video_batch_files[self.current_batch_index]
            self.vid_status_label.setText(
                f"Mengonversi file {self.current_batch_index + 1} dari {len(self.video_batch_files)}: {os.path.basename(input_path)}"
            )
            self._start_single_video_conversion(input_path)
        else:
            final_msg = f"Batch selesai! Semua {len(self.video_batch_files)} video telah berhasil dikonversi."
            self.vid_status_label.setText(final_msg)
            self.vid_convert_btn.setEnabled(True)
            QMessageBox.information(self, "Batch Selesai", final_msg)
            self._open_output_folder(self.vid_output_path_edit.text())


    def on_video_progress_update(self, value, text):
        """Slot untuk menangani update progress dari worker video."""
        is_batch = self.batch_mode_checkbox.isChecked()
        if is_batch and self.video_batch_files:
            current_file_info = f"File {self.current_batch_index + 1}/{len(self.video_batch_files)}"
            self.update_progress(self.vid_progress_bar, self.vid_status_label, value, f"({current_file_info}) {text}")
        else:
            self.update_progress(self.vid_progress_bar, self.vid_status_label, value, text)

    def on_video_conversion_finished(self, msg):
        """Slot yang dipanggil saat konversi video (tunggal atau bagian dari batch) selesai."""
        is_batch = self.batch_mode_checkbox.isChecked()
        if is_batch and self.video_batch_files:
            self.vid_progress_bar.setValue(100)
            self.current_batch_index += 1
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self._start_next_batch_video_conversion()
        else:
            self.conversion_finished(self.vid_convert_btn, self.vid_progress_bar, self.vid_status_label, msg)

    def on_video_conversion_error(self, msg):
        """Slot yang dipanggil saat terjadi error konversi video."""
        is_batch = self.batch_mode_checkbox.isChecked()
        if is_batch and self.video_batch_files:
            error_msg = f"Error pada file {self.current_batch_index + 1}: {msg}\n\nProses batch dihentikan."
            self.conversion_error(self.vid_convert_btn, self.vid_progress_bar, self.vid_status_label, error_msg)
        else:
            self.conversion_error(self.vid_convert_btn, self.vid_progress_bar, self.vid_status_label, msg)

    # --- Logika untuk Audio Converter ---
    def _update_audio_input_ui(self):
        """Mengupdate UI input audio berdasarkan status batch mode."""
        is_batch = self.audio_batch_mode_checkbox.isChecked()
        if is_batch:
            self.audio_input_path_edit.setPlaceholderText("Pilih beberapa file audio untuk konversi batch...")
        else:
            self.audio_input_path_edit.setPlaceholderText("Pilih satu file audio...")
        self.audio_input_path_edit.clear()
        self.audio_batch_files = []

    def browse_audio_input_file(self):
        """Membuka file dialog untuk satu atau banyak file audio."""
        is_batch = self.audio_batch_mode_checkbox.isChecked()
        filter = "Audio Files (*.mp3 *.wav *.aac *.flac *.ogg *.wma *.m4a)"
        
        if is_batch:
            files, _ = QFileDialog.getOpenFileNames(self, "Pilih File-file Audio", "", filter)
            if files:
                self.audio_batch_files = files
                self.audio_input_path_edit.setText(f"{len(files)} file audio dipilih.")
        else:
            file_path, _ = QFileDialog.getOpenFileName(self, "Pilih File Audio", "", filter)
            if file_path:
                self.audio_input_path_edit.setText(file_path)

    def browse_audio_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Pilih Folder Output Audio")
        if folder_path:
            self.audio_output_path_edit.setText(folder_path)

    def start_audio_conversion(self):
        """Memulai proses konversi audio untuk mode tunggal atau batch."""
        self.ffmpeg_path = self._find_ffmpeg()
        if not self.ffmpeg_path:
            QMessageBox.critical(self, "FFmpeg Tidak Ditemukan",
                "ffmpeg tidak ditemukan di direktori aplikasi atau di sistem PATH. "
                "Silakan letakkan file 'ffmpeg.exe' (Windows) atau 'ffmpeg' (Mac/Linux) di sebelah aplikasi ini.")
            return

        output_path = self.audio_output_path_edit.text()
        if not output_path or not os.path.isdir(output_path):
            QMessageBox.warning(self, "Output Tidak Valid", "Silakan pilih folder output audio yang valid.")
            return

        is_batch = self.audio_batch_mode_checkbox.isChecked()

        if is_batch:
            if not self.audio_batch_files:
                QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih setidaknya satu file audio untuk mode batch.")
                return
            self.current_audio_batch_index = 0
            self._start_next_batch_audio_conversion()
        else:
            input_path = self.audio_input_path_edit.text()
            if not input_path or not os.path.exists(input_path):
                QMessageBox.warning(self, "Input Tidak Valid", "Silakan pilih file audio input yang valid.")
                return
            self._start_single_audio_conversion(input_path)

    def _start_single_audio_conversion(self, input_path):
        """Helper untuk memulai konversi satu file audio."""
        self.audio_convert_btn.setEnabled(False)
        self.audio_progress_bar.setValue(0)
        self.audio_status_label.setText(f"Mempersiapkan konversi untuk {os.path.basename(input_path)}...")

        out_format = self.audio_format_combo.currentText()
        bitrate = self.audio_bitrate_combo.currentText()
        output_path = self.audio_output_path_edit.text()

        self.thread = QThread()
        self.worker = AudioConversionWorker(self.ffmpeg_path, input_path, output_path, out_format, bitrate)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_updated.connect(self.on_audio_progress_update)
        self.worker.conversion_finished.connect(self.on_audio_conversion_finished)
        self.worker.conversion_error.connect(self.on_audio_conversion_error)
        
        self.thread.start()

    def _start_next_batch_audio_conversion(self):
        """Memulai konversi untuk file berikutnya dalam antrian batch audio."""
        if self.current_audio_batch_index < len(self.audio_batch_files):
            input_path = self.audio_batch_files[self.current_audio_batch_index]
            self.audio_status_label.setText(
                f"Mengonversi file {self.current_audio_batch_index + 1} dari {len(self.audio_batch_files)}: {os.path.basename(input_path)}"
            )
            self._start_single_audio_conversion(input_path)
        else:
            final_msg = f"Batch selesai! Semua {len(self.audio_batch_files)} audio telah berhasil dikonversi."
            self.audio_status_label.setText(final_msg)
            self.audio_convert_btn.setEnabled(True)
            QMessageBox.information(self, "Batch Selesai", final_msg)
            self._open_output_folder(self.audio_output_path_edit.text())

    def on_audio_progress_update(self, value, text):
        """Slot untuk menangani update progress dari worker audio."""
        is_batch = self.audio_batch_mode_checkbox.isChecked()
        if is_batch and self.audio_batch_files:
            current_file_info = f"File {self.current_audio_batch_index + 1}/{len(self.audio_batch_files)}"
            self.update_progress(self.audio_progress_bar, self.audio_status_label, value, f"({current_file_info}) {text}")
        else:
            self.update_progress(self.audio_progress_bar, self.audio_status_label, value, text)

    def on_audio_conversion_finished(self, msg):
        """Slot yang dipanggil saat konversi audio (tunggal atau bagian dari batch) selesai."""
        is_batch = self.audio_batch_mode_checkbox.isChecked()
        if is_batch and self.audio_batch_files:
            self.audio_progress_bar.setValue(100)
            self.current_audio_batch_index += 1
            if self.thread:
                self.thread.quit()
                self.thread.wait()
            self._start_next_batch_audio_conversion()
        else:
            self.conversion_finished(self.audio_convert_btn, self.audio_progress_bar, self.audio_status_label, msg)

    def on_audio_conversion_error(self, msg):
        """Slot yang dipanggil saat terjadi error konversi audio."""
        is_batch = self.audio_batch_mode_checkbox.isChecked()
        if is_batch and self.audio_batch_files:
            error_msg = f"Error pada file {self.current_audio_batch_index + 1}: {msg}\n\nProses batch dihentikan."
            self.conversion_error(self.audio_convert_btn, self.audio_progress_bar, self.audio_status_label, error_msg)
        else:
            self.conversion_error(self.audio_convert_btn, self.audio_progress_bar, self.audio_status_label, msg)

    # --- Slot Generik untuk Menangani Sinyal dari Worker ---
    def update_progress(self, progress_bar, status_label, value, text):
        progress_bar.setValue(value)
        status_label.setText(text)

    def _open_output_folder(self, path):
        """Membuka folder output di file explorer."""
        if not os.path.isdir(path):
            return
        try:
            os.startfile(path)
        except AttributeError:
            opener = "open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path])

    def conversion_finished(self, button, progress_bar, status_label, message):
        status_label.setText(message)
        progress_bar.setValue(100)
        button.setEnabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        QMessageBox.information(self, "Selesai", message)
        
        output_path = ""
        if button == self.convert_btn:
            output_path = self.output_path_edit.text()
        elif button == self.vid_convert_btn:
            output_path = self.vid_output_path_edit.text()
        elif button == self.audio_convert_btn:
            output_path = self.audio_output_path_edit.text()
        
        self._open_output_folder(output_path)

    def conversion_error(self, button, progress_bar, status_label, message):
        status_label.setText(f"Error: {message}")
        progress_bar.setValue(0)
        button.setEnabled(True)
        if self.thread:
            self.thread.quit()
            self.thread.wait()
        QMessageBox.critical(self, "Error", message)

    def closeEvent(self, event):
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