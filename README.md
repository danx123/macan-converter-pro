# ♻️ Macan Converter Pro

Macan Converter Pro is a multi-conversion application for files, images, audio, and video.
Fast, modern, and easy to use.

Macan Converter Pro is a versatile PySide6-based converter application that supports a wide range of file formats:
- File Converter: PDF → Image (PNG/JPG), PNG → ICO with a choice of resolutions.

- Image Converter: Convert images between formats (JPEG, PNG, WEBP, BMP, GIF), with resolution and quality settings.
- Video Converter: Convert videos to various formats (MP4, MKV, AVI, MOV, WEBM, GIF) with support for resolutions up to 4K and quality.
- Video - Audio Converter
- Audio Converter: Convert audio to MP3, WAV, AAC, FLAC, OGG, WMA, and M4A with a choice of bitrates.

This application uses PyMuPDF, Pillow, and FFmpeg, with batch mode support to speed up the process.

---

## ✨ Key Features
- Modern interface based on PySide6.
- Fast conversion with a real-time progress bar.
- Multi-format conversion support (file, image, video, audio).
- Batch mode for converting multiple files at once.
- Quality and resolution optimization according to user needs.

---

## 📸 Screenshot
<img width="830" height="667" alt="Screenshot 2025-11-09 170847" src="https://github.com/user-attachments/assets/60e2f3c0-e14c-4b2f-97d4-4b9591274b7b" />



---
## 📜 Changelog v4.0.0
This release introduces a major user experience overhaul, focusing on a more intuitive and modern file-handling workflow.

🚀 Added
Drag-and-Drop File Input: Implemented a new interactive FileDropArea widget for the Video, Audio, Image, and Extract Audio tabs.
Asynchronous Thumbnail Generation: Files dropped into the new area will now display thumbnails. A ThumbnailWorker running on a QThreadPool generates these in the background to prevent UI freezing.
Uses opencv-python for video frame extraction.
Uses QPixmap for image previews.
Displays default file-type icons for audio.
New File Management Buttons: Added "Add Files" and "Clear List" buttons to complement the new drag-and-drop functionality.
🔄 Changed
UI Overhaul: Fundamentally redesigned the layout for the Video, Audio, Image, and Extract Audio tabs to accommodate the new file list.
Unified Workflow: Refactored the conversion logic for media tabs to be "batch-by-default." All files in the list are processed as a batch, whether there is one file or one hundred.
❌ Removed
"Batch Mode" Checkbox: This option has been removed as the new drag-and-drop interface is inherently a batch-processing system, simplifying the UI.
Static Input Fields: Removed the QLineEdit fields for single-file inputs on media tabs.
🛠️ Fixed
Worker Thread Memory Leak: Corrected a potential memory leak by ensuring all QObject workers (e.g., VideoConversionWorker) are properly deleted using deleteLater() after their thread has finished.
📦 Dependencies
Added opencv-python as a new dependency for video thumbnail generation.
Added numpy as a dependency for opencv-python.
---

## ⚙️ Installation
1. Ensure Python 3.10+ is installed.
2. Install dependencies:


📦 Important Note
The source code shared in this repository is a framework/base project that serves as the foundation for the application.
For the full version with the latest features, please check the Releases section—ready-to-use binaries are available there.

📖 License
This project is released under the MIT license — free to use, modify, and distribute with proper credit.
